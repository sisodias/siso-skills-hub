# Agent Skill Invocation Patterns

How agents invoke skills in the SISO ecosystem.

---

## Pattern 1: Direct Subprocess Scripts (Most Common)

Agents invoke skills via `python3` subprocess calls to skill scripts.

**Command form:**
```bash
python3 .claude/skills/<skill-id>/scripts/<script>.py <args>
```

**Examples:**

Canonical task management (Agent Brain):
```bash
siso-brain tasks --agent my-agent
siso-brain task-create --id TASK-001 --description "Task" --agent my-agent
siso-brain task-update --id TASK-001 --status completed
siso-brain timeline --agent my-agent --type ACTION --task TASK-001 --message "Doing X"
```

Temporary PM alias (deprecated):
```bash
python3 registry/skills/system/pm-tasks/scripts/pm_tasks.py list
python3 registry/skills/system/pm-tasks/scripts/pm_tasks.py create "Task name" --priority 8
python3 registry/skills/system/pm-tasks/scripts/pm_tasks.py update TASK-001 in_progress
```

Task Manager compatibility adapter:
```bash
python3 registry/skills/system/task-manager/siso-tasks.py view-inbox --role builder
python3 registry/skills/system/task-manager/siso-tasks.py pull --role builder --claimed-by my-agent
```

**Registration:** Listed in agent's `skills/registry.md` under "Agent-Specific Skills"

---

## Pattern 2: SKILL.md with `${CLAUDE_SKILL_DIR}` Substitution

Used by AI-executable skills where the agent runs in a subagent context. The skill's SKILL.md defines the execution prompt and uses `${CLAUDE_SKILL_DIR}` for script paths.

**Command form:**
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/<script>.py "$ARGUMENTS"
```

**Examples:**

websearch:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/perplexity_search.py "$ARGUMENTS"
```

gitsearch:
```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/gitsearch.py "$ARGUMENTS"
```

xsearch, multisearch: Same pattern — `${CLAUDE_SKILL_DIR}/scripts/<script>.py "$ARGUMENTS"`

**Registration:** Listed in agent's `skills/registry.md` with the skill's SKILL.md being the source of truth

---

## Pattern 3: Hook-Based Lifecycle Logging

Agents log lifecycle events via Claude hooks that fire on session events.

**Command form:**
```bash
python3 /path/to/log_hook.py <event_type>
```

**Examples:**
```bash
python3 .../os-database/scripts/log_hook.py BOOT
python3 .../os-database/scripts/log_hook.py USER_PROMPT
python3 .../os-database/scripts/log_hook.py COMPLETED
```

**Registration:** Configured in agent's `.claude/hooks/hooks.json`

---

## Pattern 4: Skill Activation Hook

On every user prompt, a hook analyzes the prompt and suggests relevant skills.

**Script:** `hooks_hub/pipeline/skill-activation-prompt/activate_skills.py`

**Behavior:** Keyword-matches user prompt against SKILL.md files in skills_hub registry, outputs skill suggestions.

**Registration:** Triggered via `UserPromptSubmit` hook in `.claude/hooks/hooks.json`

---

## Invocation Frequency (Approximate)

| Pattern | Frequency | Example Skills |
|---------|-----------|----------------|
| Subprocess scripts | High | os-database, pm-tasks, task-manager |
| `${CLAUDE_SKILL_DIR}` | Medium | websearch, xsearch, gitsearch, multisearch |
| Lifecycle hooks | Per session | os-database (BOOT, USER_PROMPT, COMPLETED) |
| Skill activation | Per prompt | All skills (via activate_skills.py) |

---

## Skill Registry Locations

Agents maintain local skill registries at:
- `agents/<agent>/skills/registry.md` — agent's own registry
- `module_templates/agents/live/v3/skills/registry.md` — template

Skills are referenced via copy or symlink from:
- `skills_hub/registry/skills/<category>/<skill-id>/`

---

## Auto-Tracking Feasibility

**Pattern 1 (subprocess scripts):** Can wrap at the script level — add `track()` to script entry points. Or create a thin wrapper that calls the script and tracks.

**Pattern 2 (`${CLAUDE_SKILL_DIR}`):** The `${CLAUDE_SKILL_DIR}` substitution happens at SKILL.md parse time by the agent runtime. Skills run as subprocess calls within the subagent. Tracking would need to be added inside each skill's script.

**Pattern 3 (hooks):** These are already tracked in os-database timeline_events. Not skill-level telemetry.

**Pattern 4 (activation):** This is a suggestion system, not an invocation. Not tracked as skill usage.

**Recommendation:** Pattern 1 is the easiest to auto-track — a thin wrapper script at `skills_hub/scripts/agent_skill_tracker.py` that wraps subprocess calls. Pattern 2 requires modifying individual skill scripts.
