"""ラズパイ純正カメラでの静止画撮影確認スクリプト。"""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

import yaml
from libcamera import Transform
from picamera2 import Picamera2

CONFIG_PATH = Path(__file__).parent.parent / "config" / "servo_camera_check.yaml"
REPO_ROOT = Path(__file__).resolve().parents[3]


def load_config() -> dict:
    with CONFIG_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def capture(output_dir: Path, prefix: str, resolution: tuple[int, int], rotate_180: bool) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"{prefix}_{timestamp}.jpg"

    # 配線の都合でカメラが物理的に180度回転して取り付けられているための補正
    # (.claude/rules/hardware.md 参照)
    transform = Transform(hflip=1, vflip=1) if rotate_180 else Transform()

    picam2 = Picamera2()
    still_config = picam2.create_still_configuration(main={"size": tuple(resolution)}, transform=transform)
    picam2.configure(still_config)
    picam2.start()
    picam2.capture_file(str(output_path))
    picam2.stop()
    picam2.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="ラズパイ純正カメラ動作確認スクリプト")
    parser.add_argument("--count", type=int, default=1, help="撮影枚数")
    args = parser.parse_args()

    config = load_config()["camera"]
    output_dir = REPO_ROOT / config["output_dir"]

    for i in range(args.count):
        output_path = capture(
            output_dir,
            config["filename_prefix"],
            config["resolution"],
            config.get("rotate_180", False),
        )
        print(f"[{i + 1}/{args.count}] saved -> {output_path}")


if __name__ == "__main__":
    main()
