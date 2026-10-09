# LEARNING.md — AI Engineering from Scratch

Learner progress log. Maintained by the `learn` skill.

**Started:** 2026-10-08
**Entry point:** Phase 14 · Lesson 02 (resumed after Lesson 01 "The Agent Loop")

> Note: Lesson 01 (The Agent Loop / ReAct) was completed before this file
> existed, so it has no logged row. It was confirmed complete by the learner
> and used as the warm-up source for Lesson 02.

## Mission

Not recorded yet. Run `start-learning` to build a personalized plan and a
Mission statement, or keep learning linearly.

## Phase Status

| Phase | Name | Status |
|:---:|---|:---:|
| 14 | Agent Engineering | Do |

## Review queue

| Added | Phase / Lesson | Missed topic |
|---|---|---|
| 2026-10-09 | 14 / 04 — Tree of Thoughts and LATS | Hand-tracing tree growth / node counting on a branching space (had to be walked through `C(4,2)×4=24`). Re-test later: why the UCT exploration term rescues MCTS from a biased value function while BFS stays trapped no matter how wide the beam. |

## Progress log

| Date | Phase / Lesson | Score | Notes |
|---|---|:---:|---|
| 2026-10-08 | 14 / 02 — ReWOO and Plan-and-Execute | 2/2 | Warm-up (from L01) 2/2. Strong on the planning/execute split. Needed a second pass on: (a) topological layering — first thought all 3 nodes of a 3-node DAG would clear in round 1, missed that `E3` depends on `#E1` *and* `#E2`; (b) the token-accounting in `run_react_mock` (needed a concrete walkthrough to see the `history_chars` accumulation). Landed the core idea unaided in his own words: "no need to re-feed repeated thinking cost into later execution." |
| 2026-10-09 | 14 / 03 — Reflexion: Verbal Reinforcement Learning | 2/2 | Warm-up (from L02) 2/2 — clean on quadratic ReAct prompt growth and on ReWOO's per-node (not per-step) failure localization. Concept checks all correct: fresh re-attempt vs resume (correctly rejected "keep the trajectory"), scalar-over-self-eval when a real executor exists (SQL case), and discarding transient-external failures. Only stumble: hand-tracing the code — could not predict the trial count unaided, needed a step-by-step walkthrough. The subtlety he'd missed is the ordering in `run_reflexion`: `if success: break` fires *before* `memory.add(...)`, so the successful trial's reflection is never stored, and the baseline stays stuck on `[1,2,3]` because a fresh `EpisodicMemory()` is passed each trial. Ran the code live to confirm trial 3 succeeds with 2 reflections in memory. Connected it himself to L02: "don't re-feed the repeated thinking cost" → "don't re-feed the failed process." |
| 2026-10-09 | 14 / 04 — Tree of Thoughts and LATS | 2/2 | Warm-up (from L03) 2/2 — fresh re-attempt and scalar-evaluator, both immediate. Concept checks: node definition (C), UCT exploration term growing as N(s,a) shrinks (A), and the single-right-answer + noisy-evaluator case where search is harmful (C) — all correct, no misses. Stumbled on the node-count prediction: could not get `C(4,2)×4=24` unaided, said "我数据结构这里有点欠缺", needed the full tree walkthrough (state 4→3→2→1, depth fixed at 3, prune 24→8). Then *asked whether the sample code was deliberately broken or was a bug* — an excellent question that turned into a 4-round controlled experiment. Findings: (1) `_all_leaves` counts "no children" as a leaf, so a never-expanded `(24,4)` node was returned as a finished leaf — real bug, confirmed by its disappearance after the fix; (2) `value()` ignores how many numbers are still unused, but the `leftover` penalty is a *constant within a BFS level*, so it cannot reorder anything — my first fix was inert; (3) the binding constraint is not the scorer but the search shape: widening the BFS beam 8→24 changed nothing (the `6*4=24` partial scores a perfect 0.0 and dominates at every width), while MCTS with 400 iterations *did* solve it, because UCT's exploration term penalises the over-visited branch. Two genuine solutions exist: `6+1=7, 7*4=28, 28-4=24` and `6-1=5, 5*4=20, 20+4=24`. Kept `code/experiment_value_fn.py` and `code/diagnose_pruning.py` as his own artifacts. Added to Review queue. |
