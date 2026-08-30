from light_bulb import LightBulb
from lightbulb_cli.commands import (
    AdjustBrightness,
    Command,
    SetBrightness,
    Toggle,
    TurnOff,
    TurnOn,
    Unknown,
)


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def execute(bulb: LightBulb, command: Command) -> None:
    if isinstance(command, TurnOn):
        bulb.turn_on()

    elif isinstance(command, TurnOff):
        bulb.turn_off()

    elif isinstance(command, Toggle):
        bulb.turn_off() if bulb.is_on else bulb.turn_on()

    elif isinstance(command, SetBrightness):
        bulb.set_brightness(round(_clamp(command.value), 2))

    elif isinstance(command, AdjustBrightness):
        new_value = _clamp(bulb.brightness + command.delta)
        bulb.set_brightness(round(new_value, 2)) # Rounded it into 2 to avoid rounding the float that migth loose a percent

    elif isinstance(command, Unknown):
        detail = f" ({command.reason})" if command.reason else ""
        print(f"Sorry, I didn't understand: \"{command.raw_text}\"{detail}.")

    else:  # pragma: no cover - guards against forgetting a branch
        raise TypeError(f"Unhandled command type: {command!r}")
