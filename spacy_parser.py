from functools import lru_cache
from typing import Optional

from lightbulb_cli.commands import (
    AdjustBrightness,
    Command,
    SetBrightness,
    Toggle,
    TurnOff,
    TurnOn,
    Unknown,
)
from lightbulb_cli.state import LightBulbState

DEFAULT_MODEL_NAME = "en_core_web_sm"

# Relative brightness step used for vague instructions with no explicit
# number, e.g. "brighten it a bit" / "dim it".
DEFAULT_STEP = 0.10

TOGGLE_LEMMAS = {"toggle", "flip"}
INCREASE_LEMMAS = {"increase", "raise", "brighten", "boost", "up"}
DECREASE_LEMMAS = {"decrease", "reduce", "lower", "dim", "darken", "down"}
BRIGHTNESS_TOPIC_LEMMAS = {"brightness", "bright", "dim", "dimmer", "brighten"}


class SpacyParserError(RuntimeError):
    """Raised when spaCy or its language model can't be loaded."""


# Since spacy.load is expensive, lru_cache memorizes the function.
# maxsize signifies the model_name and caches only one model, increase the value to cache multiple distinct models
@lru_cache(maxsize=1)
def load_nlp(model_name: str):
    try:
        import spacy
    except ImportError as exc:
        raise SpacyParserError(
            "The 'spacy' package is not installed. Run `pip install spacy` "
            "(see requirements.txt)."
        ) from exc
    try:
        return spacy.load(model_name)
    except OSError as exc:
        raise SpacyParserError(
            f"spaCy model {model_name!r} is not installed. Run: "
            f"python -m spacy download {model_name}"
        ) from exc

# Drop a trailing 'instead of ...' clause naming the value NOT chosen.
def strip_instead_of_clause(doc):
    tokens = list(doc)
    for i in range(len(tokens) - 1):
        if tokens[i].lemma_.lower() == "instead" and tokens[i + 1].lower_ == "of":
            return doc[:i].as_doc()
    return doc


# Finds percentage in the command
def find_percent(tokens):
    for i, tok in enumerate(tokens):
        if not tok.like_num:
            continue
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if nxt is None or (nxt.text != "%" and nxt.lower_ != "percent" and nxt.lower_ != "percentage"):
            continue
        try:
            value = float(tok.text)
        except ValueError:
            continue
        preceding = tokens[i - 1].lower_ if i > 0 else None # preceding suggests whether to adjust (by) or set brightness (to)
        print("value and preceding: ", value, preceding)
        return value, preceding
    return None


# Parser class
class SpacyParser:
    def __init__(self, model_name: str = DEFAULT_MODEL_NAME):
        self.nlp = load_nlp(model_name)

    def parse(self, text: str, state: LightBulbState) -> Command:
        stripped = text.strip()
        if not stripped:
            return Unknown(raw_text=text, reason="empty input")

        doc = self.nlp(stripped) # Parsing the command with spaCy
        working = strip_instead_of_clause(doc)
        tokens = list(working)
        lemmas = {tok.lemma_.lower() for tok in tokens}
        print("lemmas: ", lemmas)
        lowers = {tok.lower_ for tok in tokens}
        print("lowers: ", lowers)

        brightness_relevant = bool(
            lemmas & (BRIGHTNESS_TOPIC_LEMMAS | INCREASE_LEMMAS | DECREASE_LEMMAS)
        ) or find_percent(tokens) is not None

        if brightness_relevant:
            command = self.parse_brightness(tokens, lemmas, text)
            if command is not None:
                return command
            # Mentioned brightness/up/down but nothing usable came out of it;
            # fall through in case it's actually a plain on/off instruction.

        if lemmas & TOGGLE_LEMMAS:
            return Toggle()

        has_on = "on" in lowers
        has_off = "off" in lowers
        if has_off and not has_on:
            return TurnOff()
        if has_on and not has_off:
            return TurnOn()

        return Unknown(raw_text=text, reason="could not identify an action")

    @staticmethod
    def parse_brightness(tokens, lemmas, original_text: str) -> Optional[Command]:
        found = find_percent(tokens)
        if found is not None:
            value, preceding = found
            magnitude = value / 100.0
            if preceding == "by":
                if lemmas & DECREASE_LEMMAS:
                    return AdjustBrightness(delta=-magnitude)
                if lemmas & INCREASE_LEMMAS:
                    return AdjustBrightness(delta=magnitude)
                return Unknown(
                    raw_text=original_text,
                    reason="relative brightness change with no clear direction",
                )
            return SetBrightness(value=max(0.0, min(1.0, magnitude)))

        if lemmas & INCREASE_LEMMAS:
            return AdjustBrightness(delta=DEFAULT_STEP)
        if lemmas & DECREASE_LEMMAS:
            return AdjustBrightness(delta=-DEFAULT_STEP)

        return None
