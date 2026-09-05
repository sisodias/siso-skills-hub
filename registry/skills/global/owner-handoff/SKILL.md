---
name: owner-handoff
description: Check readiness for an explicitly adopted owner handoff using durable preservation, cold readback and single-writer release gates.
---

# P4 — handoff readiness adapter

The composed procedure lives in Agent Playbook's `docs/OWNER-CONTINUITY.md`; its
gate is `bin/owner-handoff-check.mjs`. Resolve that owning checkout through the
project entrypoint. Do not duplicate the workflow or run its whole-stack installer.

Where the project explicitly adopted every-two-compactions continuity, record
observed event identities in its owner-local handoff history. Two events mean
handoff is due, not permission to kill a runtime. Inspect actual effective hooks;
missing wiring is unverified, not a reason to toggle global settings blindly.

Use the existing owner, one read-only successor on the verified same route, and
a short durable checkpoint. The successor may ask at most one question. Preserve
dirty/index state, source/recovery pointers and in-flight operations; do not force
a clean tree. Require matching evidence hashes, completed cold readback, resolved
questions and the responsible owner's semantic acceptance before release.

The gate performs no runtime mutation. Re-resolve exact old/successor identities
before any explicitly coordinated close; keep the successor read-only until the
old writer relinquishes the role. Never archive/delete the old thread or stop
unrelated services. Failed cold reads retain the original owner.
