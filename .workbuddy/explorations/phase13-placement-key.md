# Phase 13 Placement — Answer Key & Scoring Rules

**Do not show any part of this file to the learner before they submit the round it scores.**

## Answer key

| Q | Correct | Index | Source (Learning Objectives) |
|---|---|:---:|---|
| 1 | C | 2 | 01 — name who owns each step of the four-step loop |
| 2 | A | 0 | 02 — three shape differences across OpenAI / Anthropic / Gemini |
| 3 | D | 3 | 03 — correlate streamed chunks to the right tool-call id; reassemble before parsing |
| 4 | B | 1 | 04 — why constrained decoding differs from validate-after-generation |
| 5 | C | 2 | 06 — attach version, capabilities, identity to every request |
| 6 | B | 1 | 07/08 — `server/discover`; `UnsupportedProtocolVersionError` without a handshake |
| 7 | D | 3 | 09 — stdio for local child processes; Streamable HTTP for network services |
| 8 | A | 0 | 11/12 — MRTR `input_required`; retry with a fresh JSON-RPC id |
| 9 | A | 0 | 13 — stateless transport vs durable task state; `resultType: "task"` after durable creation |
| 10 | D | 3 | 15 — treat tool descriptions and metadata as untrusted data |
| 11 | B | 1 | 16/18 — PKCE, RFC 8707 resource indicators, RFC 9207 `iss` |
| 12 | B | 1 | 19 — agent-to-tool (MCP) vs agent-to-agent (A2A) |
| 13 | C | 2 | 20 — agent loop → LLM call → tool call → MCP client dispatch; redact by default |
| 14 | A | 0 | 22/24 — Skill lifecycle and three disclosure levels vs a callable tool |
| 15 | D | 3 | 25/27 — trigger precision and recall over positives, negatives, near misses |
| 16 | C | 2 | 28–31 — registry record is discovery evidence; pin provenance; detect drift |

Answer distribution — balanced 4/4/4/4:

| Letter | Questions |
|---|---|
| A | Q2, Q8, Q9, Q14 |
| B | Q4, Q6, Q11, Q12 |
| C | Q1, Q5, Q13, Q16 |
| D | Q3, Q7, Q10, Q15 |

## Question → lesson mapping

| Q | Verdict applies to |
|---|---|
| 1 | 01 The Tool Interface |
| 2 | 02 Function Calling Deep Dive |
| 3 | 03 Parallel and Streaming Tool Calls |
| 4 | 04 Structured Output · 05 Tool Schema Design |
| 5 | 06 MCP Fundamentals |
| 6 | 07 Building an MCP Server · 08 Building an MCP Client |
| 7 | 09 MCP Transports |
| 8 | 10 MCP Resources and Prompts · 11 MCP Sampling · 12 MCP Roots and Elicitation |
| 9 | 13 MCP Async Tasks · 14 MCP Apps |
| 10 | 15 MCP Security: Tool Poisoning |
| 11 | 16 MCP Security: OAuth 2.1 · 17 Gateways and Registries · 18 Auth Production |
| 12 | 19 A2A Protocol |
| 13 | 20 OpenTelemetry GenAI · 21 LLM Routing Layer |
| 14 | 22 Skills and Agent SDKs · 24 Skill Discovery and Progressive Disclosure |
| 15 | 25 Skill Invocation and Routing · 26 Skill Permissions, Sandboxes, and Trust · 27 Skill Evals, Packaging, and Portability |
| 16 | 28 Tool Contracts and Content · 29 Reliability, Cancellation, and Flow Control · 30 Registry, Supply Chain, and Drift · 31 Conformance, Versioning, and Operations |

Lesson 23 (Capstone: Tool Ecosystem) has no question. It is a synthesis lesson that
depends on the whole phase; always record it as **Deferred** — do not schedule it into a
bridge.

## Verdict rules

Per question:

- **Wrong → 必学 (Do).** Every lesson mapped to that question goes into the bridge.
- **Right → 快读 (Skim)** for rounds 1–2, **跳过 (Skip)** for rounds 3–4.

Rationale for the asymmetry: one correct answer is weak evidence about a foundational
lesson, and strong evidence about a narrow production one. Rounds 1–2 carry the Phase 14
prerequisites, so a correct answer only earns a skim; rounds 3–4 test specialisations the
learner may never need, so a correct answer earns a skip.

Fixed overrides, independent of score:

| Lesson | Status | Why |
|---|---|---|
| 01 | Do | Direct prerequisite of Phase 14 · L06 |
| 02 | Do | Direct prerequisite of Phase 14 · L06 |
| 15 | Do | Same attack class as Phase 14 · L27; needed before any non-loopback MCP bind |
| 23 | Deferred | Phase capstone; revisit after the bridge |

## Bridge ordering

When writing the bridge into `LEARNING.md`, order the resulting lessons as:

1. All enforced overrides first (01, 02).
2. Then remaining `Do` lessons in numeric order.
3. Then `Skim` lessons in numeric order, marked as skim.
4. `Deferred` and `Skip` lessons listed in one line at the end, for honesty about coverage.

## Score → bridge size (sanity check)

| Total /16 | Reading |
|---|---|
| 0–4 | The learner needs most of Phase 13. Bridge the six mandatory groups; route the rest through `learn-mcp` as a separate track. |
| 5–9 | Typical. Bridge rounds 1–2 lessons plus the missed specialisation groups. |
| 10–13 | Strong. Bridge the misses plus 01, 02, 15; skim the rest. |
| 14–16 | Phase 13 is largely known. Bridge 01, 02, 15 only and verify with `check-understanding 13` later. |
