# GitHub Workflow Rules — room-eye

## ブランチ運用

- `main` への直接コミットは禁止。変更は必ず PR 経由でマージする。
- ブランチ命名:
  - `feat/<name>`
  - `fix/<name>`
  - `chore/<name>`
  - `refactor/<name>`
  - `experiment/<name>`
  - `docs/<name>`

---

## コミットルール

### 原子コミットの徹底

- 1 コミット = 1 つの論理的変更を原則とする
- 「リファクタリング」と「新機能追加」は必ず別のコミットに分ける

### Conventional Commits 形式

| プレフィックス | 用途 |
|---|---|
| `feat:` | 新機能 |
| `fix:` | バグ修正 |
| `docs:` | ドキュメントのみの変更 |
| `style:` | コードの意味に影響しない変更（空白・フォーマット等） |
| `refactor:` | バグ修正も機能追加も行わないコード変更 |
| `chore:` | ビルドプロセスや依存関係の変更 |
| `experiment:` | 実験・検証の追加・更新 |

スコープ例:

```text
feat(gesture): add hand landmark detection
fix(detect): correct bounding box coordinate scaling
chore(docker): update base image to pytorch 2.6
experiment(yolo): test yolo11n inference speed on CPU
docs(readme): add raspberry pi setup instructions
```

---

## Issue 作成

必ず `.github/ISSUE_TEMPLATE/` のテンプレートに沿って作成する。

- 粒度が大きすぎる issue は分割する
- 重複する issue を増やさない

---

## PR 作成

`.github/PULL_REQUEST_TEMPLATE.md` に従い、以下のセクションをすべて埋める。

- `## 関連Issue` は必ず埋める
- `## 動作確認` には実際に行ったものだけをチェックする
- 実行できなかった検証は `## 補足情報` に理由を書く

---

## Issue への作業報告

Issue に対応する作業を行った場合は、完了後に GitHub Issue へコメントでレポートを残す。

コメントには以下を含める。

- 実装した内容
- Issue の完了条件に対する達成状況
- 実行した検証コマンドと結果
- 未対応事項・制約・次に確認すべき点

---

## マージ

- PR のマージはユーザーが行う
- エージェントは勝手にマージしない
