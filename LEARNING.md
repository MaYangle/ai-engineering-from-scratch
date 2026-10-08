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

_(empty)_

## Progress log

| Date | Phase / Lesson | Score | Notes |
|---|---|:---:|---|
| 2026-10-08 | 14 / 02 — ReWOO and Plan-and-Execute | 2/2 | Warm-up (from L01) 2/2. Strong on the planning/execute split. Needed a second pass on: (a) topological layering — first thought all 3 nodes of a 3-node DAG would clear in round 1, missed that `E3` depends on `#E1` *and* `#E2`; (b) the token-accounting in `run_react_mock` (needed a concrete walkthrough to see the `history_chars` accumulation). Landed the core idea unaided in his own words: "no need to re-feed repeated thinking cost into later execution." |
