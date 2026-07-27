"""ラズパイ純正カメラの共通撮影ロジック。

カメラの取り付け向き（180度回転）補正の前提は .claude/rules/hardware.md を参照。
"""
from __future__ import annotations

from pathlib import Path

from libcamera import Transform
from picamera2 import Picamera2


class PanTiltCamera:
    """Picamera2 のライフサイクルと180度回転補正をまとめて扱うクラス。"""

    def __init__(self, resolution: tuple[int, int], rotate_180: bool) -> None:
        # 配線の都合でカメラが物理的に180度回転して取り付けられているための補正
        transform = Transform(hflip=1, vflip=1) if rotate_180 else Transform()

        self._picam2 = Picamera2()
        still_config = self._picam2.create_still_configuration(
            main={"size": tuple(resolution)}, transform=transform
        )
        self._picam2.configure(still_config)
        self._picam2.start()

    def capture(self, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self._picam2.capture_file(str(output_path))
        return output_path

    def close(self) -> None:
        self._picam2.stop()
        self._picam2.close()

    def __enter__(self) -> PanTiltCamera:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
