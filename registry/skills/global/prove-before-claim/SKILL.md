---
name: prove-before-claim
description: Verify live-state, completion, and changed-contract claims with the smallest applicable probe while reusing existing evidence.
---

Verify a claim when it describes a live state, completed action, external side effect, or a
changed data/API/config shape. Load this skill after a success report from a worker or when
the source of truth is available. Do not load it for design choices, product trade-offs,
explicit uncertainty, or predictions with no available oracle.

## Claim check

Name the claim and the smallest artifact or behavior that could falsify it. Reuse source,
test, receipt, deployment, or UI evidence while the relevant inputs and live state are
unchanged. Refresh only stale or changed evidence. If the evidence is unavailable, say
`UNVERIFIED` and identify the concrete gap. A labelled hypothesis is allowed; it does not
require a new probe or a proof ritual for every sentence.

| Claim kind | Evidence to inspect |
| --- | --- |
| File, code, or configuration state | The named source file, parsed config, or focused test result |
| Process, deployment, capture, or external side effect | The authoritative service receipt, current status, or persisted output |
| UI or browser state | The current rendered artifact or screenshot tied to the acceptance criterion |
| Worker or tool completion | The output artifact, receipt, or host state; a self-report alone is insufficient |
| Changed schema, API, event, IPC, stored-data, or config shape | Bounded producers and consumers that may still speak the old shape |

For a changed contract, check only relevant compatibility surfaces: running readers,
old-payload producers, persisted values, and downstream consumers of renamed or removed
fields. Show a migration, shim, dual-read, or confirmed-unused result where applicable.
Code-internal consistency alone does not prove compatibility.

Respect authority and privacy boundaries. Use the project’s approved artifact or UI surface,
do not inspect secrets or private payloads, and do not treat a worker report as authority
when an external source of truth exists. Preserve the distinction between `BLOCKED` (the
truth could not be observed) and `FAIL` (the observed result is wrong).
