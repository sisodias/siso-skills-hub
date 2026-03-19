# os-database Skill

Core Agent OS Database API for Claude Code agents.

## Structure

```
os-database/
├── SKILL.md           # Claude Code entrypoint
├── config.json        # Agent identity (edit before use)
├── state.json        # Session state (auto-managed)
├── schema.sql        # Database schema reference
├── requirements.txt  # Dependencies (none - stdlib only)
└── scripts/
    ├── init_session.py    # Boot agent, create session
    ├── log_event.py      # Log timeline events
    ├── update_task.py    # Mark tasks done
    ├── query_context.py  # Get goal/mission hierarchy
    ├── get_my_tasks.py   # List assigned tasks
    └── create_subtask.py # Break down work
```

## Quick Start

1. **Edit config.json** - Set your agent_id, role, department, root_path
2. **Boot** - Run `python3 scripts/init_session.py --task-id "TASK-001"`
3. **Log** - Use `log_event.py` constantly for timeline

## Commands

```bash
# Boot (run once)
python3 scripts/init_session.py --task-id "TASK-001"

# Log thoughts/actions
python3 scripts/log_event.py --type "THOUGHT" --msg "Reading requirements..."
python3 scripts/log_event.py --type "ACTION" --msg "Wrote auth.py"

# Get work
python3 scripts/get_my_tasks.py

# Complete task
python3 scripts/update_task.py --task-id "TASK-001" --status "completed" --summary "Done!"

# Check context
python3 scripts/query_context.py
```

## Auto-State

Scripts automatically read from:
- `config.json` - agent_id, role, db_path
- `state.json` - current_task_id, session_id (written by init_session.py)

## Event Types

| Type | Use When |
|------|----------|
| BOOT | Agent starts |
| THOUGHT | Before writing code |
| ACTION | After saving file |
| TOOL_CALL | External API |
| ERROR | Something fails |
| HANDOFF | Pass to another agent |
| COMPLETED | Task done |

## Deploy to Agent

Copy entire `os-database/` folder to:
```
agent/.claude/skills/os-database/
```

Then add to agent's CLAUDE.md:
```
## Database
Use the os-database skill for all task management.
```
