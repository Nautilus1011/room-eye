# CLAUDE.md — room-eye

このファイルは Claude Code や同種のエージェントが、このリポジトリで迷わず作業するための実務ガイドです。

## プロジェクト概要

- 名称: `room-eye`
- 主題: ラズベリーパイ + カメラ + YOLO による自室のスマートホーム化
- 実現したい機能:
  - ハンドジェスチャー認識 → PC の Wake on LAN・扇風機・照明の制御
  - 床の空き面積算出 → 部屋の散らかり度の定量化
  - 物体カウント（コップ・ペットボトル等）→ 片付け通知

## ディレクトリの見方

- `src/room_eye/`: パッケージ本体（エントリーポイント・共通処理）
- `experiment/`: 実験・検証用の Notebook・スクリプト（使い捨て可）。各実験ディレクトリの説明ドキュメント`EXPERIMENT.md` を作成する
- `data/`: 学習・推論用データ（Git 管理外）
- `models/`: モデルファイル（Git 管理外）
- `outputs/`: 推論結果・出力（Git 管理外）
- `scripts/`: 実行用スクリプト
- `notebooks/`: 分析・可視化用 Notebook
- `external/`: 外部リポジトリ（Git 管理外）

## 開発環境

標準環境は Docker (`docker-compose.yml` の `dev` サービス) です。

```bash
# イメージビルド
docker compose build dev

# コンテナ起動
docker compose up -d dev

# インタラクティブシェル
docker compose exec dev bash
```

VS Code を使う場合は `.devcontainer/devcontainer.json` が定義済みなので、**Dev Containers** 拡張でそのまま開けます。

## 実行コマンド

### 最低限の構文チェック

```bash
python3 -m compileall src experiment
```

Docker 経由の場合:

```bash
docker compose exec dev bash -lc "python3 -m compileall src experiment"
```

## 実装方針

1. 既存パターンを優先する。新しい抽象化は必要な時だけ入れる。
2. `src/room_eye/` は再利用対象、`experiment/` は実験対象として扱う。
3. 重い成果物や一時生成物は Git に入れない。
4. パス・閾値・ハイパーパラメータはコードにハードコードせず設定ファイルに逃がす。
5. ラズパイ（ARM64 CPU のみ）での動作を常に意識した実装にする。

## 実装完了の必須チェックリスト

**コミット前・PR 作成前に必ず全項目を確認すること。**

- [ ] 1 コミット = 1 つの論理的変更（原子コミット）
- [ ] Conventional Commits 形式（`feat:` / `fix:` / `docs:` / `chore:` 等）
- [ ] `git diff` が意図した差分だけになっている
- [ ] `data/`・`outputs/`・`models/`・学習済み重みが含まれていない
- [ ] `python3 -m compileall src experiment` が通る
- [ ] 実行できなかった検証があれば、PR の `## 補足情報` に理由を明記する
- [ ] Issue 対応の場合、該当 Issue に実装内容・達成状況・検証結果・残課題をコメントする
- [ ] PR 本文は `.github/PULL_REQUEST_TEMPLATE.md` に従っている
- [ ] **PR のマージはユーザーが実施する（エージェントはマージしない）**

## 参照ルール

- `.claude/rules/github-workflow.md`
- `.claude/rules/coding-standards.md`
- `.claude/rules/cv-research.md`
- `.claude/rules/project-guardrails.md`
- `.claude/rules/hardware.md`
- `.claude/rules/experiment-report.md`
