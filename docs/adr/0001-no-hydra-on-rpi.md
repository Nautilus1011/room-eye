---
作成日: 2026-07-27
最終更新: 2026-07-27
ステータス: 採用
---

# ADR-0001: ラズパイ実行系の設定管理に Hydra を採用しない

## 背景

`experiment/pan_tilt_camera_check/` のスクリプトは、それぞれが `yaml.safe_load()` で設定ファイルを
直接読んでいる。`config/servo_camera_check.yaml` と `config/pan_tilt_explore.yaml` で `servo:` ブロックが
ほぼ完全に重複しており、設定の合成・共通化の仕組みが必要になっている。

その解決手段として Hydra（`hydra-core`）の導入を検討した。Hydra は設定のグループ合成、CLI からの上書き、
multirun によるスイープ、実行ごとの出力ディレクトリ生成を提供する。

一方で room-eye には「**Python で検証し、C/C++ で運用する**」という前提がある（`roadmap.md`）。
この前提のもとで Hydra の費用対効果を評価した。

## 決定

**ラズパイ実行系（`src/room_eye/` および `experiment/` 配下の実機スクリプト）に Hydra を採用しない。**

代わりに以下の構成を採る。

- 設定スキーマは `dataclass`（`frozen=True`）で型付き定義する
- 設定ファイルは**素のフラットな YAML**とし、`PyYAML` で読む
- 複数ファイルの合成が必要な場合は、辞書の deep merge を自前で実装する
  （`config/hardware.yaml` などの共通定義 + 実験固有ファイルの 2 段重ね）
- CLI からの上書きが必要になったら、まず `argparse` で対応する

なお、**GPU 側の学習・評価実験（`requirements-dev.txt` 側）での Hydra 採用は、この ADR の対象外**とする。
conf_thres やモデル変種のスイープを行う段階になったら、そちらに限定して別途検討する。

## 理由

### 1. C++ に等価物がない（最大の理由）

C++ 側の YAML パーサ（yaml-cpp）は、Hydra の `defaults:` によるグループ合成も `${...}` の変数補間も
`_target_` によるインスタンス化も解釈しない。Hydra 前提で書いた設定ファイルは、C++ 移植時に
**作り直しになる**。

Python フェーズの成果物は Python コードではなく検証済みのパラメータ値である以上、
設定ファイルは Python と C++ が**同じファイルをそのまま読める**形式に保つ価値が高い。

`dataclass` による定義は C++ の `struct` にほぼ 1:1 で対応するため、スキーマ自体も移植の足場になる。

### 2. multirun の恩恵がない

Hydra の最大の売りである multirun（並列スイープ）は、**サーボが物理的に 1 台**である以上機能しない。
実機を伴う制御パラメータのチューニングは本質的に逐次実行になる。

### 3. 依存関係の増加

`requirements-rpi.txt` は現在 5 パッケージの最小構成で、`--system-site-packages` の venv で apt 側の
`picamera2` / `libcamera` / GPIO 系と組み合わせて動かしている。ここに `hydra-core` + `omegaconf` +
`antlr4-python3-runtime` を持ち込むと、実機環境の再現性リスクに見合わない。

### 4. 作業ディレクトリの変更が既存前提と衝突する

Hydra は既定で cwd を `outputs/<日時>/` に変更する（`hydra.job.chdir`）。
既存スクリプトは `REPO_ROOT` を起点にした相対パスで出力先を解決しており、この挙動と噛み合わない。

## 結果と影響

- 設定ファイルの合成機能は自前実装が必要になる（deep merge。10 行程度で足りる見込み）
- CLI からの動的な上書きは Hydra ほど手軽ではなくなる
- 一方で、設定ファイルが Python / C++ 双方から読める資産になる
- `requirements-rpi.txt` の最小構成が維持される

## 再検討する条件

以下のいずれかに該当した場合、この判断を再検討する（新しい ADR を追加する）。

- 設定の合成ロジックが自前実装で手に負えない複雑さになった
- C/C++ 移植の方針自体が変わり、Python で運用し続けることになった
- ラズパイ側で大規模なパラメータスイープを自動実行する必要が生じた
