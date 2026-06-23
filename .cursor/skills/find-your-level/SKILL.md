---
name: find-your-level
version: 2.1.0
description: >
  Adaptive placement assessment for AI Engineering from Scratch. Samples from a
  56-question, phase-aligned bank (3 difficulty tiers) to estimate per-phase
  mastery, weak areas, and a personalized learning path. Trigger: /find-your-level,
  "find my level", "where should I start", "assess my knowledge", "placement test".
tags: [assessment, onboarding, curriculum, ai-engineering, adaptive]
---

# Find Your Level (v2 — Adaptive Phase Assessment)

You administer a **curriculum-aligned placement assessment** for **AI Engineering
from Scratch** (20 phases, 500+ lessons). The goal is not a single score — it is
a **per-phase mastery profile** that identifies weak areas and recommends where to
start, what to skip, and what to review.

**Linked skill:** `/check-understanding <phase>` — deep 8-question phase quiz.
This skill writes a shared **`placement-profile.json`** that `check-understanding`
reads to prioritize weak lessons and queue follow-up quizzes.

## Shared Files

| File | Purpose |
|------|---------|
| `.cursor/skills/placement-profile.json` | Cross-skill state (written here, updated by check-understanding) |
| `.cursor/skills/shared/phase-map.json` | Canonical phase id → directory → name mapping |
| `.cursor/skills/find-your-level/question-bank.json` | Placement question bank |

Fallback paths use `.claude/skills/…` if `.cursor/skills/…` is missing.

## Question Bank (required)

Load questions from the co-located bank:

```
.cursor/skills/find-your-level/question-bank.json
```

If that path is missing (e.g. user copied only SKILL.md), fall back to:

```
.claude/skills/find-your-level/question-bank.json
```

Each bank entry includes:

| Field | Meaning |
|-------|---------|
| `phase` | 0–19, aligned with `phases/NN-*` directories |
| `difficulty` | 1 = foundation, 2 = applied, 3 = advanced |
| `lesson` | Slug tying the question to a specific lesson |
| `question`, `options`, `correct`, `explanation` | MCQ payload |

**Supplemental source:** When the bank lacks coverage for a phase, or to validate
a borderline score, read `phases/<phase-dir>/<lesson>/quiz.json` and `docs/en.md`
for that phase. Do not invent off-curriculum trivia.

## Session Length (ask first)

Use **AskUserQuestion** once at start:

| Mode | Questions | Time | When to use |
|------|-----------|------|-------------|
| **Quick** | 12 | ~8 min | Rough placement |
| **Standard** (default) | 18 | ~12 min | Recommended |
| **Thorough** | 24 | ~18 min | High-stakes path planning |

If the user does not choose, use **Standard (18)**.

## Adaptive Selection Algorithm

Do **not** ask all 56 questions. Select dynamically:

### Step 1 — Coverage guarantee

Ensure the session touches **every phase cluster** at least once:

| Cluster | Phases | Min questions in session |
|---------|--------|--------------------------|
| Foundations | 0–3 | 4 (≥1 per phase) |
| Modalities | 4–6 | 2 (sample 2 of 3) |
| Transformers & Gen | 7–9 | 3 (≥1 per phase) |
| LLM stack | 10–12 | 3 (≥1 per phase) |
| Agents & systems | 13–16 | 4 (≥1 per phase) |
| Production & safety | 17–19 | 2 (≥1 per phase) |

Adjust counts proportionally for Quick (12) and Thorough (24).

### Step 2 — Difficulty ramp per phase

For each phase first touched:

1. Start with **difficulty 1** (foundation).
2. **Correct on D1** → next question from same phase at **D2**.
3. **Correct on D2** → optionally probe **D3** (if session budget allows).
4. **Wrong on D1** → stay at D1; add one more D1 from same phase if budget allows.
5. **Wrong on D2+** → do not escalate difficulty in that phase.

Never ask two questions with the same `id`. Track used IDs.

### Step 3 — Early exit (optional, Standard+ only)

If a learner gets **3 consecutive D1 wrong** across phases 1–3, stop escalating
globally — remaining foundation cluster questions should stay at D1 only.

If a learner gets **3 consecutive D3 correct** in phases 10+, skip remaining
foundation/modality questions and allocate budget to phases 13–19.

## Administering Questions

- Present **one question at a time** via **AskUserQuestion**.
- Show metadata: `Question 7/18 · Phase 11 LLM Engineering · Applied (D2) · from lesson 06-rag`.
- Do **not** reveal answers until the session ends.
- After each answer, update internal scoreboard only (no long feedback mid-quiz).

## Scoring Model

### Per-question points

| Difficulty | Points if correct | Points if wrong |
|------------|-------------------|-----------------|
| 1 — foundation | 1 | 0 |
| 2 — applied | 2 | 0 |
| 3 — advanced | 3 | 0 |

### Per-phase mastery

For each phase `P` that was tested:

```
earned_P = sum(points for correct answers in phase P)
max_P    = sum(points for all questions asked in phase P)
mastery_P = round(100 * earned_P / max_P)   # if max_P > 0
```

Phases **not tested** show `—` (unknown).

### Mastery bands

| mastery_P | Status | Recommendation |
|-----------|--------|----------------|
| ≥ 75% | **Strong** | Skip phase (skim artifacts in `outputs/` only) |
| 50–74% | **Review** | Skim `docs/en.md` + run 1–2 lesson codes |
| 25–49% | **Gap** | Work through phase partially — focus listed lessons |
| < 25% | **Weak** | Start phase from lesson 01 |
| not tested | **Unknown** | Infer from adjacent phases or assign 1 probe question |

## Entry Point Rule

**Recommended entry phase** = the **lowest-numbered phase** with status **Gap**
or **Weak**, after applying dependencies:

- If Phase 3 is Weak → entry ≤ 3 (do not start at Phase 10 even if later phases look Strong).
- If Phases 1–3 are Strong but Phase 7 is Gap → entry = 7.
- Phase 0 (Setup & Tooling) is **never** the knowledge entry point — always recommend
  it only as a parallel "environment checklist" if the user hasn't completed setup.

## Output Report (required format)

After the last question, produce:

### 1. Score summary

```
Phase | Name                      | Asked | Mastery | Status
------|---------------------------|-------|---------|--------
  0   | Setup & Tooling           |   2   |   50%   | Review
  1   | Math Foundations          |   3   |   67%   | Review
  ...
```

### 2. Weak areas (actionable)

List phases with **Gap** or **Weak**. For each, cite:

- Up to **3 lesson slugs** from missed questions (`lesson` field).
- Full path pattern: `phases/NN-<phase>/NN-<lesson>/docs/en.md`.

Example:

> **Phase 11 — LLM Engineering (Gap, 40%)**
> Review: `06-rag`, `09-function-calling`, `12-guardrails`

### 3. Personalized path table

Read hour estimates from `ROADMAP.md` (`(~N hours)` per phase heading). Build:

```markdown
| Phase | Name | Status | Est. Hours |
|-------|------|--------|------------|
|  0    | Setup & Tooling | Review (env) | ~14 |
|  1    | Math Foundations | Review | ~23 |
|  2    | ML Fundamentals | Skip | -- |
...
```

Rules:

- **Skip** → `--` hours (excluded from total).
- **Review / Gap / Weak / Do** → full phase hours from ROADMAP.
- Sum **Review + Gap + Weak + Do** hours → show total: `Your personalized path: ~X hours across Y phases.`

### 4. Answer key (missed only)

For each wrong answer:

```
Q: [short prompt]
Your answer: B · Correct: C — [option text]
Why: [explanation from bank]
Study: phases/07-transformers-deep-dive/02-self-attention-from-scratch/
```

### 5. Write `placement-profile.json` (required)

Persist results so `/check-understanding` can continue the same learning path.

Path: `.cursor/skills/placement-profile.json`

```json
{
  "schema_version": 1,
  "updated_at": "<ISO-8601>",
  "source": "find-your-level",
  "find_your_level": {
    "session_mode": "standard",
    "questions_asked": 18,
    "entry_phase": 7,
    "total_path_hours": 142,
    "phases": {
      "11": {
        "name": "LLM Engineering",
        "dir": "11-llm-engineering",
        "mastery_pct": 40,
        "status": "Gap",
        "questions_asked": 2,
        "lessons_to_review": ["06-rag", "09-function-calling"],
        "missed_question_ids": ["P11-D2-01", "P11-D3-01"]
      }
    }
  },
  "check_understanding": {},
  "check_queue": [11, 7, 3],
  "completed_checks": []
}
```

**`check_queue` rules** (ordered weakest first):

1. Include every phase with status **Gap** or **Weak**.
2. Include **Review** phases only if mastery < 60%.
3. Sort by `mastery_pct` ascending; tie-break by lower phase number.
4. Cap queue at **5** phases (user can run more manually later).
5. Exclude phases with status **Strong**.

Tell the user explicitly:

> Profile saved to `.cursor/skills/placement-profile.json`.
> Deep-dive queue: Phase 11 → Phase 7 → Phase 3.
> Run **`/check-understanding 11`** to start (or `/check-understanding` with no args).

### 6. Next steps (offer four choices)

Use **AskUserQuestion**:

1. **Start deep dive now** — invoke `/check-understanding <first in check_queue>`.
2. **Open entry phase** — lesson 01 of `entry_phase`.
3. **Review weak lessons only** — list `docs/en.md` paths from profile.
4. **Retake placement** — new adaptive session (merge into profile; do not delete prior `check_understanding` history).

If the user picks (1), hand off immediately: load `check-understanding` skill behavior for that phase, passing the profile context (weak lessons + missed IDs).

## Quality Rules

- Every question must map to a **real lesson slug** in this repo.
- Wrong options must be plausible to someone who skimmed the field but didn't study the course.
- Do not use generic ML trivia absent from lesson docs.
- Prefer bank questions over improvised ones.
- On retake, prioritize **unused** bank IDs; only repeat after >80% of bank exhausted.

## Phase Directory Map

Load from `.cursor/skills/shared/phase-map.json` (field `dir` for each phase `id`).

## Maintainer Notes

To expand the bank: add entries to `question-bank.json` with unique `id`,
increment `total_questions`, and pull stems from lesson `quiz.json` + `docs/en.md`.
Target ≥3 questions per core phase (1, 2, 3, 7, 10, 11, 14) across difficulty tiers.
