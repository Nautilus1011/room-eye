---
作成日: 2026-07-27
最終更新: 2026-07-27
ステータス: active
---

# アーキテクチャ設計方針

`room_eye/` のレイヤ構成と設計上の決めごと。C/C++ 移植の具体的な手順は `cpp-migration.md` を参照。
ディレクトリ構成を決めた経緯は [ADR-0002](../adr/0002-directory-layout.md)。

## 基本方針: 「移植性」でレイヤを切る

room-eye は Python で検証し C/C++ で運用する（`../roadmap.md`）。
そのため、モジュールを**機能で分けるのではなく、C++ 移植時に書き直す必要があるかどうかで分ける**。

| レイヤ | 移植時の扱い | 依存 |
| :--- | :--- | :--- |
| `hal/` | **全面書き直し** | `gpiozero` / `picamera2` などラズパイ固有 |
| `control/` | **ほぼ 1:1 で移植** | **なし**（標準ライブラリのみ） |
| `perception/` | **API 差し替え**（同じ `.onnx` を共用） | `onnxruntime` / `numpy` |
| `config.py` | `struct` + yaml-cpp に対応 | `PyYAML` |

`control/` がロジックの本体であり、最も丁寧に書く価値がある層。ここを外部依存ゼロに保つことが、
Phase 3 のゴールデンデータによる言語横断テスト（`cpp-migration.md`）を成立させる前提になる。

## ディレクトリ構成

言語の分割は**トップレベルで 1 回だけ**行う。モジュールごとに `py/` `cpp/` を掘る入れ子はしない
（判断の経緯と調査結果は [ADR-0002](../adr/0002-directory-layout.md)）。

```
room-eye/
├── CMakeLists.txt           ← Phase 4
├── pyproject.toml
├── config/                  ★共有: 両言語が読む YAML（hardware.yaml 等）
├── models/                  ★共有: .onnx（Git 管理外）
│
├── room_eye/                Python 実装。src/ を挟まないフラットレイアウト
│   ├── __init__.py
│   ├── __main__.py          python -m room_eye
│   ├── config.py
│   ├── control/             geometry.py / pid.py
│   ├── hal/                 servo.py / camera.py
│   └── perception/          detector.py
│
├── include/room_eye/        ← Phase 4: C++ ヘッダ
│   ├── control/
│   ├── hal/
│   └── perception/
├── src/                     ← Phase 4: C++ 実装
│   ├── control/
│   ├── hal/
│   └── perception/
├── apps/                    ← Phase 4: C++ エントリーポイント（main.cpp）
│
├── tests/
│   ├── py/
│   ├── cpp/                 ← Phase 4
│   └── fixtures/            ★共有: ゴールデンデータ
└── experiment/              薄い CLI + EXPERIMENT.md
```

### 構成の要点

- **`src/` は C++ 専用**。C++ の慣習どおりで、ROS 2 の混在パッケージとも一致する。
  `src/` が `room_eye/` 1 つしか抱えない冗長な入れ子を避けられる
- **Python は `room_eye/` フラットレイアウト**。`room_eye.control.pid` で import でき、
  `py/` のような中間階層が挟まらない。`room_eye` 名前空間が残るので、
  `control` などのトップレベル名の衝突も避けられる（`control` は PyPI に同名パッケージが実在する）
- **移植の進捗は `room_eye/` と `src/` のミラー構造で見える**。`src/control/` はあるが
  `src/perception/` はない、という状態が一目でわかる
- **共有資産（`config/` `models/` `tests/fixtures/`）は両ツリーの外**に置く。
  同じ設定ファイル・同じ `.onnx`・同じゴールデンデータを両言語が読むのが前提だから
  （[ADR-0001](../adr/0001-no-hydra-on-rpi.md)、`cpp-migration.md`）

### `experiment/` の扱い

`experiment/` のスクリプトには**ロジックを置かない**。引数のパース、設定の読み込み、
`room_eye` の呼び出し、結果の表示に限る。

`experiment/` は「使い捨て可」と定義されている領域（CLAUDE.md）なので、
再利用するロジック・移植対象のロジックをここに残さない。

## 現状との差分（Phase 0 で埋める）

`experiment/pan_tilt_camera_check/scripts/` に `servo.py`（`build_servo` / `clamp` / `PanTilt`）と
`camera.py`（`PanTiltCamera`）が切り出され、スクリプト間の重複と `try/finally` の手書きは解消済み。

Phase 0 で残っているのは以下。

| 項目 | 現状 | あるべき姿 |
| :--- | :--- | :--- |
| 置き場 | `experiment/` 配下（使い捨て領域） | `room_eye/` 配下（恒久資産） |
| レイヤ分離 | `clamp` が `servo.py` に同居し、`gpiozero` を import するモジュールに閉じ込められている | `clamp` は `control/` へ。実機なしで import・テストできる状態にする |
| 設定 | `dict` を直接受け渡し（`axis_config["gpio_pin"]`） | `dataclass` による型付き設定 |
| import | `from gpiozero import AngularServo` がモジュールトップ | 遅延 import（後述） |
| ハードウェア定義 | 2 つの YAML に `servo:` ブロックが重複 | `config/hardware.yaml` に集約 |

## 設計上の決めごと

### 1. `control/` に numpy を持ち込まない

素の `float` だけで書く。ベクトル化の必要がない粒度の計算しか行わないため性能上の問題はなく、
C++ への移植が機械的な作業になる。

### 2. HAL のインターフェースは狭く保つ

`gpiozero.AngularServo` や `Picamera2` のオブジェクトを層の外に漏らさない。
漏らすと呼び出し側が Python 固有 API に依存し、移植範囲が `hal/` の外まで広がる。

公開するのは「角度を指定する」「解放する」「画像を取得する」といった**意味のある操作**だけにする。

### 3. `hal/` の import は遅延させる

`picamera2` / `gpiozero` をモジュールトップで import すると、Mac や GPU 側の Docker 環境で
`import room_eye` すら通らなくなる（これらは `requirements-rpi.txt` 側にしかない）。

コンストラクタや関数の内部で import すること。**`control/` の単体テストが実機なしで回せることが重要**で、
これは Phase 3 のゴールデンデータ検証の前提でもある。

```python
class PanTilt:
    def __init__(self, config: ServoConfig) -> None:
        from gpiozero import AngularServo  # 実機以外では import できないため遅延
        ...
```

### 4. リソース解放は context manager で保証する

`hal/` のクラスは `__enter__` / `__exit__` を実装し、呼び出し側は `with` で使う
（現行の `PanTilt` / `PanTiltCamera` で実装済み）。

```python
with PanTilt(cfg.servo) as pan_tilt, Camera(cfg.camera) as camera:
    ...
```

### 5. ultralytics の便利メソッドに寄りかからない

C++ 側に等価物がないため、letterbox・正規化・NMS は自前で実装しておく。
そうすれば移植が「同じ処理の書き換え」で済み、再設計にならない。

### 6. 並行処理の構造を Python 段階から合わせる

キャプチャ / 推論 / 制御をスレッド分離する場合、C++ では `std::thread` + リングバッファになる。
**Python 段階から同じ producer / consumer 構造で書いておく**こと。構造が同じなら移植であって再設計にならない。

制御ループは推論より速い周期で回す（最新の検出結果を保持しつつ制御周期を上げる）設計を前提とする。

## エントリーポイント

| 対象 | 起動方法 | 実体 |
| :--- | :--- | :--- |
| 本体アプリ（Python） | `python -m room_eye` | `room_eye/__main__.py` |
| 本体アプリ（C++） | ビルドした実行ファイル | `apps/main.cpp`（Phase 4） |
| 実験スクリプト | `python3 experiment/<name>/scripts/<script>.py` | 各スクリプトの `if __name__ == "__main__":` |

### エントリーポイントは薄くする

`__main__.py` に処理を書かず、実体は `cli.py` に置いて呼ぶだけにする。

```python
# room_eye/__main__.py
from room_eye.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
```

理由:

1. **テストできる**。`from room_eye.cli import main` でテストから叩ける
2. **後から `room-eye` コマンド化できる**。`pyproject.toml` に
   `[project.scripts] room-eye = "room_eye.cli:main"` を足すだけで済む
3. **C++ 側と対称になる**。`apps/main.cpp` も薄いラッパにするため、
   **ロジックがライブラリ層にあること**が両言語で保証される。
   エントリーポイントに処理を書くと、そこは移植対象から漏れる

機能が増えたら `python -m room_eye track` のようにサブコマンド方式にする。
C++ 側で機能ごとにバイナリを分けたくなった時点で `apps/` に分割できる。

### ⚠️ 実験スクリプトから `room_eye` を import するには editable install が必要

**`python3 script.py` で直接実行した場合、`sys.path[0]` はスクリプトのあるディレクトリになる**
（cwd ではない）。実測:

```
python3 sub/script.py   →  sys.path[0] = .../sub      ← スクリプトの場所
python3 -m sub.script   →  sys.path[0] = ...          ← cwd
```

そのため `python3 experiment/pan_tilt_camera_check/scripts/capture_photo.py` を実行すると
`sys.path[0]` は `.../scripts/` になり、**リポジトリルートから実行しても `import room_eye` は失敗する**。

対処は **`venv/room-eye` への editable install**（`pip install -e .`）とする。
どこから実行しても import が通り、実験スクリプトの実行方法は現状のまま変わらない。

- ❌ スクリプト内での `sys.path` 書き換えはしない（絶対パス増加の温床。`.claude/rules/coding-standards.md`）
- ❌ 実験スクリプトを `python3 -m ...` 起動にはしない（`experiment/` 配下すべてに `__init__.py` が必要になる）

`venv/room-eye` は `--system-site-packages` で作られているが、そこに editable install を足して問題ない。
Phase 0 でこの手順を `EXPERIMENT.md` のセットアップ手順に追加すること。

## 設定管理

Hydra は採用しない。判断の理由は [ADR-0001](../adr/0001-no-hydra-on-rpi.md)。

### 方式

- スキーマは `dataclass(frozen=True)` で型付き定義する。C++ の `struct` に 1:1 対応させる
- 設定ファイルは素のフラットな YAML。`PyYAML` で読む
- 複数ファイルの合成は辞書の deep merge を自前実装する（後勝ち）

```python
@dataclass(frozen=True)
class AxisConfig:
    gpio_pin: int
    min_angle: float
    max_angle: float
    min_pulse_width: float
    max_pulse_width: float
```

### ファイルの階層

ハードウェア定義は**リポジトリ共通の不変値**であり、実験ごとに複製すべきではない
（現状 `servo_camera_check.yaml` と `pan_tilt_explore.yaml` で `servo:` ブロックが重複している）。

```
config/hardware.yaml                      共通。GPIO 割当・可動域・パルス幅・カメラ取付向き
experiment/<name>/config/<name>.yaml      実験固有。待機時間・waypoints・出力先など
```

読み込み時に共通 → 実験固有の順で merge する。実験固有ファイルでハードウェア定義を上書きすることは
原則しない（`.claude/rules/hardware.md` の制約に反するため）。

### パスの扱い

- 設定ファイル内のパスは**リポジトリルートからの相対パス**で書く
- 絶対パスを新たに増やさない（`.claude/rules/coding-standards.md`）
- 可動域を超える角度指定は `control/geometry.py` の clamp で必ず抑える

## `room_eye/` に置いてよいもの・いけないもの

`.claude/rules/project-guardrails.md` の「ラズパイで動かない前提のコードを混ぜない」に従う。

- ✅ `hal/` — ラズパイ固有だが、ラズパイ**で動く**コードなので置いてよい
- ✅ `control/` `perception/` — 環境非依存
- ❌ GPU 必須の学習コード — `experiment/` または別の場所に置く
