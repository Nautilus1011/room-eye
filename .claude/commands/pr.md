現在のブランチから GitHub PR を作成してください。

## 手順

1. `git log main..HEAD --oneline` でコミット一覧を確認
2. `git diff main...HEAD --stat` で変更ファイルを確認
3. `.github/PULL_REQUEST_TEMPLATE.md` に沿って本文を作成
4. 実行した検証と、実行していない検証を明示する

## ルール

- タイトルは Conventional Commits 形式
- `main` へ直接 push しない
- マージはユーザーが行う
- issue 対応なら `## 関連Issue` に番号を入れる

## ひな形

```bash
gh pr create --title "<type>(<scope>): <summary>" --body "$(cat <<'EOF'
## 変更内容
- <変更点>

## 関連Issue
- #<番号>

## 動作確認
- [ ] `python3 -m compileall src experiment`
- [ ] 対象スクリプトの限定実行
- [ ] Docker コンテナ内での動作確認

## 補足情報
<重い検証を省略した理由や前提条件>
EOF
)"
```
