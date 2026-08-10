---
作成日: 2026-07-27
最終更新: 2026-07-27
ステータス: active
---

# docs — room-eye の計画・方針ドキュメント

このディレクトリは room-eye の **計画・設計方針と、その判断理由** をまとめる場所です。
実装を進めながら継続的に更新していくことを前提とします。

## 文書の使い分け

room-eye には 3 種類の文書があります。書く前にどれに当たるかを判断してください。

| 置き場所 | 役割 | 性質 |
| :--- | :--- | :--- |
| `.claude/rules/` | エージェントが**守るべき制約**（GPIO 割当・禁止事項・命名規則） | 短く規範的。「何を守るか」だけを書き、理由は書かない |
| `docs/`（ここ） | **計画・設計方針と、そう決めた理由** | 育てる文書。実装しながら更新する |
| `experiment/<name>/EXPERIMENT.md` | 個別実験の**記録** | 実施した内容の記録。原則あとから書き換えない |

判断に迷ったときの目安:

- 「GPIO14 はパン軸」→ `.claude/rules/hardware.md`（守るべき事実）
- 「なぜソフトウェア PWM が問題で PCA9685 を検討するのか」→ `docs/`（判断と理由）
- 「pigpio に切り替えて実測したら FPS はこうだった」→ `EXPERIMENT.md`（実験結果）

## 構成

```
docs/
├── README.md                    このファイル。索引と運用ルール
├── roadmap.md                   プロジェクト全体の計画（Phase 0〜4）
├── design/                      設計方針（機能横断）
│   ├── architecture.md          レイヤ構成と移植性を基準にした分割方針
│   └── cpp-migration.md         C/C++ 移植方針・ライブラリ対応
├── plans/                       機能ごとの実験・開発方針
│   └── auto-tracking.md         カメラ自動追尾
└── adr/                         意思決定記録（Architecture Decision Record）
    ├── README.md
    ├── 0001-no-hydra-on-rpi.md
    └── 0002-directory-layout.md
```

## 索引

### 全体

- [roadmap.md](roadmap.md) — Phase 0〜4 の全体計画と現在地

### 設計方針

- [design/architecture.md](design/architecture.md) — `hal` / `control` / `perception` のレイヤ構成、設定管理方式
- [design/cpp-migration.md](design/cpp-migration.md) — C/C++ 移植の方針、ライブラリ対応表、ゴールデンデータによる検証

### 機能別の計画

- [plans/auto-tracking.md](plans/auto-tracking.md) — カメラ自動追尾の実験・開発方針

### 意思決定記録

- [adr/README.md](adr/README.md) — ADR の索引と書き方
- [adr/0001-no-hydra-on-rpi.md](adr/0001-no-hydra-on-rpi.md) — ラズパイ実行系の設定管理に Hydra を採用しない
- [adr/0002-directory-layout.md](adr/0002-directory-layout.md) — Python / C++ のディレクトリ構成

## 運用ルール

詳細は `.claude/rules/documentation.md` を参照。要点のみ:

- すべての文書の先頭に `作成日` / `最終更新` / `ステータス` の frontmatter を置く
- 内容を変更したら `最終更新` を必ず更新する
- `roadmap.md`・`design/`・`plans/` は**書き換えていく生きた文書**
- `adr/` は**追記専用**。判断を覆すときは既存ファイルを書き換えず、新しい番号を追加して旧番号を `superseded` にする
