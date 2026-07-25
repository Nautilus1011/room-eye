"""パン・チルトサーボを可動域内で動かしながら撮影し、周囲を探索するスクリプト。

可動域・GPIO割り当ての定義は .claude/rules/hardware.md を参照。
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import yaml
from gpiozero import AngularServo
from libcamera import Transform
from picamera2 import Picamera2

CONFIG_PATH = Path(__file__).parent.parent / "config" / "pan_tilt_explore.yaml"
REPO_ROOT = Path(__file__).resolve().parents[3]


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_servo(axis_config: dict) -> AngularServo:
    return AngularServo(
        axis_config["gpio_pin"],
        min_angle=axis_config["min_angle"],
        max_angle=axis_config["max_angle"],
        min_pulse_width=axis_config["min_pulse_width"],
        max_pulse_width=axis_config["max_pulse_width"],
    )


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def main() -> None:
    config = load_config()
    servo_config = config["servo"]
    camera_config = config["camera"]

    pan = build_servo(servo_config["horizontal"])
    tilt = build_servo(servo_config["vertical"])

    output_dir = REPO_ROOT / camera_config["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    transform = Transform(hflip=1, vflip=1) if camera_config.get("rotate_180", False) else Transform()
    picam2 = Picamera2()
    still_config = picam2.create_still_configuration(
        main={"size": tuple(camera_config["resolution"])}, transform=transform
    )
    picam2.configure(still_config)
    picam2.start()

    try:
        for pan_angle, tilt_angle in config["waypoints"]:
            pan_angle = clamp(
                pan_angle, servo_config["horizontal"]["min_angle"], servo_config["horizontal"]["max_angle"]
            )
            tilt_angle = clamp(
                tilt_angle, servo_config["vertical"]["min_angle"], servo_config["vertical"]["max_angle"]
            )

            pan.angle = pan_angle
            tilt.angle = tilt_angle
            time.sleep(servo_config["settle_wait_sec"])

            # PWM保持中のサーボの微振動（ハンチング）がブレの原因になるため、
            # 撮影直前に一度サーボを解放して完全に静止させてから撮る
            pan.detach()
            tilt.detach()
            time.sleep(servo_config["hold_release_wait_sec"])

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{camera_config['filename_prefix']}_pan{pan_angle:g}_tilt{tilt_angle:g}_{timestamp}.jpg"
            output_path = output_dir / filename
            picam2.capture_file(str(output_path))
            print(f"pan={pan_angle} tilt={tilt_angle} -> {output_path}")
    finally:
        picam2.stop()
        picam2.close()
        pan.close()
        tilt.close()


if __name__ == "__main__":
    main()
