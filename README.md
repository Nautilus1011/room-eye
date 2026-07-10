# Room Eye

ラズベリーパイ + カメラ + 画像認識技術を使って、自室の利便性向上・課題解決を図るプロジェクトです。

## プロジェクトの目的

部屋にカメラを設置し、常時または定期的に映像を解析することで以下を実現します。

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
[Raspberry Pi + Camera]
        |
   物体検出 / 姿勢推定（YOLO系）
        |
   ┌────┴─────────────────┐
   |                      |
ジェスチャー認識        部屋状態の解析
   |                      |
スマートデバイス制御    通知・レポート出力
(Wake on LAN / 家電)
```

## 技術スタック

- **推論**: YOLO（最新バージョンを採用予定）
- **実行環境**: Raspberry Pi（ARM64）
- **開発環境**: Docker
- **言語**: Python 3.9+

## ディレクトリ構成

```
room-eye/
├── experiment/       # 実験・検証用 Notebook・スクリプト
│   └── yolov5/       # YOLOv5 推論テスト（初期実験）
├── external/         # 外部リポジトリ（clone先）
├── data/             # 学習・推論用データ
├── models/           # モデルファイル
├── outputs/          # 推論結果・出力
├── scripts/          # 実行スクリプト
├── notebooks/        # 分析・可視化用 Notebook
└── tests/            # テストコード
```

## 開発環境セットアップ

> Docker ベースの環境整備が進行中です（[#8](https://github.com/Nautilus1011/room-eye/issues/8)）。
> 現状はローカル venv での作業を想定しています。

```bash
pip install -e .
pip install -r requirements-dev.txt
pre-commit install
```

## 実験記録

| Notebook | 内容 |
|---|---|
| `experiment/yolov5/infer-yolov5.ipynb` | YOLOv5s.pt による推論テスト（初期実験） |

## License

MIT License
