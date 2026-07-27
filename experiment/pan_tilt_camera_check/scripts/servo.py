"""パン・チルトサーボの共通制御ロジック。

GPIO割り当て・可動域の定義は .claude/rules/hardware.md を参照。
"""
from __future__ import annotations

from gpiozero import AngularServo


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


class PanTilt:
    """パン(水平)・チルト(垂直)2軸サーボをまとめて扱うクラス。

    角度は config (`horizontal`/`vertical` の min_angle/max_angle) の
    可動域内にクランプしてから反映する（機構保護のため）。
    """

    def __init__(self, servo_config: dict) -> None:
        self._config = servo_config
        self.pan = build_servo(servo_config["horizontal"])
        self.tilt = build_servo(servo_config["vertical"])

    def move_to(self, pan_angle: float, tilt_angle: float) -> tuple[float, float]:
        pan_angle = clamp(
            pan_angle,
            self._config["horizontal"]["min_angle"],
            self._config["horizontal"]["max_angle"],
        )
        tilt_angle = clamp(
            tilt_angle,
            self._config["vertical"]["min_angle"],
            self._config["vertical"]["max_angle"],
        )
        self.pan.angle = pan_angle
        self.tilt.angle = tilt_angle
        return pan_angle, tilt_angle

    def detach(self) -> None:
        # PWM保持中のサーボの微振動（ハンチング）を防ぐため、PWM出力を止める
        self.pan.detach()
        self.tilt.detach()

    def close(self) -> None:
        self.pan.close()
        self.tilt.close()

    def __enter__(self) -> PanTilt:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()
