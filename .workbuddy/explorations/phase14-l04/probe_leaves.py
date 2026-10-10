"""Probe the MCTS result-picking bug in L04's `_all_leaves`.

Question under test: L04's MCTS returns state (24, 4) instead of a solved
single number. Is that (a) the search failing to find a solution, or
(b) the search finding one but the result-picker lying about it?

Three detectors are compared:

  baseline  - the shipped `_all_leaves`: "no children" counts as a leaf.
              BUG: a node that was never visited (`visits == 0`) is never
              expanded by `mcts()`, so it has `children == []` and is
              returned as a finished leaf.
  S0        - "a node holding a single number is finished". Intended as the
              fix. WRONG: it demands one exact path reach the root of the
              tree, so it finds nothing at low iteration counts.
  S1        - "a node that can still be expanded is a valid answer". BROKEN
              differently: the root itself satisfies it, so the empty trace
              wins unconditionally.

Run:
    python probe_leaves.py
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

CODE_DIR = (
    Path(__file__).resolve().parents[3]
    / "phases"
    / "14-agent-engineering"
    / "04-tree-of-thoughts-lats"
    / "code"
)
sys.path.insert(0, str(CODE_DIR))

import main as M  # noqa: E402


def leaves(node: M.Node) -> list[M.Node]:
    """Iterative leaf collection; same semantics as the shipped helper."""
    stack = [node]
    out: list[M.Node] = []
    while stack:
        cur = stack.pop()
        if not cur.children:
            out.append(cur)
        else:
            stack.extend(cur.children)
    return out


def s0_single_number(node: M.Node) -> M.Node | None:
    """S0: only a node with one number left counts as finished."""
    stack = [node]
    while stack:
        cur = stack.pop()
        if len(cur.state) == 1:
            return cur
        stack.extend(cur.children)
    return None


def s1_expandable(node: M.Node) -> M.Node | None:
    """S1: any node that could still be expanded counts as an answer."""
    stack = [node]
    while stack:
        cur = stack.pop()
        if len(cur.state) > 1:
            return cur
        stack.extend(cur.children)
    return None


def fresh_root() -> M.Node:
    root = M.Node(state=tuple(sorted(M.NUMBERS, reverse=True)), trace=[])
    root.children = M.expand(root)
    for child in root.children:
        child.visits = 0
    return root


def main() -> None:
    print(f"{'detector':>16} {'iters':>6} {'expans':>7}  {'picked state':>14} {'value':>7}  trace")
    print("-" * 78)

    detectors = [
        ("baseline", lambda r: max(leaves(r), key=M.value, default=r)),
        ("S0 single-num", s0_single_number),
        ("S1 expandable", s1_expandable),
    ]

    for tag, detect in detectors:
        for iters in (80, 200, 400, 800):
            root = fresh_root()
            _, expansions = M.mcts(root, iterations=iters, rng=random.Random(7))
            picked = detect(root)
            if picked is None:
                print(f"{tag:>16} {iters:>6} {expansions:>7}  {'-- none --':>14}")
                continue
            print(
                f"{tag:>16} {iters:>6} {expansions:>7}  "
                f"{str(picked.state):>14} {M.value(picked):>7.3f}  {picked.trace}"
            )


if __name__ == "__main__":
    main()
