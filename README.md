# Room Eye

ラズベリーパイ + カメラ + 画像認識技術を使って、自室の利便性向上・課題解決を図るプロジェクトです。

## プロジェクトの目的

部屋にカメラを設置し、映像を解析することで以下を実現します。

### カメラ自動追尾 ← 現在の主対象

パン・チルト 2 軸のサーボでカメラを動かし、映った対象を画面中心に保ち続けます。

| 項目 | 内容 |
|---|---|
| 追尾対象 | **人（`person`）と犬（`dog`）** |
| 対象の選び方 | 先に検出した対象を、見失うまで追い続ける（複数映っても乗り換えない） |
| 可動範囲 | あらかじめ設定した運用可動範囲まで。**範囲外に出た対象は追わず、端で停止して見続ける** |
| 動作環境 | 照明点灯下の明るい部屋（低照度・暗所は当面スコープ外） |

詳細な要件と制御方針は [docs/plans/auto-tracking.md](docs/plans/auto-tracking.md) を参照してください。

### 操作自動化（ジェスチャーコントロール）

| ジェスチャー | アクション |
|---|---|
| 特定のハンドサイン | デスクトップPC の Wake on LAN |
| 特定のハンドサイン | 扇風機のオン/オフ |
| 特定のハンドサイン | 部屋の照明のオン/オフ |

### 部屋の状態モニタリング

- **床面積の計測**: 床の空き面積を算出し、部屋の散らかり具合を定量化
- **物体カウント**: コップやペットボトルなどの数を検出し、片付けを促す通知を出す

## システム構成（予定）

```
[Raspberry Pi + Pan-Tilt Camera]
        |
   物体検出 / 姿勢推定（YOLO系）
        |
   ┌────┴──────┬─────────────────┐
   |           |                 |
自動追尾   ジェスチャー認識   部屋状態の解析
   |           |                 |
サーボ制御  スマートデバイス制御  通知・レポート出力
(パン/チルト) (Wake on LAN / 家電)
```

## 開発の進め方

**Python で検証し、C/C++ で運用する**方針です。Python フェーズの成果物はコードそのものではなく、
検証済みのパラメータ値とアルゴリズム仕様と位置づけています。

フェーズごとの計画と現在地は [docs/roadmap.md](docs/roadmap.md) を参照してください。

## 技術スタック

- **推論**: YOLO 系の軽量モデル（ラズパイ CPU での実測を経て選定）
- **実行環境**: Raspberry Pi（ARM64・CPU のみ）
- **開発環境**: Docker（GPU 側のモデル開発）/ ラズパイ実機の venv（ハードウェア制御）
- **言語**: Python（検証）→ C/C++（運用）

## ディレクトリ構成

```
room-eye/
├── docs/             # 計画・設計方針とその判断理由（まず docs/README.md を参照）
├── src/room_eye/     # パッケージ本体
├── experiment/       # 実験・検証用 Notebook・スクリプト（EXPERIMENT.md に記録を残す）
├── external/         # 外部リポジトリ（clone先・Git 管理外）
├── data/             # 学習・推論用データ（Git 管理外）
├── models/           # モデルファイル（Git 管理外）
├── outputs/          # 推論結果・出力（Git 管理外）
├── scripts/          # 実行スクリプト
├── notebooks/        # 分析・可視化用 Notebook
└── tests/            # テストコード
```

## 開発環境セットアップ

用途によって 2 つの環境を使い分けます。

### GPU 環境（モデル開発・学習）

Docker (`docker-compose.yml` の `dev` サービス) を標準環境とします。
VS Code の **Dev Containers** 拡張でもそのまま開けます。

```bash
docker compose build dev
docker compose up -d dev
docker compose exec dev bash
```

依存関係は `requirements-dev.txt` にまとめています。

### ラズパイ実機（カメラ・サーボ制御）

`picamera2` や GPIO 系ライブラリは OS 側のパッケージを使うため、
`--system-site-packages` で作成した venv 上で実行します。

```bash
source venv/room-eye/bin/activate
python3 experiment/pan_tilt_camera_check/scripts/capture_photo.py
```

依存関係は `requirements-rpi.txt` にまとめています。

## 実験記録

各実験の詳細は実験ディレクトリ内の `EXPERIMENT.md` を参照してください。

| 実験 | 内容 |
|---|---|
| `experiment/pan_tilt_camera_check/` | パン・チルトサーボ + カメラの実機動作確認 |
| `experiment/yolov5/` | YOLOv5s による推論テスト（初期実験） |
| `experiment/yolov8/` | YOLOv8 による推論・人物検出テスト |
| `experiment/cpp_opencv_intro/` | C++ / OpenCV の導入検証 |

## License

**GNU Affero General Public License v3.0 (AGPL-3.0)**

Copyright (C) 2025-2026 Jin Yasuda

採用理由は [docs/adr/0003-agpl-license.md](docs/adr/0003-agpl-license.md) を参照してください。
