---
作成日: 2026-08-11
最終更新: 2026-08-11
ステータス: active
---

# エッジ推論の方針 — ラズパイ CPU での物体検出

ラズパイ（ARM64・CPU のみ）で人・犬の追尾に使える物体検出を成立させるための、
モデル・ランタイム・パイプライン構成の方針。

**本文書は机上調査の結果であり、実測値ではない。** 実機での計測は Phase 1（`../roadmap.md`）で行う。
数値はすべて出典に基づく公開値・報告値であり、本プロジェクトの環境で再現することを保証しない。

追尾側の要件は `../plans/auto-tracking.md`、C++ 移植の制約は `cpp-migration.md` を参照。

## 前提

`../plans/auto-tracking.md` で確定した要件のうち、本文書のスコープを決めるもの。

| 要件 | 調査への影響 |
| :--- | :--- |
| 追尾対象は人（`person`）と犬（`dog`） | どちらも COCO 標準クラス。追加学習・独自データセットは対象外 |
| 個体識別は行わない | 再識別（ReID）系の手法は対象外 |
| 追うのは常に 1 体 | 多対象トラッキングは不要 |
| 明るい部屋のみ | 低照度向けの前処理・暗所特化モデルは対象外 |
| 最終的に C/C++ で運用する | C++ API が成熟していないランタイムは減点 |

## ライセンス

ライセンスは制約条件から外した。[ADR-0003](../adr/0003-agpl-license.md) でリポジトリを
AGPL-3.0 に変更したため、下表のどのモデルを選んでも整合する。

### モデル

| モデル | ライセンス |
| :--- | :--- |
| YOLO26 / YOLO11 / YOLOv8（Ultralytics） | AGPL-3.0 |
| YOLOv5 / v7 / v9 | GPL-3.0 系 |
| NanoDet / NanoDet-Plus（RangiLyu 本家） | Apache-2.0 |
| YOLOX（Megvii） | Apache-2.0 |
| PP-PicoDet（PaddleDetection） | Apache-2.0 |
| RTMDet（MMDetection 版） | Apache-2.0 |
| RTMDet（MMYOLO 版） | GPL-3.0 |

⚠️ 同名のモデルでも配布元によってライセンスが異なる。RTMDet は MMDetection 版が Apache-2.0、
MMYOLO 版が GPL-3.0。NanoDet も第三者のサンプル実装リポジトリは別ライセンスの場合がある。
**必ず本家リポジトリの `LICENSE` を確認する。**

### ランタイム

| ランタイム | ライセンス |
| :--- | :--- |
| NCNN（Tencent） | BSD-3-Clause |
| ONNX Runtime（Microsoft） | MIT |
| TFLite | Apache-2.0 |

ランタイム軸には制約がない。**モデル軸とランタイム軸は独立に選べる。**

### Ultralytics 系を採用する場合の注意

Ultralytics は AGPL-3.0 の適用範囲を「学習コードと、そのコードが生成したモデル」としている。
**ONNX / NCNN にエクスポートしても AGPL は外れない。** また Enterprise ライセンスが必要な用途として
「hardware, edge devices, robotics, cameras, or appliances」を明示しており、本プロジェクトの
用途はこれに該当する。AGPL-3.0 のもとで運用する限り問題ないが、商用化する場合は再検討が必要。

**非対称性**: Apache-2.0 のモデルを選べば将来の選択肢が広い。同等性能なら permissive 側を採る。

## モデル候補

| モデル | 特徴 |
| :--- | :--- |
| **YOLO26n** | NMS 不要（End-to-End NMS-Free）の設計。後処理時間が削減されるうえ、**推論時間が検出数に左右されず予測可能になる**。制御ループのむだ時間が安定する点で追尾と相性が良い |
| **YOLO11n** | パラメータ数を抑えつつ精度を維持 |
| **NanoDet-Plus** | モバイル特化の超軽量モデル。速度は最有力だが全体 mAP は低め |
| **YOLOX-Nano / Tiny** | Apache-2.0。NCNN / ONNX / OpenVINO の公式エクスポートあり |
| **PP-PicoDet** | Apache-2.0。モバイル特化 |

### 報告されている推論時間（ラズパイ5・CPU）

| 構成 | 推論時間 |
| :--- | :--- |
| YOLO26n × NCNN | 約 67 ms |
| YOLO11n × ONNX Runtime | 約 126 ms |

⚠️ **いずれも「純粋な推論時間」であり、フレーム取得・前処理・後処理を含まない。**
制御ループのむだ時間に効くのはエンドツーエンド時間なので、この数値をそのまま FPS 換算してはいけない。

## ランタイム

| ランタイム | 評価 |
| :--- | :--- |
| **NCNN** | ARM 向けに高度に最適化されており、ラズパイでは最有力。**C++ ネイティブなので Phase 4 の移植と最も相性が良い** |
| **ONNX Runtime** | PyTorch 直実行より大幅に高速。C++ API あり |
| **TFLite + XNNPACK** | INT8 量子化モデルを使う場合に有効 |

## 目標値の仮置き

| 項目 | 仮の目標値 |
| :--- | :--- |
| 検出レート | 5〜10 FPS |
| 入力解像度 | 320×320（速度優先）/ 640×640（精度優先）の 2 水準で比較 |

⚠️ **この 5 FPS という数値の根拠には注意が必要。** 出典は「追尾アルゴリズム（ByteTrack 等）は
5 Hz の推論レートでも高精度な検出と組み合わせれば MOT 精度がほぼ最適」という報告だが、これは
**オフラインの追跡精度（軌跡が正しく繋がるか）の話であり、サーボの閉ループ制御の安定性とは別の指標**である。

5 FPS はむだ時間 200 ms に相当する。`../plans/auto-tracking.md` の「むだ時間が大きいと `Kp` を
上げられず発振する」という制約に直結する。**Phase 1 では「何 FPS 出せるか」を測り、
Phase 2 で「何 FPS 必要か」を決める**という分担にする。

## パイプラインの軽量化

### 検出の間引きと補間

推論が制御周期に対して遅い場合、毎フレーム検出せず、間のフレームを補間する。
補間の方式は 2 つあり、性質が異なる。

| 方式 | 内容 | 性質 |
| :--- | :--- | :--- |
| **視覚トラッカー** | KCF / CSRT / MOSSE 等。画像を見て対象を追う | 画像処理のコストがかかるが、対象の実際の動きに追従できる |
| **状態外挿** | カルマンフィルタ等で位置を予測する | 画像を見ないため極めて軽量。ただし予測が外れると誤差が蓄積する |

⚠️ **ByteTrack / MCDTrack はどちらも「補間」の手法ではない。** これらは検出結果どうしの
対応付け（association）を行う多対象トラッキング手法であり、検出を実行しなかったフレームの位置を
画像から求めるものではない。ByteTrack のカルマンフィルタによる外挿は上表の「状態外挿」として
使えるが、その用途で語られている数値ではない点に注意する。

参考として報告されているコスト（ラズパイ4B）:

| 手法 | コスト |
| :--- | :--- |
| ByteTrack | 約 4.22 ms/frame |
| MCDTrack | 約 2.53 ms/frame |

推論時間（67〜126 ms）に比べて 2 桁小さい。**「検出 1 回 + 補間 N フレーム」の構成は
コスト面では確実に成立する。** 問題は精度側（N をいくつまで伸ばせるか）であり、実測で決める。

**KCF / CSRT / MOSSE の ARM 上でのコストは未調査**。視覚トラッカーを採る場合は実測が必要。
なお OpenCV のトラッカーは C++ にも同じ実装があるため、移植性は損なわない（`cpp-migration.md`）。

### カメラ取得のコスト

⚠️ **最優先で実測すべき項目。** `picamera2` の `capture_array()` について、カメラ側の
エンコード / デコード処理だけで **~300 ms の遅延**が生じるリスクが報告されている。

これが事実なら、推論時間 67 ms の議論が意味を失う。**モデル比較より先にカメラ取得時間を測る。**
最も安く測れて、かつ全体設計をひっくり返し得る。

対策の候補:

- `picamera2` の低解像度ストリーム（lores）を使い、モデル入力サイズに近い解像度で直接取得する
- YUV420 → RGB の変換コストを避ける（モデル側で YUV を受けられないか検討する）
- キャプチャと推論を別スレッドに分離する

### 非同期化の注意点

キャプチャ・推論・トラッキングを別スレッド化すると FPS は向上するが、
**スレッド間のデータ受け渡しがレイテンシ（むだ時間）を増大させる**。

追尾では「スループット（FPS）」より「むだ時間」が制御の安定性を決めるため、
**FPS が上がってもむだ時間が伸びれば逆効果になり得る。** 両方を測って判断する。

### 推論スレッド数と PWM ジッタ

⚠️ **このプロジェクト固有の重要な制約。**

サーボはソフトウェア PWM で駆動しており、PWM 保持中の微振動が未解決の課題として残っている
（Phase H、`../plans/auto-tracking.md`）。推論スレッドが全コアを占有すると、OS のスケジューリング
遅延によって PWM のパルス生成が乱れ、**ジッタが悪化する**。

対策の候補:

- 推論スレッド数を 1〜2 に制限して CPU の余力を残す（FPS は下がる）
- 推論と PWM 制御のプロセス / スレッド優先度を分離する（nice 値等）
- PWM の生成自体を外部チップ（PCA9685）に逃がす → Phase H の選択肢 1 と同じ結論になる

**Phase H と Phase 1 は独立ではない。** 推論の CPU 負荷が PWM 品質に影響するため、
Phase 1 のベンチマークでは「サーボを動かしながら推論した場合」も測る必要がある。

## 実測（Phase 1 / #15）に向けた候補

机上調査の結論として、以下を実測候補とする。

| # | 構成 | 狙い |
| :--- | :--- | :--- |
| 1 | NanoDet-Plus × NCNN × 320 | 最高速。精度が足りるかを見る |
| 2 | YOLO26n × NCNN × 640 | NMS-free による安定したむだ時間 |
| 3 | YOLO11n × ONNX Runtime × 640 | 精度・安定性の基準。ONNX Runtime のベースライン |

**測定の順序**（依存関係があるため、この順で測る）:

1. **カメラ取得時間**（モデルに依存しない。ここが支配的なら以降の比較の意味が変わる）
2. 各構成のエンドツーエンド時間の内訳（取得 / 前処理 / 推論 / 後処理）
3. `person` / `dog` の検出率（自室の実環境で。`dog` は実測でしか分からない）
4. 推論スレッド数を変えた場合の速度と、サーボ動作時の PWM ジッタへの影響
5. 数分〜数十分の連続稼働での SoC 温度・サーマルスロットリング

## 未確定事項（TODO）

- [ ] **ラズパイの実機モデル**。`cat /proc/device-tree/model`。本文書の数値はラズパイ5 の報告値が中心で、
      Pi4 以前なら大幅に下振れする
- [ ] **`dog` クラスのクラス別 AP**。二次情報では見つからなかった。実測で判断する
- [ ] **KCF / CSRT / MOSSE の ARM 上でのコスト**。視覚トラッカーを採る場合に必要
- [ ] **INT8 量子化による精度低下の定量値**。速度向上とのトレードオフが未評価
- [ ] **能動冷却の要否**。ラズパイ5 で連続推論する場合はアクティブクーラーが必須との報告がある一方、
      5 分間の連続推論では FPS 低下は僅かとの報告もある。測定条件（冷却の有無）が不明

## 出典

- [Ultralytics License](https://www.ultralytics.com/license)
- [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics)
- [RangiLyu/nanodet — LICENSE](https://github.com/RangiLyu/nanodet/blob/main/LICENSE)
- [Megvii-BaseDetection/YOLOX — LICENSE](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/LICENSE)
- [PaddlePaddle/PaddleDetection](https://github.com/PaddlePaddle/PaddleDetection)
- [open-mmlab/mmdetection — LICENSE](https://github.com/open-mmlab/mmdetection/blob/main/LICENSE)
- [Tencent/ncnn — LICENSE](https://github.com/Tencent/ncnn/blob/master/LICENSE.txt)
- [microsoft/onnxruntime — LICENSE](https://github.com/microsoft/onnxruntime/blob/main/LICENSE)
- MCDTrack: Park et al., "Multi-Object Tracking on SWIR Images for City Surveillance in an
  Edge-Computing Environment", Sensors, 2023

ベンチマーク数値（推論時間・トラッカーコスト・持続性能）は外部の調査結果に基づく報告値であり、
一次情報の再確認は行っていない。**採用判断は Phase 1 の実測に基づいて行う。**
