"""Trace the critique -> refine "protocol" break in L05's Self-Refine toy.

The toy implements generate / feedback / refine as three *separate* deterministic
functions instead of as three prompts to one model. That makes an implicit
requirement explicit: the three functions must agree on a protocol. They do not.

Findings this script reproduces:

1. `feedback_self` emits the critique "double-check capital", but `generate()`
   greps for "germany". Mismatch -> `generate()` falls through to
   `return history[-1].output` -> the output never changes. 4 iterations, zero
   progress. (My first guess blamed the *everest* link; the break is at the
   FIRST link instead.)

2. `feedback_self` has no branch for the second error at all. "Europe" +
   "Everest" falls into the unconditional `return "no issues", True`, which is
   the rubber-stamp loop from the lesson, in code form.

3. The `everest` branch in `generate()` is NOT dead code -- it is correctly
   wired but never receives its signal. Hand-feed a critique containing
   "everest" and it repairs the output immediately.

4. `verify_external` (the CRITIC path) converges in 3 iterations not because it
   fixes the protocol, but because it re-checks every item on every round, so
   its freeform critique happens to carry the right keywords. Real lesson:
   verifier output must be structured JSON, not prose -- exactly the "hard
   reject" already written in outputs/skill-refine-loop.md.

Run:
    python trace_critique_protocol.py
"""

from __future__ import annotations

import sys
from pathlib import Path

CODE_DIR = (
    Path(__file__).resolve().parents[3]
    / "phases"
    / "14-agent-engineering"
    / "05-self-refine-and-critic"
    / "code"
)
sys.path.insert(0, str(CODE_DIR))

import main as M  # noqa: E402


def which_branch(critique: str) -> str:
    """Reproduce generate()'s dispatch to show which keyword it greps for."""
    low = critique.lower()
    if "germany" in low:
        return "'germany' branch (repairs bullet 1)"
    if "everest" in low:
        return "'everest' branch (repairs bullet 2)"
    return "NONE -> falls through to `return history[-1].output` (no change)"


def trace_self_refine() -> None:
    print("=== Self-Refine path: follow critique text -> refine action ===")
    output = M.generate("world facts", [])
    print(f"\n[init]\n{output}")

    for i in range(1, 5):
        critique, ok = M.feedback_self(output)
        print(f"\n--- iter {i} ---")
        print(f"  feedback_self -> critique={critique!r}  ok={ok}")
        if ok:
            print("  ok=True -> loop breaks. The 'Everest' error was never examined.")
            return
        print(f"  generate() dispatch: {which_branch(critique)}")
        output = M.generate("world facts", [M.Attempt(i, output, critique, ok)])


def prove_everest_branch_is_live() -> None:
    print("\n\n=== Is generate()'s `everest` branch dead code? ===")
    fake = M.Attempt(1, "dummy", "the everest bullet looks wrong", False)
    print("hand-fed critique: 'the everest bullet looks wrong'")
    print(M.generate("world facts", [fake]))
    print("-> branch is correctly wired; it simply never receives its signal.")


def contrast_critic() -> None:
    print("\n\n=== CRITIC path for contrast (re-checks all items every round) ===")
    reg = M.run_loop("world facts", use_critic=True)
    for attempt in reg:
        tag = "OK " if attempt.verified else "..."
        print(f"  iter {attempt.iteration} {tag} {attempt.critique}")
    print(f"-> converged in {len(reg)} iterations despite the same broken protocol.")


def main() -> None:
    trace_self_refine()
    prove_everest_branch_is_live()
    contrast_critic()


if __name__ == "__main__":
    main()
