# Agent Integration — Skills Telemetry

How to integrate skill telemetry into the agent runtime.

---

## Current State

**Telemetry SDK exists:** `skills_hub/scripts/skills_telemetry.py`
- `track(skill_id, success, agent_id, session_id, duration_ms, error_type, context)`
- Writes to `~/.SystemDB/sisostem.db` (skill_events table - migrated from separate `skills_hub/data/skill_events.db`)

**CLI has telemetry:** `skills_hub/scripts/skills` — all CLI commands (install, search, info, validate) call `track()` internally.

**Agent skill invocations are NOT yet tracked.**

---

## Agent Skill Invocation Patterns

See `AGENT_SKILL_INVOCATION.md` for full details. Summary:

1. **Subprocess scripts** (most common): `python3 .claude/skills/<skill>/scripts/<script>.py <args>`
2. **`${CLAUDE_SKILL_DIR}` substitution**: Used by websearch, gitsearch, xsearch, multisearch
3. **Hook-based lifecycle**: os-database log_hook.py for BOOT/USER_PROMPT/COMPLETED events

---

## Where to Insert Telemetry

### Option A: Wrapper Script (Recommended for Phase 1)

Create `skills_hub/scripts/agent_skill_tracker.py`:

```python
#!/usr/bin/env python3
"""Lightweight wrapper to track agent skill invocations."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from skills_telemetry import track

if __name__ == '__main__':
    skill_id = sys.argv[1]
    success = sys.argv[2].lower() == 'true'
    duration_ms = int(sys.argv[3]) if len(sys.argv) > 3 else None
    agent_id = sys.argv[4] if len(sys.argv) > 4 else os.environ.get('AGENT_ID', 'unknown')
    track(skill_id, success=success, agent_id=agent_id, duration_ms=duration_ms, context="agent_invocation")
```

**Usage:**
```bash
python3 skills_hub/scripts/agent_skill_tracker.py websearch true 150 agent-123
```

**Integration:** Prepend to any skill invocation:
```bash
python3 .../agent_skill_tracker.py <skill-id> <success> <duration-ms> <agent-id> && \
python3 .claude/skills/<skill>/scripts/<script>.py <args>
```

**Pros:** No changes to existing skill scripts. Thin layer.
**Cons:** Requires modifying agent registry documentation or wrappers.

### Option B: Modify Skill Scripts

Add `from skills_telemetry import track` to each skill script's entry point.

**Pros:** Native, no extra wrapper.
**Cons:** 23 skills to modify. Skill scripts become coupled to telemetry.

### Option C: Hook-Based Interception

Use the existing `UserPromptSubmit` hook system to intercept skill invocations. The `activate_skills.py` hook already identifies skills from prompts. Could add a companion hook that tracks skill invocations after execution.

**Pros:** Centralized, no per-skill changes.
**Cons:** Hooks fire on prompt submit, not skill completion. Hard to correlate invocation with success.

---

## Recommended Integration Points

### For Subprocess Skills (Pattern 1)

These are the highest-value targets — task management skills (os-database, pm-tasks, task-manager) that are called frequently.

**os-database scripts** (most used):
- `get_my_tasks.py` — called every session
- `create_task.py`, `update_task.py`, `log_event.py` — called multiple times per task
- `search_tasks.py`, `bulk_update.py` — periodic use

**Integration:** Add `track()` to the script entry points. Example for `get_my_tasks.py`:
```python
import sys
import os
sys.path.insert(0, "/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/scripts")
from skills_telemetry import track

if __name__ == '__main__':
    import time
    start = time.time()
    try:
        # existing script logic
        success = True
    except Exception as e:
        success = False
    finally:
        duration_ms = int((time.time() - start) * 1000)
        track("get_my_tasks", success=success, duration_ms=duration_ms)
```

### For `${CLAUDE_SKILL_DIR}` Skills (Pattern 2)

These run inside subagent contexts. The skill's `SKILL.md` defines the prompt template. The actual script invocation uses `${CLAUDE_SKILL_DIR}`.

**Integration:** Add `track()` to `scripts/perplexity_search.py` (websearch), `scripts/gitsearch.py`, etc.

Example for `perplexity_search.py`:
```python
import sys
import os
sys.path.insert(0, "/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/scripts")
from skills_telemetry import track

if __name__ == '__main__':
    import time
    start = time.time()
    try:
        # existing search logic
        success = True
    except Exception as e:
        success = False
    finally:
        duration_ms = int((time.time() - start) * 1000)
        track("websearch", success=success, duration_ms=duration_ms)
```

---

## Specific File:Line References

### os-database — highest value targets

| File | Function | Line |
|------|----------|------|
| `skills/global/os-database/scripts/get_my_tasks.py` | `if __name__ == '__main__':` | Entry point — add track() |
| `skills/global/os-database/scripts/create_task.py` | `if __name__ == '__main__':` | Entry point — add track() |
| `skills/global/os-database/scripts/update_task.py` | `if __name__ == '__main__':` | Entry point — add track() |
| `skills/global/os-database/scripts/log_event.py` | `if __name__ == '__main__':` | Entry point — add track() |
| `skills/global/os-database/scripts/search_tasks.py` | `if __name__ == '__main__':` | Entry point — add track() |

### Skill scripts with `${CLAUDE_SKILL_DIR}` pattern

| File | Skill |
|------|-------|
| `skills/data/websearch/scripts/perplexity_search.py` | websearch |
| `skills/data/xsearch/scripts/xsearch.py` | xsearch |
| `skills/devops/gitsearch/scripts/gitsearch.py` | gitsearch |
| `skills/data/multisearch/scripts/multisearch.py` | multisearch |

### pm-tasks

| File | Function | Line |
|------|----------|------|
| `skills/system/pm-tasks/scripts/pm_tasks.py` | `if __name__ == '__main__':` | Entry point — add track() |

---

## Changes Needed for Full Auto-Tracking

1. **Create wrapper script** `scripts/agent_skill_tracker.py` (Phase B deliverable)
2. **Add `track()` to top N skill scripts** (os-database, pm-tasks, websearch) — ~10 scripts
3. **Update agent registry docs** to reference wrapper usage
4. **Optional: Create a skill template snippet** that auto-adds telemetry

**No structural changes needed to the ecosystem.** The existing subprocess invocation pattern is compatible with telemetry insertion.

---

## os-database vs skills_hub Schema Decision

**Decision: Telemetry now lives in sisosystem.db, NOT in a separate file.**

**History:**
- Original decision: Separate `skills_hub/data/skill_events.db` for clean domain separation
- Consolidation decision (2026-03-19): Merged into `~/.SystemDB/sisostem.db` for cross-domain query capability

**Rationale for consolidation:**
- `skill_events.session_id` can now JOIN to `sisosystem.sessions` and `sisosystem.tasks`
- Enables: "Show me all skill invocations for task X" queries
- Single operational burden: one backup, one path, one connection
- If sisosystem goes down, you lose task tracking AND skill telemetry — both equally critical

**Implementation:** `~/.SystemDB/sisostem.db` (skill_events table) is now the canonical home for skill telemetry.
