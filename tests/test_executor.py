import contextlib
import io
import unittest

from light_bulb import LightBulb
from lightbulb_cli.commands import (
    AdjustBrightness,
    SetBrightness,
    Toggle,
    TurnOff,
    TurnOn,
    Unknown,
)
from lightbulb_cli.executor import execute


def _captured_stdout(bulb, command) -> str:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        execute(bulb, command)
    return buf.getvalue()


class TestOnOffToggle(unittest.TestCase):
    def test_turn_on(self):
        bulb = LightBulb()
        execute(bulb, TurnOn())
        self.assertTrue(bulb.is_on)

    def test_turn_off(self):
        bulb = LightBulb()
        bulb.is_on = True
        execute(bulb, TurnOff())
        self.assertFalse(bulb.is_on)

    def test_toggle_from_off(self):
        bulb = LightBulb()
        bulb.is_on = False
        execute(bulb, Toggle())
        self.assertTrue(bulb.is_on)

    def test_toggle_from_on(self):
        bulb = LightBulb()
        bulb.is_on = True
        execute(bulb, Toggle())
        self.assertFalse(bulb.is_on)


class TestSetBrightness(unittest.TestCase):
    def test_absolute_value(self):
        bulb = LightBulb()
        execute(bulb, SetBrightness(value=0.7))
        self.assertEqual(bulb.brightness, 0.7)

    def test_clamps_above_one(self):
        bulb = LightBulb()
        execute(bulb, SetBrightness(value=1.5))
        self.assertEqual(bulb.brightness, 1.0)

    def test_clamps_below_zero(self):
        bulb = LightBulb()
        execute(bulb, SetBrightness(value=-0.3))
        self.assertEqual(bulb.brightness, 0.0)


class TestAdjustBrightness(unittest.TestCase):
    def test_decrease_from_full(self):
        bulb = LightBulb()  # starts at 1.0
        out = _captured_stdout(bulb, AdjustBrightness(delta=-0.20))
        self.assertEqual(bulb.brightness, 0.8)
        self.assertIn("80%", out)

    def test_handles_float_drift(self):
        """0.7 - 0.2 == 0.49999999999999994 in raw floating point, which
        would make LightBulb's own int(value * 100) print 49% instead of
        50% if we didn't round before calling it."""
        bulb = LightBulb()
        bulb.brightness = 0.7
        out = _captured_stdout(bulb, AdjustBrightness(delta=-0.2))
        self.assertEqual(bulb.brightness, 0.5)
        self.assertIn("50%", out)

    def test_clamps_to_range(self):
        bulb = LightBulb()
        bulb.brightness = 0.1
        execute(bulb, AdjustBrightness(delta=-0.5))
        self.assertEqual(bulb.brightness, 0.0)

        bulb.brightness = 0.9
        execute(bulb, AdjustBrightness(delta=0.5))
        self.assertEqual(bulb.brightness, 1.0)


class TestUnknownCommand(unittest.TestCase):
    def test_does_not_touch_bulb_and_explains_itself(self):
        bulb = LightBulb()
        original_state = (bulb.is_on, bulb.brightness)
        out = _captured_stdout(
            bulb, Unknown(raw_text="make me a sandwich", reason="not a bulb command")
        )
        self.assertEqual((bulb.is_on, bulb.brightness), original_state)
        self.assertIn("make me a sandwich", out)


if __name__ == "__main__":
    unittest.main()
