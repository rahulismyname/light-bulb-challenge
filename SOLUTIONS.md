# Solution

A CLI that controls the `LightBulb` using natural-language commands,
parsed with [spaCy](https://spacy.io/).

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate   # optional but recommended
pip install -r requirements.txt
python -m spacy download en_core_web_sm

python -m lightbulb_cli.cli
```

```
Light Bulb CLI. Type 'quit' to exit.
>>> User: Please turn the light on
Light Bulb switched ON
>>> User: Now please turn it off
Light Bulb switched OFF
>>> User: Switch it back on instead of off
Light Bulb switched ON
>>> User: Please set the brightness to 70%
Light Bulb brightness set to 70%
>>> User: Now set it to 10% instead of 70%
Light Bulb brightness set to 10%
>>> User: Reduce the brightness by 20%
Light Bulb brightness set to 90%
>>> User: quit
```

Or with Docker (builds spaCy + its English model into the image, so it
works offline at run time):

```bash
docker compose run --rm lightbulb-cli
```

## Architecture

```
light_bulb.py                    # Lightbulb call with Fns
spacy_parser.py               # NLU backend, built on spaCy
cli.py                          # REPL: input() -> parser.parse() -> executor.execute()
lightbulb_cli/
  commands.py                    # TurnOn / TurnOff / Toggle / SetBrightness / AdjustBrightness / Unknown
  state.py                       # LightBulbState: read-only snapshot (is_on, brightness)
  executor.py                     # Command -> calls the real LightBulb's methods
tests/
  test_executor.py                # unittest, no spaCy needed
  test_spacy_parser.py             # unittest, needs spaCy + en_core_web_sm (skips cleanly if absent)
```

**Parsing and execution are deliberately separate.** A parser's only job is
text -> `Command` (a small, closed set of dataclasses); the executor's only
job is `Command` -> calls on a real `LightBulb`. Neither knows about the
other's internals. That split is what makes it possible to swap the whole
NLU implementation without touching the bulb logic, and to unit-test the
bulb-mutation logic (rounding, clamping, toggle) completely independently
of how the sentence was understood.

## Why spaCy, and how it's used

The parser (`spacy_parser.py`) loads `en_core_web_sm` and works with spaCy's
tokenized/lemmatized `Doc`/`Token` objects rather than the raw string:

* **Lemmatization** handles verb inflections for free. `"turn"/"turns"/
  "turning"/"turned"`, `"reduce"/"reduces"/"reduced"`, `"raise"/"raised"/
  "raising"` all collapse to one lemma each (`token.lemma_`), so the keyword
  sets (`INCREASE_LEMMAS`, `DECREASE_LEMMAS`, `TOGGLE_LEMMAS`, ...) only need
  to list base forms, not every surface form.
* **Tokenization** turns `"70%"` into two tokens, `"70"` and `"%"`, and
  `token.like_num` flags the numeric one -- so extracting a percentage is a
  token scan (`_find_percent`), not a hand-written digit regex.
* **The token immediately before a number** (`"by"` vs `"to"`/`"at"`) is what
  distinguishes a *relative* change ("reduce ... **by** 20%") from an
  *absolute* one ("set ... **to** 70%").
* **"instead of X" distractors** ("Switch it back on **instead of off**",
  "set it to 10% **instead of 70%**") are stripped by finding the token pair
  with lemma `"instead"` + text `"of"` and slicing the `Doc` to everything
  before it (`_strip_instead_of_clause`), so both examples are handled by
  the same general rule rather than two special cases. **Assumption:** the
  distractor clause trails the real instruction, matching every example in
  the spec; `"Instead of X, do Y"` (distractor first) is not handled.

### Handled beyond the spec's two required examples
- `"Toggle the light"` / `"Flip the switch"` -- reads `state.is_on` and
  flips it.
- `"Reduce the brightness by 20%"` / `"Increase ... by 15%"` -- relative
  change against `state.brightness`, resolved via the "by" vs "to" check
  above.
- Spelled-out `"45 percent"`, `"45%"` as well as `"45 percentage"`.
- Vague relative instructions with no number (`"brighten it"`, `"dim it"`)
  fall back to a fixed 10-point step (`DEFAULT_STEP`).
- Case-insensitive, punctuation-tolerant (spaCy tokenizes `"on."`, `"on!"`
  etc. the same as `"on"`).

## Brightness math and the given class's rounding

`LightBulb.set_brightness` prints
`int(value * 100)`. Plain float arithmetic can undershoot a whole percent:

```python
>>> 0.7 - 0.2
0.49999999999999994
>>> int(0.49999999999999994 * 100)
49          # should be 50
```

So "reduce brightness by 20%" starting from 70% would silently print **49%**
instead of **50%** if we hooked `set_brightness` up naively. `executor.py`
rounds every value to the nearest whole percent (`round(value, 2)`) right
before calling `set_brightness`, without touching `light_bulb.py` at all.
`tests/test_executor.py::TestAdjustBrightness::test_handles_float_drift`
pins this behaviour down explicitly.

## Testing

```bash
python -m unittest discover      # or: pytest
```

`test_executor.py` has no spaCy dependency and covers on/off/toggle,
absolute and relative brightness (including the float-drift case above),
clamping at 0%/100%, and that `Unknown` never mutates the bulb.

`test_spacy_parser.py` covers both required examples from the spec
verbatim, the toggle/relative/named-level/spelled-out-percent extensions
above, and a couple of `Unknown` cases -- but it needs `en_core_web_sm`
installed, and skips itself cleanly (via `setUpClass` -> `SkipTest`) if
spaCy or the model isn't present, so the suite as a whole still passes
without it.