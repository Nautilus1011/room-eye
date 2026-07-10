PR 前の動作確認を行ってください。

## 基本チェック

まず変更ファイルを確認します。

```bash
git diff main...HEAD --name-only
```

次に、Python コードを変更している場合は最低限これを実行します。

```bash
docker compose exec dev bash -lc "python3 -m compileall src experiment"
```

## 追加チェックの考え方

- `src/` や `experiment/` の Python を触った場合:
  - `compileall` を必須
  - 可能なら対象スクリプトを限定実行
- `CLAUDE.md` / `.claude/` / `.github/` だけを触った場合:
  - 文面整合性の確認を行う
- 推論・モデル関連を触った場合:
  - モデルファイルがあれば対象スクリプトの限定確認を行う
  - 実行しない場合は PR に理由を書く

## 結果報告

通過したものを明示します。例:

```text
OK: python3 -m compileall src experiment
SKIP: inference test (model weights not available in this environment)
```
