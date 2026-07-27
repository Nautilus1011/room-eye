---
作成日: 2026-07-27
最終更新: 2026-07-27
ステータス: 採用
---

# ADR-0002: Python / C++ のディレクトリ構成

## 背景

room-eye は Python で検証し C/C++ で運用する（`../roadmap.md`）。両言語のコードを同一リポジトリに
どう配置するかを決める必要がある。検討した案は 4 つ。

| 案 | 構成 | 評価 |
| :--- | :--- | :--- |
| A | `src/` を C++ 専用にし、Python は `experiment/` に置く | ❌ 却下 |
| B | `src/python/` と `src/cpp/` で最上位から言語分割 | ❌ 却下 |
| C | モジュールごとに `control/py/` `control/cpp/` を掘る | ❌ 却下 |
| D | `room_eye/`（Python）+ `src/` `include/`（C++） | ✅ 採用 |

判断にあたり、同種のプロジェクトの実際の慣習を調査した。

## 決定

**案 D を採用する。言語の分割はトップレベルで 1 回だけ行う。**

```
room-eye/
├── config/                  ★共有: 両言語が読む YAML
├── models/                  ★共有: .onnx（Git 管理外）
├── room_eye/                Python 実装（フラットレイアウト）
│   ├── control/
│   ├── hal/
│   └── perception/
├── include/room_eye/        ← Phase 4: C++ ヘッダ
├── src/                     ← Phase 4: C++ 実装
├── apps/                    ← Phase 4: C++ エントリーポイント
├── tests/{py,cpp,fixtures}/
└── experiment/
```

## 理由

### 1. 案 A の却下 — `experiment/` は使い捨て領域

`experiment/` は CLAUDE.md で「使い捨て可」と定義されている。しかし `control/` は Phase 3 の
ゴールデンデータで **C++ の正しさを検証し続けるリファレンス実装**であり、役割と置き場が矛盾する。

また Python は C++ までの繋ぎではない。追尾の後にジェスチャー認識・床面積算出・物体カウントが控えており、
どの機能も Python 検証から始まる。**Python は恒久的なプロトタイピング系**である。

### 2. 案 C の却下 — 実際の現場でこの構成は使われていない

調査の結果、モジュールごとに `py/` `cpp/` を掘る構成は主要な慣習のどこにも見当たらなかった。

**ROS 2**（ロボティクス・C++/Python 混在・実機制御と条件が最も近い）の混在パッケージ:

```
my_cpp_py_pkg/
├── my_cpp_py_pkg/          Python パッケージ（再利用モジュール）
├── scripts/                Python 実行ノード
├── include/my_cpp_py_pkg/  C++ ヘッダ
└── src/                    C++ 実装
```

**pybind11 / scikit-build-core の公式テンプレート**:

```
├── src/
│   ├── main.cpp                          C++
│   └── scikit_build_example/__init__.py  Python パッケージ
└── tests/
```

Scientific Python の公式ガイドも「ソースは `/src`、Python パッケージは `/src/<package>`」としている。
いずれも**言語で分けるのはトップレベル 1 回だけ**で、モジュール単位の入れ子はしない。

入れ子は import パスに `py` が挟まって読みにくくなり（`room_eye.control.py.pid`）、
CMakeLists.txt が深い階層に散らばる。得られる「移植進捗の可視性」は、
`room_eye/` と `src/` のミラー構造でも同じように得られる。

### 3. 案 B より案 D が良い理由 — `src/` が何も仕切っていない

案 B（`src/python/` + `src/cpp/`）では `src/` の下に 2 つのツリーができるが、
C++ も Python も結局モジュール構成が同じなので、`src/` という階層が意味を持たない。

案 D は `src/` を C++ 専用にすることで C++ の慣習に合わせ、Python 側は `src/` を挟まない
フラットレイアウトにして冗長な階層を消している。深さは案 B と同じで、両言語とも自然な形になる。

### 4. モジュールを `src/` 直下に置かない理由 — 名前空間の衝突

`control` / `hal` / `perception` / `config` を `src/` 直下に置くと、これらがトップレベルの
名前空間を占有する。**`control` は PyPI に同名パッケージが実在する**（Python Control Systems Library。
PID や状態空間モデルを扱う、このプロジェクトが将来導入しかねないもの）。

さらにラズパイ側の venv は `--system-site-packages` で apt の `dist-packages` と名前空間を共有しており、
通常より衝突リスクが高い。`pip install -e .` した場合は 3 つの独立したトップレベルパッケージが
site-packages に入ることにもなる。

`room_eye` 名前空間を残すことでこれを回避する。
なお scikit-build-core が Python パッケージとして自動認識するのは `<package_name>` /
`src/<package_name>` / `python/<package_name>` の 3 つで、**リポジトリ直下の `room_eye/` は正式にサポートされている**。

### 5. 共有資産を言語ツリーの外に置く

`config/`（両言語が読む YAML）・`models/`（同じ `.onnx`）・`tests/fixtures/`（ゴールデンデータ）は
どちらの言語にも属さない。[ADR-0001](0001-no-hydra-on-rpi.md) の「両言語が同じ設定ファイルを読む」方針と、
`../design/cpp-migration.md` のゴールデンデータ方式の前提がこれ。

Python 版と C++ 版は**参照実装と運用実装という対等なピア**であり、共有資産を挟んで両側に立つ。

## 結果と影響

- `setup.cfg` の `package_dir` / `[options.packages.find]` が不要になる（フラットレイアウト）
- `python3 -m compileall src experiment` → 対象パスの変更が必要（CLAUDE.md・coding-standards.md）
- `.claude/rules/project-guardrails.md` の `src/` に関する記述の更新が必要
- C++ の実体は Phase 4 まで存在しないため、`include/` `src/` `apps/` `tests/cpp/` は
  **その時点で作る**（Git は空ディレクトリを追跡しない）

## 再検討する条件

- Python パッケージを PyPI に配布することになった場合（`src` レイアウトの利点が効いてくる）
- C++ 側が単一プロジェクトに収まらず、複数のビルドターゲットに分割が必要になった場合

## 参考

- [Create a ROS2 package for Both Python and Cpp Nodes — The Robotics Back-End](https://roboticsbackend.com/ros2-package-for-both-python-and-cpp-nodes/)
- [pybind/scikit_build_example](https://github.com/pybind/scikit_build_example)
- [Packaging Compiled Projects — Scientific Python Development Guide](https://learn.scientific-python.org/development/guides/packaging-compiled/)
- [Getting started — scikit-build-core documentation](https://scikit-build-core.readthedocs.io/en/latest/guide/getting_started.html)
