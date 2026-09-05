---
name: writeback
description: Append an exact owner handoff line to a repository log and mirror it to the Agent Zero ledger.
version: 1.0.0
---

# Owner writeback mirror

This atomic capability complements the existing v1 `owner-writeback` adapter. Use it when the caller already has the exact indexed line (including any structured `[p5:v1:...]` payload) and needs that line appended to `<repo>/.agents/owners.log` and mirrored byte-for-byte to `<a0-root>/ledger/OWNERS.md`.

From this skill directory, run `python3 scripts/writeback.py --repo PATH --a0-root PATH --entry 'time · OWNER · what · path'`. (The Hub-level behavioral test is separately run as `python3 scripts/test_writeback.py` from the Hub root.) The entry is one bounded line: four nonempty fields, an ISO8601 timestamp with timezone, and an uppercase bounded owner. The script does not generate time, decode or trust the `what` payload, consult status databases, or execute user-supplied pointers.

The local append is durable before the mirror is attempted. Retries of the same entry are idempotent, including existing ledger lines prefixed with `- ` (legacy semantic dedupe; a newly written mirror line is otherwise byte-identical to the local line). A failed mirror leaves the local line durable and reports “mirror pending”; rerun the exact entry to complete it. The shared `<ledger>.p5.lock` is acquired with exclusive-create and never stolen. Partial tails, symlinks, non-regular files, oversized logs, malformed entries, and escaped targets are rejected. No observer/completion labels, timers, hooks, provider actions, or remote operations are part of this skill.

Verify the focused behavior with `python3 scripts/test_writeback.py`; commit the repository and ledger in the authorized workflow.
