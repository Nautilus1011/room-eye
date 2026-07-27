# 🧪 パン・チルト + カメラ 動作確認

## 📌 1. 目的 (Objective)
* [x] サーボモータ2軸（パン・チルト）とラズパイ純正カメラを組み合わせ、GPIO 制御・撮影・
  カメラの取り付け向き補正（180度回転）が実機で問題なく動作するかを確認する。
* **背景**: room-eye では最終的にカメラによる自動追尾（トラッキング）を実現したい。その前段として、
  `.claude/rules/hardware.md` に定めた GPIO 割当（GPIO14=パン, GPIO15=チルト）・可動域・カメラ取り付け
  向きの前提が実機のハードウェア単体で成立するかを、追尾ロジックを組み込む前に確認しておく必要がある。

## ⚙️ 2. 実験条件 (Setup & Hyperparameters)
> **環境**: Raspberry Pi 実機（Raspberry Pi OS）/ Python 3.13 / `venv/room-eye`（`--system-site-packages`）
> 依存パッケージは `requirements-rpi.txt` を参照。GPIO・カメラ制御は Docker 開発コンテナ（`dev` サービス）
> では動作しないため、実機の venv から直接実行する。

```bash
sudo apt install -y python3-gpiozero python3-picamera2 python3-yaml

# リポジトリルートで実行
python3 -m venv --system-site-packages venv/room-eye
source venv/room-eye/bin/activate
```

サーボの信号線は GPIO14（パン）/ GPIO15（チルト）に接続。UART を有効化していると GPIO14/15 が
競合するため、事前に `raspi-config` 等でシリアルコンソールを無効化しておく必要がある。

| カテゴリ | パラメータ名 | 設定値 | 意図・備考 |
| :--- | :--- | :--- | :--- |
| **Hardware** | 水平軸（パン） | GPIO14 | `.claude/rules/hardware.md` の可動域定義（-90°〜+90°）に準拠 |
| **Hardware** | 垂直軸（チルト） | GPIO15 | 同上（0°〜90°） |
| **Config** | `config/servo_camera_check.yaml` | - | サーボ可動域・パルス幅・撮影解像度 |
| **Config** | `config/pan_tilt_explore.yaml` | `waypoints` | 撮影する pan/tilt の組み合わせを定義 |
| **Control** | `settle_wait_sec` | `1.5`（`pan_tilt_explore.yaml`） | 角度指定後、機構の揺れを収めるための待機 |
| **Control** | `hold_release_wait_sec` | `0.5`（`pan_tilt_explore.yaml`） | `detach()` で PWM 保持解除後の待機（微振動対策） |

実行したスクリプト:

```bash
cd experiment/pan_tilt_camera_check

# サーボ可動域の確認（servo_control.py, config/servo_camera_check.yaml を使用）
python3 scripts/servo_control.py                              # 両軸スイープ
python3 scripts/servo_control.py --axis horizontal             # 片軸のみ
python3 scripts/servo_control.py --axis horizontal --angle 30   # 指定角度

# 静止画撮影（capture_photo.py, config/servo_camera_check.yaml を使用）
python3 scripts/capture_photo.py
python3 scripts/capture_photo.py --count 3

# 複数姿勢での周囲撮影（explore.py, config/pan_tilt_explore.yaml を使用）
python3 scripts/explore.py
```

## 📊 3. 実験結果 (Results)
* **主要な確認結果**:
  * サーボ（`servo_control.py`）: 水平・垂直軸とも可動域内でのスイープ動作を確認。実行時に
    `PWMSoftwareFallback` の警告が発生するが、動作自体に支障はない ⚠️
  * カメラ（`capture_photo.py`）: 静止画の撮影・`outputs/servo_camera_check/` への保存を確認
  * 複数姿勢撮影（`explore.py`）: PWM 保持中の微振動によりブレが発生することを確認 ⚠️。
    角度指定後に `settle_wait_sec` 待機 → `detach()` で PWM 保持解除 → `hold_release_wait_sec`
    待機、という3ステップを導入することでブレを抑制できることを確認
  * 暗所では露出時間が伸びる分、わずかな振動でもブレが目立ちやすい傾向を確認
    （`settle_wait_sec` / `hold_release_wait_sec` を伸ばすことで軽減する想定だが、定量計測は未実施）
* **ログ/出力（一部抜粋）**:
  ```text
  [WARN] PWMSoftwareFallback: falling back to software PWM
  ```
* **実行できなかった検証**: `PWMSoftwareFallback` の警告に対して `pigpiod` を起動し
  `gpiozero` の pin factory を `pigpio` に切り替える改善案は、今回は未検証（対策候補として記録のみ）。
  また、ブレ量・角度精度などの定量的な計測は行っていない（目視での動作確認にとどまる）。

## 💡 4. 考察とネクストアクション (Discussion & Next Steps)
### 🧐 考察 (Why?)
1. **サーボの微振動**: ソフトウェア PWM フォールバックにより PWM 保持中の微振動が発生し、
   複数姿勢撮影時のブレの主因になっていると考えられる。
2. **静止→保持解除→待機の3ステップが有効**: `detach()` による PWM 保持解除を挟むことで、
   保持継続時よりも撮影時の振動要因を減らせている（目視ベースの確認）。
3. **暗所でのブレ感度**: 露出時間が伸びる分、同じ振動量でも画像上のブレが目立ちやすくなる。

### 🚀 ネクストアクション (Next)
* [ ] `pigpiod` + `gpiozero` の pin factory を `pigpio` に切り替え、`PWMSoftwareFallback`
      警告とブレへの影響を検証する。
* [ ] ブレ量・角度再現精度を定量的に計測できる方法を検討し、`settle_wait_sec` /
      `hold_release_wait_sec` のチューニングを数値ベースで行えるようにする。
* [ ] ハードウェア単体の動作確認が完了した前提で、自動追尾（トラッキング）ロジックの実験に進む。

### 🔧 追記: カメラ・サーボ制御の共通化

`capture_photo.py` / `servo_control.py` / `explore.py` で重複していたサーボ生成・可動域クランプ・
Picamera2 のライフサイクル管理を `scripts/servo.py`（`build_servo` / `clamp` / `PanTilt`）と
`scripts/camera.py`（`PanTiltCamera`）に切り出した。各スクリプトは config 読み込みと CLI 引数
処理のみを担う薄い層とし、将来 `src/room_eye/` へ移植する際にこの2モジュールをそのまま
移動できる形にしている。動作確認は本項の実験結果と同じ手順（実機での撮影・サーボスイープ・
複数姿勢撮影）を再実行し、リファクタ前と同じ挙動になることを目視で確認予定（未実施の場合は
PR の `## 補足情報` に理由を記載する）。
