---
name: check-understanding
version: 2.0.0
description: >
  Phase-deep quiz (8 MCQs from lesson docs) for AI Engineering from Scratch.
  Reads placement-profile.json from /find-your-level to prioritize weak lessons
  and queue follow-ups. Trigger: /check-understanding [phase], "quiz me on phase N",
  "deep dive phase 11", "continue my placement queue".
tags: [assessment, quiz, curriculum, ai-engineering, placement-linkage]
---

# Check Understanding (v2 — Placement-Linked Phase Quiz)

Deep **phase-level** assessment: 8 questions drawn from `docs/en.md` and
`quiz.json` under one phase. Designed as the **second step** after
`/find-your-level` — placement finds weak phases; this skill verifies and
guides remediation lesson-by-lesson.

## Linked Skill

| Skill | Role |
|-------|------|
| `/find-your-level` | Broad adaptive placement → writes `placement-profile.json` |
| `/check-understanding <phase>` | Narrow deep quiz → updates profile + advances queue |

## Shared Files (read on every activation)

```
.cursor/skills/placement-profile.json   ← cross-skill state
.cursor/skills/shared/phase-map.json    ← phase id / dir / name / keywords
```

Fallback: `.claude/skills/…` if `.cursor/skills/…` missing.

### Profile fields this skill uses

```json
{
  "find_your_level": {
    "entry_phase": 7,
    "phases": {
      "11": {
        "mastery_pct": 40,
        "status": "Gap",
        "lessons_to_review": ["06-rag", "09-function-calling"],
        "missed_question_ids": ["P11-D2-01"]
      }
    }
  },
  "check_queue": [11, 7, 3],
  "check_understanding": {
    "11": {
      "last_score": 5,
      "last_grade": "Almost",
      "last_at": "2026-06-23T12:00:00Z",
      "attempts": 1,
      "lessons_missed": ["06-rag"]
    }
  },
  "completed_checks": [14]
}
```

## Activation

- `/check-understanding 11` · `/check-understanding llm-engineering`
- "quiz me on phase 3" · "test transformers"
- **"continue placement"** · **"next in queue"** · `/check-understanding` (no args)

## Step 0 — Load Profile & Resolve Phase

1. Read `placement-profile.json` if it exists.
2. Parse user argument:

| Argument | Action |
|----------|--------|
| **None** / "continue" / "next in queue" | If `check_queue` non-empty → use **first** phase. Else if profile has `find_your_level.entry_phase` → offer entry phase or list all 20. Else → list all 20 phases. |
| **Number 0–19** or keyword | Resolve via `phase-map.json` |
| **`--all-weak`** | Run queue sequentially (ask confirm before each phase) |

3. If profile exists for resolved phase, show brief context **before** Q1:

```
Linked from /find-your-level: Phase 11 was Gap (40% placement).
Priority lessons: 06-rag, 09-function-calling
This quiz will weight questions toward those lessons.
```

If no profile exists, proceed normally (no linkage banner).

## Step 1 — Resolve Phase Directory

Use `phase-map.json`. Validate 0–19. On unknown input, show full phase list.

## Step 2 — Read Phase Content

Glob `phases/<dir>/[0-9][0-9]-*/docs/en.md` and matching `quiz.json`.

**Priority read order when profile lists weak lessons:**

1. All `lessons_to_review` slugs from `find_your_level.phases[N]`
2. Lessons tied to `lessons_missed` from prior `check_understanding[N]` attempts
3. Representative spread: first 2, middle 2, last 2 lessons if phase has 15+ lessons
4. Otherwise read all lesson docs (or as many as context allows)

Also read `find-your-level/question-bank.json` entries for this phase — reuse
stems where they match weak lessons (rephrase options order, do not duplicate
placement session questions the user already saw in same day if IDs are known).

## Step 3 — Generate 8 Questions

| Slot | Type | Source priority |
|------|------|-----------------|
| Q1–Q4 | Conceptual (what/why) | ≥2 from weak lessons if profile exists |
| Q5–Q8 | Practical (how/build/debug) | ≥2 from weak lessons if profile exists |

Rules:

- Exactly **8** MCQs, 3–4 options each, one correct.
- Tag each: `Lesson NN: <title> (<lesson-slug>)`.
- Ground every question in lesson docs or lesson `quiz.json` — no generic trivia.
- If weak-lesson list has 1 item, still diversify across phase but weight 5/8 to that lesson + neighbors.

## Step 4 — Present One at a Time

```
Question 3/8 (Conceptual) · Phase 11 LLM Engineering
From lesson 06-rag · [Placement priority]

What is the correct order of steps in a basic RAG pipeline at query time?
A) ...
```

Use **AskUserQuestion**. No answers until end.

## Step 5 — Score

Track: correct / 8, per-lesson misses, conceptual vs practical breakdown.

## Step 6 — Grade & Interpret (with placement context)

| Score | Grade | Message |
|-------|-------|---------|
| 7–8 | **Mastered** | Ready for next phase (or capstone complete if phase 19) |
| 5–6 | **Almost** | Solid; review listed lessons |
| 3–4 | **Developing** | Revisit half the phase |
| 0–2 | **Start Over** | Work phase from lesson 01 |

**Placement reconciliation** (when profile exists):

| Placement status | Phase quiz grade | Updated recommendation |
|------------------|------------------|------------------------|
| Gap / Weak | Mastered | Upgrade phase to **Strong** in profile; remove from `check_queue`; add to `completed_checks` |
| Gap / Weak | Almost / Developing | Keep in queue; update `lessons_missed` |
| Gap / Weak | Start Over | Keep first in queue; set `entry_phase` to this phase if lower than current |
| Review | Mastered | Upgrade to **Strong**, remove from queue |
| Strong (placement) | Developing or worse | Downgrade to **Review** — placement may have been lucky |

Show one line:

> Placement said Gap (40%) → Phase quiz: Almost (6/8). Status updated to **Review**.

## Step 7 — Wrong Answer Breakdown

Same as v1 — include full path `phases/<dir>/<lesson>/docs/en.md`.

## Step 8 — Update `placement-profile.json` (required)

Merge (never discard unrelated phases):

```json
"check_understanding": {
  "<N>": {
    "last_score": 6,
    "last_grade": "Almost",
    "last_at": "<ISO-8601>",
    "attempts": 2,
    "lessons_missed": ["06-rag"],
    "conceptual_correct": 3,
    "practical_correct": 3
  }
}
```

Queue maintenance:

- **Mastered** → remove phase from `check_queue`, append to `completed_checks`
- **Almost** on last attempt (≥2) → move to back of queue
- Update `find_your_level.phases[N].status` per reconciliation table
- Set `updated_at`, `source` to `"check-understanding"`

## Step 9 — What Next? (placement-aware)

Use **AskUserQuestion** with options tailored to profile:

1. **Next in queue** — `/check-understanding` (show next phase name if queue non-empty)
2. **Retake this phase** — fresh 8 questions, avoid prior stems
3. **Study weak lesson** — open first `lessons_missed` doc path
4. **Re-run placement** — `/find-your-level` (after finishing ≥2 queue phases or user request)
5. **Explain a missed concept** — free-form tutoring on one wrong answer

If `check_queue` is empty after this session:

> Queue complete. Run `/find-your-level` to refresh your path, or start Phase {entry_phase} lesson 01.

## Rules

- Do not repeat identical questions on retake; rephrase or pull from different lessons.
- If phase has no `en.md` files: "Phase N has no lesson content yet."
- Never show correct answer before user responds.
- When both skills run in one conversation, treat profile as single source of truth.

## Phase Map

Load keywords and directories from `.cursor/skills/shared/phase-map.json`.

## Maintainer Notes

- Keep placement bank IDs in find-your-level; phase quizzes prefer lesson `quiz.json`.
- When adding phases, update `phase-map.json` once (both skills read it).
