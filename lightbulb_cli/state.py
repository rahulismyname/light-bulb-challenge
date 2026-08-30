from dataclasses import dataclass


@dataclass(frozen=True)
class LightBulbState:
    is_on: bool
    brightness: float
