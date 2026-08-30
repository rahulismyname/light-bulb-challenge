import unittest

from lightbulb_cli.commands import (
    AdjustBrightness,
    SetBrightness,
    Toggle,
    TurnOff,
    TurnOn,
    Unknown,
)
from lightbulb_cli.state import LightBulbState

try:
    from lightbulb_cli.parsers.spacy_parser import SpacyParser, SpacyParserError
except ImportError:
    SpacyParser = None
    SpacyParserError = Exception


def _state(is_on: bool = False, brightness: float = 1.0) -> LightBulbState:
    return LightBulbState(is_on=is_on, brightness=brightness)


class SpacyParserTestCase(unittest.TestCase):
    """Base class that loads the spaCy pipeline once, skipping if unavailable."""

    parser: "SpacyParser"

    @classmethod
    def setUpClass(cls):
        if SpacyParser is None:
            raise unittest.SkipTest("spacy is not installed")
        try:
            cls.parser = SpacyParser()
        except SpacyParserError as exc:
            raise unittest.SkipTest(str(exc))


class TestOnOff(SpacyParserTestCase):
    def test_turn_on(self):
        cmd = self.parser.parse("Please turn the light on", _state())
        self.assertIsInstance(cmd, TurnOn)

    def test_turn_off(self):
        cmd = self.parser.parse("Now please turn it off", _state(is_on=True))
        self.assertIsInstance(cmd, TurnOff)

    def test_on_with_instead_of_off_distractor(self):
        cmd = self.parser.parse("Switch it back on instead of off", _state())
        self.assertIsInstance(cmd, TurnOn)

    def test_case_insensitive(self):
        cmd = self.parser.parse("PLEASE TURN THE LIGHT ON", _state())
        self.assertIsInstance(cmd, TurnOn)

    def test_toggle_keyword(self):
        cmd = self.parser.parse("Toggle the light", _state())
        self.assertIsInstance(cmd, Toggle)

    def test_flip_keyword(self):
        cmd = self.parser.parse("Flip the switch", _state())
        self.assertIsInstance(cmd, Toggle)


class TestAbsoluteBrightness(SpacyParserTestCase):
    def test_set_to_70_percent(self):
        cmd = self.parser.parse("Please set the brightness to 70%", _state())
        self.assertIsInstance(cmd, SetBrightness)
        self.assertAlmostEqual(cmd.value, 0.70)

    def test_set_with_instead_of_distractor(self):
        cmd = self.parser.parse("Now set it to 10% instead of 70%", _state())
        self.assertIsInstance(cmd, SetBrightness)
        self.assertAlmostEqual(cmd.value, 0.10)

    def test_spelled_out_percent(self):
        cmd = self.parser.parse("Set the brightness to 45 percent", _state())
        self.assertIsInstance(cmd, SetBrightness)
        self.assertAlmostEqual(cmd.value, 0.45)

    def test_named_level_full(self):
        cmd = self.parser.parse("Set it to full brightness", _state())
        self.assertIsInstance(cmd, SetBrightness)
        self.assertAlmostEqual(cmd.value, 1.0)

    def test_named_level_half(self):
        cmd = self.parser.parse("Set it to half brightness", _state())
        self.assertIsInstance(cmd, SetBrightness)
        self.assertAlmostEqual(cmd.value, 0.5)


class TestRelativeBrightness(SpacyParserTestCase):
    def test_reduce_by_20_percent(self):
        cmd = self.parser.parse("Reduce the brightness by 20%", _state())
        self.assertIsInstance(cmd, AdjustBrightness)
        self.assertAlmostEqual(cmd.delta, -0.20)

    def test_increase_by_15_percent(self):
        cmd = self.parser.parse("Increase the brightness by 15%", _state())
        self.assertIsInstance(cmd, AdjustBrightness)
        self.assertAlmostEqual(cmd.delta, 0.15)

    def test_lower_by_verb_form(self):
        # "lowered" should still resolve via lemmatization to "lower".
        cmd = self.parser.parse("The brightness was lowered by 30%", _state())
        self.assertIsInstance(cmd, AdjustBrightness)
        self.assertAlmostEqual(cmd.delta, -0.30)

    def test_vague_brighten_uses_default_step(self):
        cmd = self.parser.parse("Brighten it a bit", _state())
        self.assertIsInstance(cmd, AdjustBrightness)
        self.assertGreater(cmd.delta, 0)


class TestUnknown(SpacyParserTestCase):
    def test_unrelated_sentence(self):
        cmd = self.parser.parse("What's the weather like today?", _state())
        self.assertIsInstance(cmd, Unknown)

    def test_empty_string(self):
        cmd = self.parser.parse("   ", _state())
        self.assertIsInstance(cmd, Unknown)


if __name__ == "__main__":
    unittest.main()
