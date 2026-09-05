---
name: owner-writeback
description: Persist a material project-owner checkpoint and append its discoverable pointer using the project's existing durable writeback adapter.
---

# P5 — material owner writeback

Read the project's normal entrypoint and resolve its existing handoff, stable
owner/thread identity and writeback adapter. If no adapter is present, report that
boundary; do not invent another registry, planner or shared task queue.

Write your own checkpoint: intent, current work, actual output/evidence, failed
or unperformed checks, and next owned/unallocated/decision-bound needs. Never turn
working/idle badges into acceptance. Do not rewrite another owner's handoff.

For the `agent-zero-handover.mjs` adapter, prepare its bounded JSON input and read
the existing handoff SHA. Run `writeback --handoff <workspace-relative-path>
--owner <owner> --thread <thread> --expect-sha <sha> --input <local-json>`.
Then append through `index-append` using the same identity/handoff and its **new**
SHA. Failure of the second step does not undo successful durable writeback; record
that the index still needs an append. Retry the same checkpoint idempotently.

The index remains append-only: `time · OWNER · what · path`. Observer seeds must
be attributed as observations, never owner-authored completion. Cold heads can
use `recover-index` first, then read relevant handoff/evidence and live identity
before acting. Index-only recovery does not verify current source hashes or
discover undeclared tasks. Private state stays in the consuming workspace.

Use a material boundary, not every tool call or a timer. No mandatory ACK or
parallel edits to a central queue; preserve every existing ledger line.
