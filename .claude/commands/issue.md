GitHub Issue を作成してください。内容: "$ARGUMENTS"

## ルール

- `.github/ISSUE_TEMPLATE/` のテンプレートに従う
- タイトルは後で一覧を見た時に判別できる粒度にする
- 「実装」「実験」「環境整備」を混ぜすぎない

## 機能追加のひな形

```bash
gh issue create --label enhancement --title "<タイトル>" --body "$(cat <<'EOF'
## 概要

<追加または変更する機能の説明>

## 背景

<なぜ必要か>

## やること
- [ ]

## 補足事項 (optional)

<補足>
EOF
)"
```

## バグ報告のひな形

```bash
gh issue create --label bug --title "<タイトル>" --body "$(cat <<'EOF'
## 概要
<バグの要約>

## 再現手順
1.
2.
3.

## 期待される動作
<期待値>

## 実際の動作
<実際の挙動>

## 環境情報
- OS:
- Python version:
- Docker image:
- その他:

## 補足事項 (optional)

<補足>
EOF
)"
```
