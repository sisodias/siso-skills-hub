# Phase 1 Progress — Skills Hub Telemetry

**Goal:** Build telemetry pipeline + health scores. Turn the skills hub into a data-driven system.

---

## Checklist

### PH1-T1: Telemetry Pipeline (DB schema + SDK + CLI)
- [x] `skill_events` table schema
- [x] `skills_telemetry.py` SDK
- [x] CLI integration (install, validate, search, info)
- [x] Telemetry logged to database

**Status:** [DONE]
**Owner:** telemetry-dev
**Deliverable:** `scripts/skills_telemetry.py`, SQL schema, CLI integration

---

### PH1-T2: Health Scores + `skills hub health`
- [x] `skills hub health` command
- [x] Health score computation (usage × success × latency × diversity)
- [ ] `health` field added to registry entries

**Status:** [DONE]
**Owner:** health-dev
**Deliverable:** `skills hub health` command

---

### PH1-T3: Agent Runtime Telemetry Integration
- [x] Find agent skill invocation points
- [x] Add `track()` calls to agent skill usage
- [x] Document agent telemetry integration points

**Status:** [DONE]
**Owner:** runtime-dev
**Deliverable:** Patched agent invocation layer

**Phase A findings:**
- 3 distinct invocation patterns identified (subprocess scripts, SKILL.md with `${CLAUDE_SKILL_DIR}`, hook-based lifecycle)
- Skills invoked via `python3 .claude/skills/<skill>/scripts/<script>.py <args>`
- Key integration point: `.claude/hooks/hooks.json` lifecycle events + skill activation hook

**Phase B deliverables:**
- `scripts/agent_skill_tracker.py` — wrapper script created and tested
- `docs/AGENT_INTEGRATION.md` — full integration doc
- `docs/AGENT_SKILL_INVOCATION.md` — invocation patterns documented

---

### PH1-T4: Tracking Doc + Ecosystem Integration Review
- [x] Phase 1 progress tracked here
- [x] os-database vs skills_hub schema decision
- [x] Agent skill reference pattern review
- [x] Ecosystem changes identified
- [ ] STRATEGIC_ROADMAP.md updated

**Status:** [DONE]
**Owner:** integration-review
**Deliverable:** This doc + updated STRATEGIC_ROADMAP.md

**Ecosystem findings:**
- Telemetry lives in skills_hub (skill_events table), NOT os-database (which owns timeline_events)
- os-database owns task/task-events domain; skills_hub owns skill-invocation domain — clean separation
- 23 skills in registry; skill invocation happens via subprocess (scripts) and SKILL.md (agent execution)
- No structural changes needed for Phase 1 telemetry; agent wrapper script sufficient

---

## Notes

- Telemetry schema: `event_id, skill_id, agent_id, session_id, timestamp, duration_ms, success, error_type, context_hash, input_size, output_size`
- Health score formula: `health = usage_freq_percentile * success_rate * latency_score * context_diversity`
- Telemetry SDK: `from skills_telemetry import track; track("websearch", success=True, duration_ms=150)`
- **DB Consolidation (2026-03-19):** `skill_events` table moved from `skills_hub/data/skill_events.db` into `~/.SystemDB/sisostem.db` for cross-domain query capability

---

## Phase 1 Complete When

All 4 tasks show [DONE]. `skills hub health` returns scores for all 23 skills. Agent invocations are logged.
