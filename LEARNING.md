# LEARNING.md — AI Engineering from Scratch

Learner progress log. Maintained by the `learn` skill.

**Started:** 2026-10-08
**Entry point:** Phase 14 · Lesson 02 (resumed after Lesson 01 "The Agent Loop")
**Current routing:** Phase 13 bridge (01–05) → then Phase 14 · L06. See below.

> Note: Lesson 01 (The Agent Loop / ReAct) was completed before this file
> existed, so it has no logged row. It was confirmed complete by the learner
> and used as the warm-up source for Lesson 02.
>
> Note: Phase 13 was never started. A prerequisite gap surfaced on 2026-10-09
> while teaching Phase 14 · L06; the Phase 13 bridge section below closes it.

## Mission

Not recorded yet. Run `start-learning` to build a personalized plan and a
Mission statement, or keep learning linearly.

## Phase Status

Read in order: `learn` picks the first not-yet-logged lesson of the first phase
whose Status is `Do` or `Review`. Phase 13 sits above Phase 14 on purpose — see
the bridge section below.

| Phase | Name | Status |
|:---:|---|:---:|
| 13 | Tools & Protocols | Do (bridge subset only — see below) |
| 14 | Agent Engineering | Do |

## Phase 13 bridge

Installed 2026-10-09 after a placement diagnostic. Phase 13 is a prerequisite of
Phase 14 · L06 (Tool Use and Function Calling), which declares
`Phase 13 · 01` explicitly. Phase 13 had never been started.

**Diagnostic result:** Round 1 (lessons 01–05, the tool interface and function
calling block) scored **0/4**. Rounds 2–4 were not administered — the learner
elected to bridge rather than place precisely across the specialist blocks.
Instrument kept at `.workbuddy/explorations/phase13-placement.md`.

**Bridge subset — do these five, in this order, then resume Phase 14 · L06.**

| Order | Lesson | Path |
|:---:|---|---|
| 1 | 01 The Tool Interface | `phases/13-tools-and-protocols/01-the-tool-interface/` |
| 2 | 02 Function Calling Deep Dive | `phases/13-tools-and-protocols/02-function-calling-deep-dive/` |
| 3 | 03 Parallel and Streaming Tool Calls | `phases/13-tools-and-protocols/03-parallel-and-streaming-tool-calls/` |
| 4 | 04 Structured Output | `phases/13-tools-and-protocols/04-structured-output/` |
| 5 | 05 Tool Schema Design | `phases/13-tools-and-protocols/05-tool-schema-design/` |

**Progress:** 13/03 logged 2026-10-10 → next is **13/04**.

**Exit condition:** after 13/05 is logged, Phase 14 · L06 becomes the next
eligible lesson. Do not continue into 13/06 from this file.

**Note (2026-10-10):** lessons 01–05 of Phase 13 ship **no `quiz.json`** (only
06–18 and 22–31 have one), so `learn` Step 3 has nothing to fetch across the
whole bridge. A quiz was authored for 13/01 at
`phases/13-tools-and-protocols/01-the-tool-interface/quiz.json` to the
documented schema. The same gap remains open for 13/02–13/05. For **13/02** and
**13/03** the post quiz was administered **verbally in-session** (3 questions each,
written from the lessons' stated objectives) rather than by adding a file; the
repository gap is unchanged.

**Deliberately NOT in the bridge** — these belong to other routes with their own
state files, and teaching them from here would break those routes' ordering:

- **06–18, 28–31** → the Model Context Protocol route (17 lessons, ~23h15m),
  state file `MCP-LEARNING.md`, skill `learn-mcp`, order pinned in
  `learning-paths/model-context-protocol.json`. Note: **13/15 is that route's
  public-deployment security gate** and must not be pulled forward out of order.
- **22, 24–27** → the Agent Skills route, state file `AGENT-SKILLS-LEARNING.md`,
  skill `learn-agent-skills`.
- **19, 20, 21, 23** → full-curriculum lessons, deferred until they are actually
  needed; 23 is the phase capstone.

Revisit this decision when a concrete task requires MCP servers or packaged
skills. Until then, the bridge is the whole Phase 13 commitment.

## Review queue

| Added | Phase / Lesson | Missed topic |
|---|---|---|
| 2026-10-09 | 14 / 04 — Tree of Thoughts and LATS | Hand-tracing tree growth / node counting on a branching space (had to be walked through `C(4,2)×4=24`). Re-test later: why the UCT exploration term rescues MCTS from a biased value function while BFS stays trapped no matter how wide the beam. **This is one instance of a broader class, not a tree-specific gap:** the learner cannot hand-trace a loop's iteration count before predicting its output. Recurred 2026-10-10 in 13/01 (predicted `MAX_TURNS = 1` still yields an answer; it yields none), and before that in 14/02 (`history_chars`) and 14/03 (trial count). Re-test with a *loop-variable* question, and make him write out the variable's value set on paper first. **2026-10-10 update (13/02 + 13/03): the prescription is starting to work — he passed an unaided `turn ∈ {1,2,3}` count on the 13/02 warm-up, the first clean pass in five lessons.** But three new instances landed in 13/02–13/03, all of the same shape — *he traces the wrong quantity*: predicted `units.type` → `STRING, NULL` without evaluating the `isinstance(v, str)` guard; filled the streaming table's `args_buf` column with the *received chunks* instead of the *accumulated buffer*; answered the fan-out wall-clock question "800 ms" when it is **0 ms** under the stated numbers, because he advanced "per-call delivery" instead of "全部收工". **Refined re-test: ask for an *aggregated* value (running total / concatenated buffer / overall completion time), not a per-item time, and require the per-step table before the answer.** |

## Progress log

| Date | Phase / Lesson | Score | Notes |
|---|---|:---:|---|
| 2026-10-08 | 14 / 02 — ReWOO and Plan-and-Execute | 2/2 | Warm-up (from L01) 2/2. Strong on the planning/execute split. Needed a second pass on: (a) topological layering — first thought all 3 nodes of a 3-node DAG would clear in round 1, missed that `E3` depends on `#E1` *and* `#E2`; (b) the token-accounting in `run_react_mock` (needed a concrete walkthrough to see the `history_chars` accumulation). Landed the core idea unaided in his own words: "no need to re-feed repeated thinking cost into later execution." |
| 2026-10-09 | 14 / 03 — Reflexion: Verbal Reinforcement Learning | 2/2 | Warm-up (from L02) 2/2 — clean on quadratic ReAct prompt growth and on ReWOO's per-node (not per-step) failure localization. Concept checks all correct: fresh re-attempt vs resume (correctly rejected "keep the trajectory"), scalar-over-self-eval when a real executor exists (SQL case), and discarding transient-external failures. Only stumble: hand-tracing the code — could not predict the trial count unaided, needed a step-by-step walkthrough. The subtlety he'd missed is the ordering in `run_reflexion`: `if success: break` fires *before* `memory.add(...)`, so the successful trial's reflection is never stored, and the baseline stays stuck on `[1,2,3]` because a fresh `EpisodicMemory()` is passed each trial. Ran the code live to confirm trial 3 succeeds with 2 reflections in memory. Connected it himself to L02: "don't re-feed the repeated thinking cost" → "don't re-feed the failed process." |
| 2026-10-09 | 14 / 05 — Self-Refine and CRITIC | 2/2 | Warm-up (from L03) 2/2 — Actor/Evaluator/Self-Reflector, and transient-external-failure as a non-helpful Reflexion case. **Pedagogy miss, corrected mid-lesson:** I opened with a live code investigation of the L04 leaf bug instead of the theory, and he called it out — "我觉得这节课你讲的不好，没有之前几节课好，我觉得还是先看理论比较重要". Re-taught in theory-first order (Self-Refine 3 prompts + why history is load-bearing; CRITIC's swap of `feedback` for `verify(tools)`; combined stop condition; evaluator-optimizer / output guardrails; the 3 pitfalls). Concept grasp was strong: he independently derived that a self-critic scores *plausibility*, not *factuality* — "如果我不知道正确答案…我确实会认为说的很有道理", and sharpened it to "the hallucination is sampled from the same distribution as the truth". He also correctly saw that `feedback_self` has no branch for the second error at all. Kept the L04/L05 experiment scripts as evidence, not as the main line. Lesson not added to Review queue. |
| 2026-10-09 | 14 / 04 — Tree of Thoughts and LATS | 2/2 | Warm-up (from L03) 2/2 — fresh re-attempt and scalar-evaluator, both immediate. Concept checks: node definition (C), UCT exploration term growing as N(s,a) shrinks (A), and the single-right-answer + noisy-evaluator case where search is harmful (C) — all correct, no misses. Stumbled on the node-count prediction: could not get `C(4,2)×4=24` unaided, said "我数据结构这里有点欠缺", needed the full tree walkthrough (state 4→3→2→1, depth fixed at 3, prune 24→8). Then *asked whether the sample code was deliberately broken or was a bug* — an excellent question that turned into a 4-round controlled experiment. Findings: (1) `_all_leaves` counts "no children" as a leaf, so a never-expanded `(24,4)` node was returned as a finished leaf — real bug, confirmed by its disappearance after the fix; (2) `value()` ignores how many numbers are still unused, but the `leftover` penalty is a *constant within a BFS level*, so it cannot reorder anything — my first fix was inert; (3) the binding constraint is not the scorer but the search shape: widening the BFS beam 8→24 changed nothing (the `6*4=24` partial scores a perfect 0.0 and dominates at every width), while MCTS with 400 iterations *did* solve it, because UCT's exploration term penalises the over-visited branch. Two genuine solutions exist: `6+1=7, 7*4=28, 28-4=24` and `6-1=5, 5*4=20, 20+4=24`. Kept `code/experiment_value_fn.py` and `code/diagnose_pruning.py` as his own artifacts. Added to Review queue. |
| 2026-10-10 | 13 / 01 — The Tool Interface | 2/2 | Warm-up (from 14/05 quiz) 2/2 — history-on-refine + CRITIC's tool-grounded verifier. Taught theory-first on the four-step spine (describe → decide → execute → observe) with an SVG that colour-codes host vs model ownership; one question per pause, four pauses, no density problem (contrast the 10-09 L06 delivery). Pause answers: placed the stall at the `decide → execute` seam but initially said the host "doesn't know" which tool was called — corrected, the payload is fully structured and the gap is that nobody *runs* it; derived enum-for-closed-set vs open string; explained parallel-result mis-correlation; classified `read_file` as consequential because of sensitive data — **correct instinct, wrong axis**, it is pure but *sensitive*, so introduced the two-axis model (pure/consequential × public/sensitive) and Rule-of-Two composition. Final code pause **missed**: asked what `add 7 and 35` prints with `MAX_TURNS = 1`, answered "still prints 42, the user still gets the answer, because turn 2 is just the final answer" — right reason, but never counted `range(1, 2)`, so missed that turn 2 never runs. Proved it by running the harness at 1/2/3 (no `MODEL :` line at 1; only the circuit-breaker message; `42.0` appears just in the host's own EXECUTE log). Taught the distinction **executing successfully ≠ answering**. Post quiz 2/2. |
| 2026-10-10 | 13 / 03 — Parallel and Streaming Tool Calls | 3/3 | Warm-up 3/3 (13/02 quiz ×2 + an `isinstance`-guard counting probe). Post quiz 3/3. **Real conceptual progress:** he asked "绝不能 parse 是什么意思?" and, once shown the real `JSONDecodeError` output, correctly reasoned that a *try-parse* completeness test is unfalsifiable ("能证明'到目前为止能解析',永远无法证明'后面不会再有内容'"). He also independently identified the `args_buf = ""` (not `None`) choice as load-bearing. **Three misses, all one class:** (a) on the streaming-probe table he filled the `args_buf` column with the *list of received chunks* instead of the *concatenated buffer* — right content, wrong object; (b) he needed the per-step table demanded explicitly, and even then skipped it on the warm-up probe (gave `abcd`, omitted `n = 2`); (c) he answered the fan-out wall-clock question "800ms" when the correct answer under the given numbers is **0ms** — he traced "per-call delivery advance" instead of "全部收工", i.e. he measured the wrong quantity. The three-layer ordering experiment landed well: he correctly reasoned that the fake stream only demonstrates *interleaving*, not *out-of-order completion*, and that the real disorder lives in the executor layer where the id-keyed dict absorbs it. **Delivery note: he is now responding to plain text tables and to runnable probes — keep using those, no inline widgets.** |
| 2026-10-10 | 13 / 02 — Function Calling Deep Dive | 3/3 | Warm-up 3/3 (13/01 quiz ×2 + the standing loop-counting probe). **First clean pass on that class in five lessons** — he wrote out `turn ∈ {1,2,3}` on his own; the "write the variable's value set on paper" prescription is working. Post quiz 3/3. Two real misses mid-lesson: (a) **inverted the causality of call-id necessity** — said "Gemini 在结果层里已经确定了匹配 id，所以不需要"; corrected to *uniqueness comes from cardinality when there is one call, and `id` becomes mandatory only when order is untrustworthy or calls are indistinguishable by name+args*; he then independently named the **canonicalization-collapse** class himself on the follow-up. (b) **`_gemini_schema` trace missed** — predicted `units.type` → `STRING, NULL`; it is actually unchanged `['string','null']`, because the guard is `isinstance(v, str)` and a list falls through to recursion. **Same class as the loop-counting weakness: he predicts from the code's *intent*, not from the *guard's value*.** New prescription: write out every branch condition's value, node by node, before predicting output. Also: he rejected the abstract "who owns the validation authority" framing and only accepted it after a runnable 3-world demo (`who_validates.py` — out-of-enum `units='Kelvin'` rejected at the provider boundary vs. silently reaching the executor). **Inline SVG tables did not render for him this session — use markdown tables.** |
