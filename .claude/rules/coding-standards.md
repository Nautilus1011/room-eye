# Python Coding Standards — room-eye

## 基本方針

- インデントは 4 スペース（Tab 禁止）
- 命名規則:
  - クラス名: `PascalCase`
  - 関数・変数・モジュール名: `snake_case`
  - 定数: `UPPER_SNAKE_CASE`
- コメントは WHY が自明でない場合のみ書く。WHAT を説明するコメントは不要。
- 新規コードでは型ヒントを推奨する

---

## 型ヒント

- 新規ファイルでは `from __future__ import annotations` を冒頭に記述する。
- 公開関数には引数と戻り値の型ヒントを付ける。

```python
from __future__ import annotations

import numpy as np


def preprocess_frame(frame: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """フレームを指定サイズにリサイズして返す。"""
    import cv2
    return cv2.resize(frame, size)
```

---

## 設定とパス

- パス・閾値・モデルパスをコードに直書きしない。`config/*.yaml` に逃がす。
- 新規コードでは絶対パスを増やさない。

---

## 依存関係

- ルートの `requirements-dev.txt` を標準入口とする。

---

## テストと検証

| 検証種別 | 手段 | 条件 |
|---|---|---|
| 構文チェック | `python3 -m compileall src experiment` | 常に実施 |
| 軽量スクリプト | 対象ファイルを個別実行 | 環境が揃う場合 |
| 推論テスト | Notebook または対象スクリプト | モデル・データが揃う場合のみ |

- 実行できなかった検証は隠さず、PR の `## 補足情報` に理由を明記する。
