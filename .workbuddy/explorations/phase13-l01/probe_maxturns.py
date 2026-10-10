"""Probe: what does the loop print when MAX_TURNS is too small?

Loads the shipped 13/01 harness without editing it, then runs the same
`add 7 and 35` query at MAX_TURNS = 1, 2, 3 so the turn accounting is visible.

Run: <managed python> .workbuddy/explorations/phase13-l01/probe_maxturns.py
"""

from __future__ import annotations

import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
MAIN = ROOT / "phases" / "13-tools-and-protocols" / "01-the-tool-interface" / "code" / "main.py"

spec = importlib.util.spec_from_file_location("lesson_main", MAIN)
m = importlib.util.module_from_spec(spec)
sys.modules["lesson_main"] = m
spec.loader.exec_module(m)

QUERY = "please add 7 and 35"

for turns in (1, 2, 3):
    print("#" * 72)
    print(f"### MAX_TURNS = {turns}")
    print("#" * 72)
    m.MAX_TURNS = turns
    m.run_loop(QUERY)
    print()
