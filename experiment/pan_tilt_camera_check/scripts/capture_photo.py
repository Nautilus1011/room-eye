"""ラズパイ純正カメラでの静止画撮影確認スクリプト。"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import yaml

from camera import PanTiltCamera

CONFIG_PATH = Path(__file__).parent.parent / "config" / "servo_camera_check.yaml"
REPO_ROOT = Path(__file__).resolve().parents[3]


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> None:
    parser = argparse.ArgumentParser(description="ラズパイ純正カメラ動作確認スクリプト")
    parser.add_argument("--count", type=int, default=1, help="撮影枚数")
    args = parser.parse_args()

    config = load_config()["camera"]
    output_dir = REPO_ROOT / config["output_dir"]

    with PanTiltCamera(config["resolution"], config.get("rotate_180", False)) as camera:
        for i in range(args.count):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{config['filename_prefix']}_{timestamp}.jpg"
            camera.capture(output_path)
            print(f"[{i + 1}/{args.count}] saved -> {output_path}")


if __name__ == "__main__":
    main()
