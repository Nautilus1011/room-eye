"""GPIO14(水平)・GPIO15(垂直) サーボモータの動作確認スクリプト。"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

import yaml
from gpiozero import AngularServo

from servo import build_servo

CONFIG_PATH = Path(__file__).parent.parent / "config" / "servo_camera_check.yaml"


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def sweep(servo: AngularServo, min_angle: float, max_angle: float, step_deg: float, wait_sec: float) -> None:
    forward = list(range(int(min_angle), int(max_angle) + 1, int(step_deg)))
    angles = forward + forward[-2::-1]  # 端まで動かして往復させる
    for angle in angles:
        servo.angle = angle
        print(f"  angle -> {angle}")
        time.sleep(wait_sec)


def main() -> None:
    parser = argparse.ArgumentParser(description="GPIO14/15 サーボモータ動作確認スクリプト")
    parser.add_argument("--axis", choices=["horizontal", "vertical", "both"], default="both")
    parser.add_argument("--angle", type=float, default=None, help="指定角度に一度だけ動かす。未指定ならスイープ動作で確認する")
    args = parser.parse_args()

    config = load_config()["servo"]
    axes = ["horizontal", "vertical"] if args.axis == "both" else [args.axis]
    servos = {axis: build_servo(config[axis]) for axis in axes}

    try:
        for axis, servo in servos.items():
            print(f"[{axis}] GPIO{config[axis]['gpio_pin']} を動作確認します")
            if args.angle is not None:
                servo.angle = args.angle
                time.sleep(config["sweep_wait_sec"])
            else:
                sweep(
                    servo,
                    config[axis]["min_angle"],
                    config[axis]["max_angle"],
                    config["sweep_step_deg"],
                    config["sweep_wait_sec"],
                )
            servo.detach()  # PWM信号を止めてサーボの微振動を防ぐ
    finally:
        for servo in servos.values():
            servo.close()


if __name__ == "__main__":
    main()
