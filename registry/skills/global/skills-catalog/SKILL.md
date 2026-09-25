---
name: skills-catalog
description: Locate the current skill or router for a capability without relying on a stale duplicated inventory.
version: 1.0.0
tags: [skills, discovery, routing, catalog]
---
# Skills catalog

This is a maintained lookup procedure, not a generated catalog. The runtime's
available-skills list and each live `SKILL.md` are authoritative.

1. Use the current available-skills list for names, triggers, and canonical paths.
2. If the requested capability is broad, enter through one router:
   - code navigation: `pb-codenav`
   - multi-agent work: `pb-orchestration`
   - research: `pb-research`
   - agent system, memory, or skill maintenance: `pb-system`
   - verification or cleanup classification: `pb-verification`
3. Read the chosen skill fully, then load only the references it routes to.
4. If a live disk inventory is genuinely needed, use the `skill` manager's list
   command. Do not copy its output back into this file.

Model and lane policy lives in `codex-subagent-routing` and the current runtime
router, not in this lookup skill.
