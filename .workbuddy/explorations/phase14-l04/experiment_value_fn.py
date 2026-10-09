"""Controlled experiment: does the biased value function cause the search to fail?

Diagnosis from the lesson discussion:
  1. `value()` on intermediate nodes rewards "a number close to TARGET sitting in
     state" but never penalises "how many numbers are still unused". So a dead
     state like (24, 4, 1) scores a perfect 0.0 while a live state like (6, 2, 1)
     scores -0.18. The ranking is inverted.
  2. `_all_leaves()` treats "no children" as a leaf, but `expand()` uses
     len(state) < 2. A node that was never expanded looks like a leaf even when
     its state still holds 2+ numbers -> "fake leaf".

This script runs the SAME search algorithms with two value functions:
  A. ORIGINAL  : min-distance only            (the shipped `value`)
  B. CORRECTED : min-distance + leftover penalty
and reports whether the returned trace is a genuine solution.

A trace is a genuine solution iff it reaches len(state) == 1 and the final
number equals TARGET exactly.
"""

from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass, field

NUMBERS = [4, 6, 4, 1]
TARGET = 24
OPS = ["+", "-", "*", "/"]


@dataclass
class Node:
    state: tuple[float, ...]
    trace: list[str]
    visits: int = 0
    value_sum: float = 0.0
    children: list["Node"] = field(default_factory=list)
    expanded: bool = False

    @property
    def q(self) -> float:
        return self.value_sum / self.visits if self.visits else 0.0


def evaluate(a: float, op: str, b: float) -> float | None:
    if op == "+":
        return a + b
    if op == "-":
        return a - b
    if op == "*":
        return a * b
    if op == "/":
        return a / b if b != 0 else None
    return None


def expand(node: Node) -> list[Node]:
    children: list[Node] = []
    state = node.state
    node.expanded = True
    if len(state) < 2:
        return children
    for i, j in itertools.combinations(range(len(state)), 2):
        for op in OPS:
            a, b = state[i], state[j]
            v = evaluate(a, op, b)
            if v is None:
                continue
            remaining = [s for k, s in enumerate(state) if k not in (i, j)]
            new_state = tuple(sorted(remaining + [v], reverse=True))
            step = f"{a}{op}{b}={v}"
            children.append(Node(state=new_state, trace=node.trace + [step]))
    return children


# ---------------------------------------------------------------- value fns

def value_original(node: Node) -> float:
    """The shipped scoring function: min distance to TARGET only."""
    if len(node.state) == 1:
        result = node.state[0]
        return 1.0 if abs(result - TARGET) < 1e-6 else -abs(result - TARGET) / 100.0
    best_distance = min(abs(v - TARGET) for v in node.state)
    return -best_distance / 100.0


def value_corrected(node: Node) -> float:
    """Fix: penalise the number of *unused* numbers still in state.

    An intermediate node with `len(state)` numbers needs `len(state) - 1` more
    operations, each of which can destroy a good partial result. So a state
    holding a perfect 24 with 2 numbers left is far from done.
    """
    if len(node.state) == 1:
        result = node.state[0]
        return 1.0 if abs(result - TARGET) < 1e-6 else -abs(result - TARGET) / 100.0
    best_distance = min(abs(v - TARGET) for v in node.state)
    leftover = len(node.state) - 1          # operations still to perform
    return -best_distance / 100.0 - leftover * 0.2


# ---------------------------------------------------------------- search

def is_solution(node: Node) -> bool:
    return len(node.state) == 1 and abs(node.state[0] - TARGET) < 1e-6


def tot_bfs(root: Node, value_fn, max_expansions_per_level: int = 8,
            max_depth: int = 3) -> tuple[Node | None, int]:
    frontier = [root]
    expansions = 0
    for _ in range(max_depth):
        scored: list[tuple[float, Node]] = []
        for node in frontier:
            for child in expand(node):
                expansions += 1
                scored.append((value_fn(child), child))
                if value_fn(child) > 0.99:
                    return child, expansions
        scored.sort(key=lambda p: p[0], reverse=True)
        frontier = [n for _, n in scored[:max_expansions_per_level]]
    best = max(frontier, key=value_fn) if frontier else None
    return best, expansions


def uct(parent: Node, child: Node, value_fn, c: float = 1.4) -> float:
    if child.visits == 0:
        return float("inf")
    return child.q + c * math.sqrt(math.log(parent.visits) / child.visits)


def simulate(node: Node, depth: int, rng: random.Random, value_fn) -> float:
    current = node
    for _ in range(depth):
        options = expand(current)
        if not options:
            break
        current = rng.choice(options)
    return value_fn(current)


def backprop(path: list[Node], reward: float) -> None:
    for n in path:
        n.visits += 1
        n.value_sum += reward


def mcts(root: Node, iterations: int, rng: random.Random, value_fn) -> tuple[Node, int]:
    expansions = 0
    for _ in range(iterations):
        path = [root]
        cur = root
        while cur.children:
            cur = max(cur.children, key=lambda ch: uct(cur, ch, value_fn))
            path.append(cur)
        if cur.visits > 0 and len(cur.state) > 1:
            cur.children = expand(cur)
            expansions += len(cur.children)
            if cur.children:
                cur = cur.children[0]
                path.append(cur)
        reward = simulate(cur, depth=max(0, 3 - len(cur.trace)), rng=rng, value_fn=value_fn)
        backprop(path, reward)
    best_leaf = max(all_leaves(root), key=value_fn, default=root)
    return best_leaf, expansions


def all_leaves(node: Node) -> list[Node]:
    """Real leaves: state fully collapsed to one number.

    Fixes the shipped `_all_leaves`, which counted "no children" as a leaf and
    so returned never-expanded intermediate nodes as if they were finished.
    """
    if len(node.state) == 1:
        return [node]
    out: list[Node] = []
    for ch in node.children:
        out.extend(all_leaves(ch))
    return out


def all_leaves_original(node: Node) -> list[Node]:
    if not node.children:
        return [node]
    out: list[Node] = []
    for ch in node.children:
        out.extend(all_leaves_original(ch))
    return out


# ---------------------------------------------------------------- driver

def report(label: str, best: Node | None, expansions: int) -> dict:
    ok = best is not None and is_solution(best)
    trace = best.trace if best is not None else []
    state = best.state if best is not None else ()
    print(f"  {label}")
    print(f"    trace      : {trace}")
    print(f"    final state: {state}")
    print(f"    expansions : {expansions}")
    print(f"    genuine solution? {'YES' if ok else 'NO'}")
    return {"label": label, "ok": ok, "expansions": expansions}


def main() -> None:
    print("=" * 72)
    print("CONTROLLED EXPERIMENT — value function quality vs search outcome")
    print("=" * 72)
    print(f"numbers: {NUMBERS}   target: {TARGET}")
    print()

    results = []

    print("A. ORIGINAL value function (min-distance only)")
    print("-" * 72)
    root = Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[])
    best, n = tot_bfs(root, value_original)
    results.append(report("ToT BFS", best, n))

    rng = random.Random(7)
    root = Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[])
    root.children = expand(root)
    best, n = mcts(root, iterations=80, rng=rng, value_fn=value_original)
    results.append(report("LATS MCTS", best, n))
    print()

    print("B. CORRECTED value function (+ leftover penalty)")
    print("-" * 72)
    root = Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[])
    best, n = tot_bfs(root, value_corrected)
    results.append(report("ToT BFS", best, n))

    rng = random.Random(7)
    root = Node(state=tuple(sorted(NUMBERS, reverse=True)), trace=[])
    root.children = expand(root)
    best, n = mcts(root, iterations=80, rng=rng, value_fn=value_corrected)
    results.append(report("LATS MCTS", best, n))
    print()

    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    for r in results:
        print(f"  {r['ok'] and 'PASS' or 'FAIL'}  {r['label']:<24} expansions={r['expansions']}")

    solved = sum(1 for r in results if r["ok"])
    print()
    print(f"  {solved}/{len(results)} runs produced a genuine solution.")
    print()
    print("  Interpretation: the search algorithm is identical in both halves.")
    print("  Only the value function changed. That is the whole lesson — search")
    print("  optimises whatever you score, so a biased scorer is a biased search.")


if __name__ == "__main__":
    main()
