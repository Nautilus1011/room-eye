---
name: survey
description: "指定 Issue のトピックを調査し、docs/survey/ に記録して Issue にコメントする"
argument-hint: "<issue_number>"
---

# /survey

指定した Issue のトピックについて論文・ブログ・OSS 実装を調査し、結果を `docs/survey/` に記録して Issue へコメントする。

## 使い方

```text
/survey 11
/survey 12
```

## 手順

### 1. Issue の読み込み

```bash
gh issue view <issue_number> --repo Nautilus1011/room-eye
```

Issue のタイトル・本文から「カテゴリ」「調査対象キーワード」「制約条件」を把握する。

### 2. 出力先の決定

`docs/survey/` 配下のカテゴリディレクトリを確認し、適切なファイル名を決める。

| Issue カテゴリ | 出力先 |
|---|---|
| ジェスチャー認識 | `docs/survey/gesture/<トピック>.md` |
| 物体検出・カウント・面積 | `docs/survey/detection/<トピック>.md` |
| エッジ推論・軽量化 | `docs/survey/edge-inference/<トピック>.md` |

### 3. 調査（WebSearch）

以下の観点で検索を行う。それぞれ 2〜3 件の信頼性の高い情報源を収集する。

- **論文・公式資料**: `<キーワード> paper arxiv`, `<キーワード> CVPR ICCV`
- **ブログ・実装**: `<キーワード> raspberry pi implementation`, `<キーワード> github`
- **ベンチマーク**: `<キーワード> raspberry pi CPU benchmark FPS`

ラズパイ CPU 動作に関する情報を優先的に収集する。

### 4. docs ファイルへの記録

`.claude/rules/survey-workflow.md` の形式に従ってファイルを作成・更新する。

必須項目:
- 冒頭フロントマター（関連Issue番号・調査日・カテゴリ）
- 論文・公式資料テーブル
- ブログ・実装事例テーブル
- まとめ・所感（room-eye への応用可能性）

### 5. Issue へのコメント

```bash
gh issue comment <issue_number> --repo Nautilus1011/room-eye --body "$(cat <<'EOF'
## 調査完了

docs に記録しました → `docs/survey/<カテゴリ>/<ファイル名>.md`

### 主な発見

- <箇条書き 3〜5 点>

### 参考リンク

- [タイトル](URL)

### 次のアクション（任意）

- <実装・実験に向けた次のステップ>
EOF
)"
```

## 注意

- 未確認・未読の文献はリンクだけ記録し「未読」と明記してよい
- 調査中に発見した派生トピックは別ファイルを作り元ファイルからリンクする
- Issue のクローズはユーザーが判断する。スキル実行だけでクローズしない
