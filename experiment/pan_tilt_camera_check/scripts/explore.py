"""パン・チルトサーボを可動域内で動かしながら撮影し、周囲を探索するスクリプト。

可動域・GPIO割り当ての定義は .claude/rules/hardware.md を参照。
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import yaml

from camera import PanTiltCamera
from servo import PanTilt

CONFIG_PATH = Path(__file__).parent.parent / "config" / "pan_tilt_explore.yaml"
REPO_ROOT = Path(__file__).resolve().parents[3]


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()
    servo_config = config["servo"]
    camera_config = config["camera"]

    output_dir = REPO_ROOT / camera_config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    with (
        PanTilt(servo_config) as pan_tilt,
        PanTiltCamera(camera_config["resolution"], camera_config.get("rotate_180", False)) as camera,
    ):
        for pan_angle, tilt_angle in config["waypoints"]:
            pan_angle, tilt_angle = pan_tilt.move_to(pan_angle, tilt_angle)
            time.sleep(servo_config["settle_wait_sec"])

            # PWM保持中のサーボの微振動（ハンチング）がブレの原因になるため、
            # 撮影直前に一度サーボを解放して完全に静止させてから撮る
            pan_tilt.detach()
            time.sleep(servo_config["hold_release_wait_sec"])

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{camera_config['filename_prefix']}_pan{pan_angle:g}_tilt{tilt_angle:g}_{timestamp}.jpg"
            output_path = output_dir / filename
            camera.capture(output_path)
            print(f"pan={pan_angle} tilt={tilt_angle} -> {output_path}")


if __name__ == "__main__":
    main()
