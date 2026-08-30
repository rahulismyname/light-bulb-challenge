from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class TurnOn:
    """Switch the bulb on."""


@dataclass(frozen=True)
class TurnOff:
    """Switch the bulb off."""


@dataclass(frozen=True)
class Toggle:
    """Toggle the bulb to the opposite of its current on/off state."""


@dataclass(frozen=True)
class SetBrightness:
    """Set brightness to an absolute value.
    value: float in [0.0, 1.0], matching LightBulb.set_brightness's contract.
    """

    value: float


@dataclass(frozen=True)
class AdjustBrightness:
    """Change brightness relative to whatever it currently is.

    delta: float in [-1.0, 1.0] (percentage points / 100), e.g. -0.20 for
    "reduce brightness by 20%". The executor is responsible for clamping the
    resulting value to [0.0, 1.0].
    """

    delta: float


@dataclass(frozen=True)
class Unknown:
    """The parser could not confidently map the input to a bulb action."""
    raw_text: str
    reason: str = ""


Command = Union[TurnOn, TurnOff, Toggle, SetBrightness, AdjustBrightness, Unknown]
