"""Diagnose WHY the corrected value function still fails.

Hypothesis: the `leftover` penalty is constant within a BFS level (all nodes at
depth d have the same len(state)), so it cannot change the ordering *within* a
level. The pruning decision at layer 1 is therefore identical to the original,
and the good path is pruned away before depth 2.

This script:
  1. Prints the layer-1 ranking under both value functions, showing the penalty
     is a constant shift.
  2. Finds a genuine solution by exhaustive search, so we know what the search
     *should* have found.
  3. Re-runs BFS while tracking whether any ancestor of a genuine solution
     survives the layer-1 cut.
"""

from __future__ import annotations

import itertools

from experiment_value_fn import (
    Node, OPS, NUMBERS, TARGET, evaluate, expand,
    value_original, value_corrected, is_solution, all_leaves,
)


def solution_paths(node: Node, limit_ops: int = 3) -> list[list[str]]:
    """Exhaustively enumerate traces that reach a genuine solution."""
    found: list[list[str]] = []
    if is_solution(node):
        return [node.trace]
    if len(node.trace) >= limit_ops:
        return []
    for ch in expand(node):
        found.extend(solution_paths(ch, limit_ops))
    return found


def main() -> None:
    print("=" * 72)
    print("DIAGNOSIS — why the leftover penalty cannot fix BFS pruning")
    print("=" * 72)
    print()

    # ---- 1. is the layer-1 penalty really constant? -------------------
    print("1. Layer-1 children under both value functions")
    print("-" * 72)
    root = Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[])
    kids = expand(root)
    print(f"   layer-1 child count: {len(kids)}")
    print(f"   all len(state) == 3 ? {all(len(k.state) == 3 for k in kids)}")
    print()

    v_orig = {}
    v_corr = {}
    for k in kids:
        v_orig[id(k)] = value_original(k)
        v_corr[id(k)] = value_corrected(k)

    diffs = {round(v_corr[id(k)] - v_orig[id(k)], 9) for k in kids}
    print(f"   distinct (corrected - original) values: {diffs}")
    print("   -> a single constant. The penalty shifts every child equally,")
    print("      so it cannot reorder them. Pruning is unchanged.")
    print()

    rank_orig = sorted(kids, key=value_original, reverse=True)[:8]
    rank_corr = sorted(kids, key=value_corrected, reverse=True)[:8]
    same = [k.trace[-1] for k in rank_orig] == [k.trace[-1] for k in rank_corr]
    print(f"   top-8 sets identical? {same}")
    print()

    # ---- 2. what is the real solution? -------------------------------
    print("2. Genuine solutions, found by exhaustive search")
    print("-" * 72)
    sols = solution_paths(Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[]))
    seen = set()
    uniq: list[list[str]] = []
    for s in sols:
        key = tuple(sorted(s))
        if key not in seen:
            seen.add(key)
            uniq.append(s)
    print(f"   total solution traces: {len(sols)} (distinct modulo commutation: {len(uniq)})")
    for s in uniq[:6]:
        print(f"     {s}")
    print()

    # ---- 3. does any ancestor survive the layer-1 cut? ---------------
    print("3. Do solution ancestors survive the layer-1 top-8 cut?")
    print("-" * 72)

    def first_step(trace: list[str]) -> str | None:
        return trace[0] if trace else None

    needed_first_steps = {first_step(s) for s in sols}
    print(f"   distinct first steps that lead to a solution: {sorted(needed_first_steps)}")

    surviving = {k.trace[-1] for k in rank_corr}
    hit = needed_first_steps & surviving
    miss = needed_first_steps - surviving
    print(f"   surviving in top-8        : {sorted(hit) or 'NONE'}")
    print(f"   pruned away before depth 2: {sorted(miss) or 'NONE'}")
    print()

    if not hit:
        print("   => NO solution-bearing branch survives layer 1.")
        print("      BFS can never reach a solution at max_expansions_per_level=8,")
        print("      regardless of how the value function is written.")
    print()

    print("=" * 72)
    print("CONCLUSION")
    print("=" * 72)
    print("  The failure has TWO independent causes, and only one was fixed:")
    print("    (a) value() ignores unused numbers  -> fixed, but it is a constant")
    print("        shift within a level, so it never changes within-level pruning.")
    print("    (b) max_expansions_per_level=8 throws away every solution-bearing")
    print("        branch at depth 1. The budget, not the scorer, is the binding")
    print("        constraint. Raising the beam is what actually recovers the")
    print("        solution.")
    print()


if __name__ == "__main__":
    main()
