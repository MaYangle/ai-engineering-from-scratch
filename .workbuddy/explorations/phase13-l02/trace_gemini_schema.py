"""Trace `_gemini_schema` on WEATHER.input_schema, field by field.

Question under test: after the canonical schema goes through the Gemini
translator, is the outer `type` written the same way as `units.type`?

Run: python .workbuddy/explorations/phase13-l02/trace_gemini_schema.py
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "phases/13-tools-and-protocols/02-function-calling-deep-dive/code/main.py"

spec = importlib.util.spec_from_file_location("l02_main", SRC)
m = importlib.util.module_from_spec(spec)
sys.modules["l02_main"] = m          # needed before exec_module (dataclass lookup)
spec.loader.exec_module(m)

src = m.WEATHER.input_schema
out = m._gemini_schema(src)

pairs = [
    ("top-level type", src["type"], out["type"]),
    ("properties.city.type", src["properties"]["city"]["type"], out["properties"]["city"]["type"]),
    ("properties.units.type", src["properties"]["units"]["type"], out["properties"]["units"]["type"]),
]

print("field                     canonical      -> gemini")
print("-" * 58)
for name, before, after in pairs:
    print(f"{name:<25} {before!r:<14} -> {after!r}")

print("-" * 58)
print("additionalProperties kept  :", "additionalProperties" in out)

# Why does units.type survive unchanged? Show the guard that decides it.
units_type = src["properties"]["units"]["type"]
print("\nguard check at the `units` node: isinstance(v, str) ->", isinstance(units_type, str))
print("=> the .upper() branch is skipped, the value falls through to recursion")
print("=> list branch maps over elements; 'string' is neither dict nor list, returned as-is")
