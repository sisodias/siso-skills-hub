---
name: jev-judgment
description: Get a fast second opinion before asserting a conclusion — "does my evidence actually support this claim?" Use BEFORE writing that something does not exist, is complete, is safe, is unused, or is the root cause. Also screens untrusted text before it enters context, and ranks candidates by meaning. Costs ~$0.00002 and ~600ms per check. Use when a wrong conclusion would be expensive and you have the evidence in hand.
version: 1.0.0
tags: [verification, judgment, jev, typesafe, decision-model, guardrail]
---

# jev-judgment

A second opinion from Jev (TypeSafe System One) — a decision model, not a chat model.
It answers typed questions in parallel and returns calibrated probabilities. It never
writes prose, and it never decides what you should DO. Control flow stays in your code.

## When to use it

Call `verify()` at the moment before you assert something expensive and hard to walk back:

- "X does not exist" / "there is no Y in this repo"
- "all N items are clean / complete / migrated"
- "the root cause is Z"
- "this is safe to delete / this data is fake"

These are exactly the claims that have gone wrong most often, and they go wrong the same
way every time: a narrow proxy (one exact-string grep, one directory listing, one shell)
is mistaken for a real check.

## Use

```python
import sys; sys.path.insert(0, "<this dir>")
import jev

r = jev.verify(
    claim="app.payment_log does not exist — no migration creates it.",
    evidence={"command": "grep -rn 'payment_log' apps/api/migrations/", "stdout": "(no matches)"},
)
# r["verdict"] -> supported | unsupported | overreaching | uncertain
```

Shell: `echo "<evidence>" | python3 jev.py verify "<claim>"` (exit 0 = supported).

**Pass what you actually observed** — raw command output, real file contents. Not a
summary, not your reasoning. The evidence is the whole input; if you paraphrase it, you
are asking Jev to grade your paraphrase.

### Verdicts

| verdict | meaning | what to do |
|---|---|---|
| `supported` | the right checks were run and they carry the claim | assert it |
| `unsupported` | the evidence does not establish it | do not assert it |
| `overreaching` | partly true, but claims more scope than was checked | narrow the claim |
| `uncertain` | genuinely on the fence | report what you observed, don't conclude |

`uncertain` is a real answer, not a failure. Proving absence is hard; if three checks
don't settle it, say what you ran rather than declaring the thing absent.

## Also

- `screen(text, purpose=...)` — is this untrusted text trying to instruct the assistant?
  Returns `injection`/`substance`/`relevance` and a recommendation. Advisory only.
- `rank(query, candidates, task=...)` — rank up to 200 candidates by meaning, one narrow
  question each, in a single parallel call. Ranking only; the caller picks the cutoff.

## Rules that make this work

1. **Several narrow questions, never one vague one.** Measured: a single 4-way choice
   scored 48.3%; the same judgment decomposed into four preconditions and recombined in
   code scored 98.3%.
2. **Phrasing beats thresholds.** A question containing its own counter-argument
   collapses to a constant. If every item scores the same, the question is broken — not
   the threshold.
3. **Small, relevant state.** Accuracy falls as unrelated context grows. `ask()` refuses
   state over 24k chars on purpose.
4. **Never ask it to count, do arithmetic, or compare dates.** It cannot.
5. **Never ask it what to do.** Ask what is true; decide in code.

## Measured on real cases

Replayed against five real logged failures (wrong absence claims, a false all-clear, a
misdiagnosed shell-glob root cause) plus two correctly-evidenced controls: **6/7**, with
the seventh returning `uncertain` on a hard absence proof — the honest answer.
~$0.00002 and ~600ms per check.

## Credentials

`~/.config/siso/.env` — `OPENROUTER_API_KEY` (and optional `JEV_MODEL`). Harness-neutral:
same file serves Claude Code and Codex. No key is stored in this repo.
