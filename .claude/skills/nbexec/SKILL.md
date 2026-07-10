---
name: nbexec
description: "Docker の dev コンテナ内で任意の Jupyter notebook を実行し outputs/notebooks/ に保存する"
argument-hint: "<notebook_path> [--output <output_filename>] [--timeout <seconds>]"
---

# /nbexec

Docker の `dev` コンテナ内で指定した notebook を実行し、結果を `outputs/notebooks/` に保存する。

## 使い方

```text
/nbexec experiment/yolov5/infer-yolov5.ipynb
/nbexec experiment/yolov5/infer-yolov5.ipynb --output infer_result.ipynb
/nbexec experiment/yolov5/infer-yolov5.ipynb --timeout 900
```

## 手順

1. notebook パスと出力ファイル名を決める
2. `docker compose up -d dev` 済みであることを確認する
3. 以下を実行する

```bash
docker compose exec dev bash -lc "jupyter nbconvert \
  --to notebook \
  --execute \
  --ExecutePreprocessor.timeout=<timeout> \
  --output-dir outputs/notebooks \
  --output <output_name> \
  <notebook_path>"
```

4. 出力先 `outputs/notebooks/<output_name>` を報告する
5. エラー時は import エラーかカーネルエラーかを切り分ける

## 注意

- `outputs/notebooks/` はローカル管理のみ（Git に含めない）
- 長時間 notebook は `--timeout` を明示する（デフォルト 600 秒）
