# `quiz.json` 覆盖审计 — 149 节课缺失

只读调查，未改动任何被审计的代码。日期 2026-10-10。

## 1. 事实

- `phases/` 共 523 个课节目录，**374 有 `quiz.json`，149 缺**。
- `certifications/claude/lessons` 33/33 齐；`certifications/mcpa/lessons` 34/34 齐。
- `projects/*/stages/*` 不是 quiz 表面（`projects/` 下 0 个 `quiz.json`；stage 交付 `docs/`、`starter/`、`tests/`）。

| Phase | 缺 | 明细 |
|---|---|---|
| 06 speech-and-audio | 17 | 全部 01–17 |
| 07 transformers-deep-dive | 15 | 01, 03–16 |
| 08 generative-ai | 15 | 01–14, 19 |
| 09 reinforcement-learning | 12 | 全部 01–12 |
| 10 llms-from-scratch | 13 | 09, 13–22, 25, 34 |
| 12 multimodal-ai | 25 | 全部 01–25 |
| 13 tools-and-protocols | 7 | 02–05, 19–21 |
| 15 autonomous-systems | 22 | 全部 01–22 |
| 16 multi-agent-and-swarms | 23 | 02, 04–25 |
| **合计** | **149** | |

其余 11 个 phase（00、01、02、03、04、05、11、14、17、18、19）全齐。

## 2. 完整缺失清单

```text
06-speech-and-audio:        01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17
07-transformers-deep-dive:  01 03 04 05 06 07 08 09 10 11 12 13 14 15 16
08-generative-ai:           01 02 03 04 05 06 07 08 09 10 11 12 13 14 19
09-reinforcement-learning:  01 02 03 04 05 06 07 08 09 10 11 12
10-llms-from-scratch:       09 13 14 15 16 17 18 19 20 21 22 25 34
12-multimodal-ai:           01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
13-tools-and-protocols:     02 03 04 05 19 20 21
15-autonomous-systems:      01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22
16-multi-agent-and-swarms:  02 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25
```

（`13/01` 已由本次会话补写，故不在此列表。）

## 3. 是"有意不补"吗 — 不是

逐条证据：

1. **ROADMAP 状态**：把 ROADMAP.md 的 523 行课表与磁盘对照，**149 节全部是 `✅ Complete`**，
   0 个 `🚧 In Progress`、0 个 `⬚ Planned`。它们是"已完成的课缺了一份交付物"，不是"没做完的课"。
2. **契约明文要求**：`AGENTS.md` 的 "New-lesson onboarding" 第 4 步写着
   `# 4. Write quiz.json with the schema above.` —— 新课必须带 quiz。
3. **但创作入口没跟上**：`LESSON_TEMPLATE.md` 的目录树只有 `code/ notebook/ docs/ outputs/`；
   `scripts/scaffold-lesson.sh` 也只 `mkdir` 这四个目录。**两者都不产生 `quiz.json`。**
   → quiz 契约是**后来加进 AGENTS.md 的**，没有回填到更早的模板与脚手架。
4. **缺失形状是分批的**：07 缺 15/16、10 缺 13/24、13 缺 7/31、16 缺 23/25 —— 部分缺、
   且缺的往往是相邻的一段。这是"分批补写"的指纹，不是"按 phase 决定不做"。
5. **工具链是"优雅降级"而非"不需要"**：`scripts/audit_lessons.py` 的 `check_quiz()` 开头就是
   `if not quiz.is_file(): return`；`build_catalog.py` 记 `has_quiz: quiz_path.is_file()`；
   `build_book.py` 用同一个条件决定书里要不要写"本章测验"。给一个功能加兼容分支，是它
   "内容早于功能"的常规做法，不是"这个功能不重要"。
6. **上游没人报过**：仓库 issue 里 quiz 相关的一大批（#239 / #240 / #368 答案位置、
   #281 长度偏置仍 open、#319 / #321 / #409），**没有一条是"缺 quiz"**。
   → 更像**盲区**，不是"已知并有意保留"。

## 4. 补了有什么用 — 有可点名的消费方

| 消费方 | 缺 quiz 的后果 |
|---|---|
| `skills/learn/SKILL.md` | Step 1 热身题、Step 3 课后测验、Step 4 "低于 70% 进 Review queue" **全部无处可取**。本次会话在 13/01 就撞上了，只能现场补一份 |
| `site/build_catalog.py` | 这 149 节在网站上没有测验入口（`has_quiz: false`） |
| `book`（`build_book.py`） | 书里这些章节没有"本章测验"那一行 |
| `learning-paths/*.json` | `13/05-tool-schema-design` 被 **5 条路径**引用：`agentic-ai-engineer`、`ai-developer-relations-engineer`、`software-engineering-fundamentals` 把它列为**正式课时**；`agent-skills`、`model-context-protocol` 把它列为**前置**。`13/19`、`13/20` 是 MCP 路由某可选课的前置。走这些路径的人会在同一处卡住 |
| `skills/check-understanding/SKILL.md` | **不受影响** —— 它是从 `docs/en.md` 现场出题，不读 `quiz.json`（别夸大） |

## 5. 成本与风险

- 总量 149 节 × 6 题 = **894 道题**（1 pre + 3 check + 2 post）。
- 社区对 quiz 质量很敏感（见第 3 节第 6 条的那些 issue）。机械生成极易复发"正确答案偏长"
  那类偏置；`check_quiz_bias.py` 的全局上限虽然松（`BASELINE_RATE = 0.84`），人工评审不松。
- `AGENTS.md` 硬规则 1 要求**一节一个 commit**，149 节 = 149 个 commit。
- 作者**不能自选答案位置**：`scripts/debias_quizzes.py` 会按 `path + 题面` 的哈希种子重排选项
  并改写 `correct`。写完必须跑它，否则 `debias_quizzes.py --check` 直接 FAIL。

## 6. 建议

**分两档，不要一次做 149。**

- **值得立刻做**：`13/02`–`13/05`。4 节、4 个 commit、1 个小 PR。理由：都在你自己的学习路径上；
  其中 `13/05` 被 5 条学习路径引用；每道题你都能负责。
- **其余 145 节**：集体价值高、对你个人低。它更像 upstream 的 backlog，适合开 issue 讨论，
  不适合由单个学习者扛下来。

**动手前先开 issue**，把第 1、3 节的证据贴上去，问一句这是"待回填"还是"有意不做"。
如果回复是后者，你就省了 149 个 commit。

### issue 草稿

> **Title:** `quiz.json` missing for 149 lessons that ROADMAP marks ✅ Complete — backfill plan?
>
> Cross-referencing ROADMAP.md (523 lesson rows parsed) against the filesystem: 374 lessons ship a
> `quiz.json`, **149 do not**, and all 149 are marked `✅ Complete`. Missing by phase: 06 (17/17),
> 07 (15/16), 08 (15/15), 09 (12/12), 10 (13/24), 12 (25/25), 13 (7/31), 15 (22/22), 16 (23/25).
>
> `AGENTS.md` step 4 of "New-lesson onboarding" requires `quiz.json`, but neither
> `LESSON_TEMPLATE.md` nor `scripts/scaffold-lesson.sh` creates one, so this looks like contract
> drift rather than a deliberate omission. `scripts/audit_lessons.py` currently returns early when
> the file is absent, so CI does not flag it.
>
> Downstream impact: `skills/learn` has no warm-up, no post-quiz and cannot populate the Review
> queue for these lessons; `site` renders no quiz entry (`has_quiz: false`); the book chapter has no
> "chapter quiz" line. `13/05-tool-schema-design` is referenced by five `learning-paths/*.json`
> entries (three as a lesson, two as a prerequisite).
>
> Question: is the intent to backfill, or are these phases intentionally quiz-free? If backfill is
> wanted, is a phase-scoped PR (one commit per lesson, per the hard rule) the preferred shape?
