# ジェスチャー認識 調査

ハンドサインによるデバイス制御に関する論文・ブログ・実装事例をまとめる。

> 関連 Issue: [#11 調査: ジェスチャー認識の先行研究・実装事例](https://github.com/Nautilus1011/room-eye/issues/11)

## 調査方針

ラズパイ（ARM64 CPU のみ）でリアルタイム動作する手法を優先して調査した。本プロジェクトで想定する用途は「PC の Wake on LAN」「扇風機」「照明」を切り替える程度の少数クラスのハンドサイン認識であり、高精度な連続手話認識までは不要という前提で事例を絞った。

## 論文・関連研究

| タイトル | 概要 | リンク |
|---|---|---|
| Smart Home Control Using Real-Time Hand Gesture Recognition and AI on Raspberry Pi 5（MDPI Electronics, 2025） | Raspberry Pi 5 + Camera Module v2 上で MediaPipe によりランドマークを抽出し、5 層の全結合層（Keras 3 → TFLite 変換）で分類。HaGRIDv2 データセットを片手 15 クラスに絞って学習し、検証精度 0.90 / 平均 20.4 FPS を達成。本プロジェクトのユースケース（少数クラスのハンドサイン→家電制御）に最も近い先行研究。 | [MDPI](https://www.mdpi.com/2079-9292/14/20/3976) |
| Improving Gesture Recognition Efficiency with MediaPipe and YOLO-Pose（ISPRS Archives, 2025） | MediaPipe で手のスケルトンを高速抽出し、YOLO-Pose で文脈・位置情報を補完するハイブリッド構成を提案。単体より計算コストは増えるが、雑然とした背景での頑健性が向上。 | [ISPRS PDF](https://isprs-archives.copernicus.org/articles/XLVIII-2-W9-2025/13/2025/isprs-archives-XLVIII-2-W9-2025-13-2025.pdf) |
| Comparative Evaluation of MediaPipe and YOLOv8 for Real-Time Pose Estimation | 姿勢・ジェスチャー認識タスクにおいて MediaPipe ベースのキーポイント検出が YOLOv8 より高精度になるケースが多く、YOLOv8 は計算資源要求が大きくジェスチャー認識には不向きと結論。CPU オンリー環境での採用判断の根拠として有用。 | [ResearchGate](https://www.researchgate.net/publication/399353653_Comparative_Evaluation_of_MediaPipe_and_YOLOv8_for_Real-Time_Pose_Estimation) |
| Person-Independent Hand Gesture Recognition Using MediaPipe and Multi-layer Perceptron（Springer） | MediaPipe ランドマーク + MLP という軽量構成で、話者非依存（person-independent）の認識精度を検証。 | [Springer](https://link.springer.com/chapter/10.1007/978-981-96-1348-9_1) |
| Hand Gesture Recognition Using MediaPipe Landmarks and Deep Learning Networks（SciTePress, 2025） | MediaPipe ランドマーク抽出 + 深層学習分類器の一般的なアーキテクチャを整理したサーベイ寄りの論文。 | [SciTePress PDF](https://www.scitepress.org/Papers/2025/130535/130535.pdf) |

## 個人ブログ・OSS 実装事例

| プロジェクト | 概要 | ラズパイでの実績 | リンク |
|---|---|---|---|
| Kazuhito00 / hand-gesture-recognition-using-mediapipe | MediaPipe Hands のランドマークを、簡易な MLP で分類してハンドサイン（パー/グー/指差し）とフィンガージェスチャー（静止/時計回り/反時計回り/移動）を認識する定番実装。学習データの追加・再学習の手順も整備されている。 | README に実機ベンチマークの明記はないが、ランドマーク抽出＋軽量 MLP という構成自体が Pi CPU 向き。 | [GitHub](https://github.com/Kazuhito00/hand-gesture-recognition-using-mediapipe) |
| BlurryFace04 / LazyLights | **Raspberry Pi 4B** ベースのホームオートメーション。OpenCV + MediaPipe でジェスチャーを認識し、Flask 経由でリレー制御。照明（2系統）・扇風機・コンセントを操作でき、本プロジェクトの目的（照明・扇風機制御）と直接一致するユースケース。音声・Web・キーボードなど他の操作系統も同居。 | Pi 4B での稼働実績あり（具体的な FPS 記載なし）。 | [GitHub](https://github.com/BlurryFace04/LazyLights) |
| mar5chi / hand_gesture_control | Raspberry Pi + OAK-D（Luxonis、depthai）でハンドジェスチャーによる家電制御。ランドマーク推論を OAK-D 側の VPU にオフロードすることで Pi CPU の負荷を回避するアプローチ。 | 専用デバイス（OAK-D）依存のため Pi CPU 単体の参考値にはならないが、「CPU オフロード」という選択肢として記録。 | [GitHub](https://github.com/mar5chi/hand_gesture_control) |
| google-ai-edge / mediapipe-samples（gesture_recognizer/raspberry_pi） | Google 公式の MediaPipe Gesture Recognizer タスクの Raspberry Pi 向けサンプル実装。ビルトインの 7 ジェスチャー（Thumb_Up/Down, Open_Palm, Closed_Fist, Victory, ILoveYou, Pointing_Up）に加え、転移学習によるカスタムジェスチャー追加も公式にサポート。 | 公式サンプルとして動作確認済み。 | [GitHub](https://github.com/google-ai-edge/mediapipe-samples/tree/main/examples/gesture_recognizer/raspberry_pi) |
| Random Nerd Tutorials: Install MediaPipe on a Raspberry Pi | Raspberry Pi への MediaPipe セットアップ手順（ビルド済み wheel の利用など）を解説。環境構築の参考。 | セットアップ手順のみ、性能記載なし。 | [記事](https://randomnerdtutorials.com/install-mediapipe-raspberry-pi/) |
| amitbhorania / Home-Automation-Using-Hand-Gesture | カメラではなく ADXL345 加速度センサ（ウェアラブル）でジェスチャーを検出する方式。カメラ方式とは異なるアプローチとして参考記録。 | センサ方式のため映像処理の負荷なし（本プロジェクトの前提とは異なる）。 | [GitHub](https://github.com/amitbhorania/Home-Automation-Using-Hand-Gesture) |

## 推論速度の参考値（CPU オンリー）

未計測・二次情報のため参考値として記載。本採用前に本プロジェクト環境で実測が必要（[cv-research.md](../../../.claude/rules/cv-research.md) 準拠）。

| 環境 | 構成 | 速度 | 出典 |
|---|---|---|---|
| Raspberry Pi 4（Cortex-A72, CPU only） | MediaPipe Hands, `max_num_hands=1` | 約 14 FPS（2 手同時は約 8 FPS） | 検索結果（一次情報未特定、要検証） |
| Raspberry Pi 4B（4GB, CPU only） | MediaPipe Hands | 1 フレーム約 220ms（≒4.5 FPS、設定により変動） | 検索結果（一次情報未特定、要検証） |
| Raspberry Pi 5 | MediaPipe ランドマーク抽出 + 5 層 FFN（TFLite） | 平均 20.4 FPS、検証精度 0.90 | [MDPI 論文](https://www.mdpi.com/2079-9292/14/20/3976) |

Pi 4 系の数値は出典ページの二次情報であり幅（4.5〜14 FPS）があるため、そのまま採用可否の判断根拠にはできない。実機での計測が必須。

## 利用ライブラリ・モデルの候補整理

| 候補 | メリット | デメリット・注意点 |
|---|---|---|
| **MediaPipe Hands / Tasks API（HandLandmarker・GestureRecognizer）** | GPU 不要でランドマーク抽出が軽量。公式に Raspberry Pi 向けサンプルあり。ビルトインジェスチャーに加え転移学習でのカスタムジェスチャー追加も公式サポート。OSS 事例（Kazuhito00 等）が豊富で実装難易度が低い。 | ジェスチャー分類自体は別途 MLP 等の追加実装が必要な場合がある（ビルトイン以外のジェスチャーを使う場合）。 |
| **YOLO Pose（YOLOv8/v11-pose 等）** | 物体検出とキーポイント推定を単一モデルで行える。手だけでなく人物全体の姿勢や複数人物の同時検出に強い。ONNX エクスポート可。 | CPU 環境ではランドマーク推定精度・速度ともに MediaPipe に劣るとの報告あり。単純なハンドサイン認識用途には過剰スペックになりやすい。 |
| **MediaPipe ランドマーク + 独自軽量分類器（MLP / 全結合層）** | Kazuhito00 実装・MDPI 論文の両方で採用されている構成。学習データさえ揃えれば自前のジェスチャークラス（Wake on LAN 用サイン等）を追加しやすい。TFLite 化すればラズパイでの推論も軽量。 | 学習データ収集・アノテーションのコストが発生する。 |

## 推奨方針（暫定）

1. まずは **MediaPipe Hands（Tasks API）でランドマーク抽出 → 軽量 MLP で自作ジェスチャー分類** の構成（Kazuhito00 実装・MDPI 論文と同系統）を第一候補とする。GPU 不要・公式 Pi サンプルあり・OSS 実装が豊富という点で、`cv-research.md` の「まず CPU での推論速度を計測してから採用を判断する」という方針に沿って着手しやすい。
2. YOLO Pose は「手だけでなく物体検出（コップ・ペットボトル等）と統合したい」場合の将来オプションとして保留する。現状の比較調査では、単純なハンドサイン識別用途では MediaPipe 単体の方が CPU 適性が高いと判断できる。
3. 次のアクションとして、本プロジェクトの Raspberry Pi 実機（または相当の ARM64 CPU 環境）で MediaPipe Hands の FPS を実測し、上表の参考値と比較する（別 Issue で追跡）。
