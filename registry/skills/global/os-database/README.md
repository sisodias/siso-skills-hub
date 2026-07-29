# os-database — SISO Agent OS Database

## Location

```
~/.SystemDB/siso_system.db
```

**DB path is configured via `_shared_config.py`**, which reads from `config.json` or environment variable `SISO_SYSTEM_DB`. All scripts in `scripts/` use this shared config.

## Schema Overview

**23 tables** with proper foreign key constraints. The DB follows a hierarchical model:

```
workspaces
  └── projects              (workspace -> projects)
        └── missions          (project -> missions)
              └── goals         (mission -> goals)
                    └── tasks     (goal -> tasks, also project-level)
                          ├── task_relationships    (task <-> task)
                          ├── custom_field_values   (task -> custom field values)
                          ├── artifacts             (task -> file artifacts)
                          ├── memories              (task -> agent memories)
                          └── timeline_events       (task -> event log)

agents
  ├── agent_permissions     (agent -> allowed tools)
  ├── sessions              (agent -> session history)
  ├── skill_events          (agent -> skill telemetry)
  └── memories              (agent -> memories)

automations
  └── automation_logs       (automation -> execution log)

custom_fields + custom_field_definitions  (parallel tables)
task_templates
execution_logs
observability_events         (claude-code-telegram hook events)
tools
```

## Tables

### Core Entity Tables

| Table | Rows | Description |
|-------|------|-------------|
| `agents` | 21 | All registered agents — `id`, `role`, `department`, `status`, `root_path`, `health_score`, `token_budget_limit`, `tokens_used_lifetime` |
| `projects` | 5 | Work projects — `id`, `name`, `status`, `workspace_id`, `parent_project_id` (self-referential hierarchy) |
| `workspaces` | 1 | Top-level containers — `WS-MAIN` at `${SISO_WORKSPACE}` |

### Task System

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `tasks` | The core work unit | `id`, `title`, `status`, `priority` (INTEGER, higher=more urgent), `assigned_agent_id`, `blocked_by_task_id`, `parent_task_id`, `goal_id`, `project_id`, `executive_summary`, `tokens_burned`, `started_at`, `completed_at` |
| `missions` | Groups goals under a project | `project_id`, `name`, `status`, `target_completion_date` |
| `goals` | Goals within a mission | `mission_id`, `name`, `success_criteria`, `status` |
| `task_relationships` | Non-hierarchical task links | `from_task_id`, `to_task_id`, `relationship_type` (freeform string) |

### Agent Activity

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `timeline_events` | Agent event log | `agent_id`, `task_id`, `event_type`, `message`, `metadata`, `timestamp` |
| `sessions` | Agent session runs | `agent_id`, `task_id`, `run_number`, `status` (`running`/`completed`/`crashed`/`timeout`), `tokens_used` |
| `skill_events` | Skill telemetry | `skill_id`, `agent_id`, `duration_ms`, `success`, `input_size`, `output_size` |
| `memories` | Agent memories | `agent_id`, `task_id`, `type`, `content` |

### Metadata & Configuration

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `custom_fields` | Custom field definitions | `field_key`, `name`, `field_type`, `is_global`, `project_id`, `options` (JSON) |
| `custom_field_definitions` | Parallel field def table | Same schema as `custom_fields` — some scripts use one, some the other |
| `custom_field_values` | Per-task custom field values | `task_id`, `field_id`, `value` (JSON) |
| `task_templates` | Reusable task templates | `name`, `title_template`, `description_template`, `default_priority`, `default_tags`, `subtasks_template` (JSON array) |
| `automations` | Automation rules | `trigger_event`, `trigger_condition` (JSON), `action_type`, `action_config` (JSON), `enabled` |
| `automation_logs` | Automation execution log | `automation_id`, `trigger_data`, `action_result` |

### Observability & Artifacts

| Table | Description | Key Columns |
|-------|-------------|-------------|
| `artifacts` | File artifacts from tasks | `task_id`, `artifact_type`, `file_path` |
| `execution_logs` | Pipeline step records | `step_id`, `session_id`, `action_type`, `details` |
| `observability_events` | Telegram hook events | `source_app`, `session_id`, `hook_event_type`, `payload` |
| `tools` | Tool registry | `name`, `description`, `parameters_schema` (JSON), `is_global` |
| `agent_permissions` | Per-agent tool grants | `agent_id`, `tool_id` |

## Foreign Key Constraints

```
tasks.assigned_agent_id      -> agents.id
tasks.created_by_agent_id    -> agents.id
tasks.parent_task_id         -> tasks.id          (subtask hierarchy)
tasks.blocked_by_task_id     -> tasks.id          (blocking chain)
tasks.goal_id               -> goals.id
tasks.project_id            -> projects.id
projects.parent_project_id   -> projects.id        (project hierarchy)
projects.workspace_id        -> workspaces.id
missions.project_id          -> projects.id
goals.mission_id            -> missions.id
sessions.agent_id           -> agents.id
sessions.task_id            -> tasks.id
timeline_events.agent_id     -> agents.id
timeline_events.task_id     -> tasks.id
memories.agent_id           -> agents.id
memories.task_id            -> tasks.id
agent_permissions.agent_id  -> agents.id
agent_permissions.tool_id   -> tools.id
custom_field_values.field_id -> custom_fields.id
custom_field_values.field_id -> custom_field_definitions.id
automation_logs.automation_id -> automations.id
artifacts.task_id           -> tasks.id
execution_logs.session_id   -> sessions.id
```

## Scripts

All scripts live in `scripts/` and use `_shared_config.py` for DB access. Run any script with `--help` to see usage.

### Task CRUD
- `create_task.py` — Create task (BEGIN IMMEDIATE for race-condition safety)
- `update_task.py` — Update status, fields, assignment
- `get_my_tasks.py` — Tasks assigned to current agent (pre-fetches blocking tasks)
- `get_task_with_subtasks.py` — Task + all subtasks
- `archive_task.py` / `unarchive_task.py` — Archive management
- `list_archived.py` — List archived tasks
- `search_tasks.py` — Full-text search (title, description, executive_summary)
- `query_context.py` — Task → Goal → Mission → Project hierarchy

### Subtasks & Hierarchy
- `add_subtask.py` / `create_subtask.py` / `delete_subtask.py`
- `toggle_subtask.py` — Mark subtask complete
- `list_subtasks.py` — List subtasks of a task

### Blocking & Dependencies
- `is_blocked.py` — Check if task is blocked
- `unblock_task.py` — Remove blocking relationship
- `add_blocked_by.py` — Add a blocking task
- `list_blocking_tasks.py` — Tasks blocking a given task
- `find_blocked_chain.py` / `find_blocking_chain.py` — Traverse dependency chains
- `detect_cycle.py` — Detect circular dependencies
- `propagate_unblock.py` — Auto-unblock dependents when blocker completes

### Custom Fields & Tags
- `add_field.py` — Define a custom field
- `query_by_field.py` — Query tasks by custom field value
- `set_field.py` — Set custom field value (INSERT ON CONFLICT upsert)
- `add_tag.py` / `remove_tag.py` — Tag management
- `list_tags.py` — All tags in use

### Templates & Automation
- `create_template.py` — Create a task template
- `use_template.py` — Create task from template (placeholder substitution `{{field}}`)
- `list_templates.py` — All templates
- `create_automation.py` — Automation rule (event + condition → action)
- `toggle_automation.py` — Enable/disable
- `run_automations.py` — Run automations for an event
- `list_automations.py` — All automations

### Time & Estimates
- `estimate_task.py` — Set `estimated_minutes`
- `track_time.py` — Start/stop timer (uses `started_at` + `time_spent` columns)
- `time_report.py` — Estimate vs actual for one task
- `compare_estimates.py` — Aggregate comparison across tasks
- `update_urgency.py` — Recalculate urgency scores (0-100) for all tasks

### Session & Events
- `init_session.py` — Boot agent, create session record
- `log_event.py` — Log timeline event (BOOT, THOUGHT, ACTION, COMPLETED, ERROR, HANDOFF)
- `log_hook.py` — External hook script
- `recent_events.py` — Timeline events by time window (e.g. `5m`, `2h`, `24h`, `7d`)
- `task_notes.py` — Add/view notes on a task

### Filtering & Status
- `bulk_update.py` — Bulk update by filter
- `ready_tasks.py` — Unblocked tasks with no future due date
- `get_tasks_with_tags.py` — Tasks with computed virtual tags (BLOCKED, OVERDUE, WEEK, READY)
- `relate_tasks.py` / `remove_relationship.py` — Task relationship management

## Migrations

Migration scripts in `migrations/`. Run in order:

```bash
python3 migrations/001_add_missing_tables.py
```

Check `migrations/` for additional migrations as schema evolves.

## Tests

```bash
cd skills_hub/registry/skills/global/os-database
pytest tests/ -v
```

- `test_scripts.py` — 51 scripts pass `--help` validation, grouped by functional area
- `test_schema.py` — Core table existence and required column validation

## Quick Query Reference

```sql
-- Active tasks for an agent
SELECT * FROM tasks WHERE assigned_agent_id = 'PM_Agent' AND status != 'completed';

-- Blocked tasks
SELECT t.* FROM tasks t WHERE t.blocked_by_task_id IS NOT NULL;

-- Full task context
SELECT t.title, t.status, a.title as agent, p.name as project
FROM tasks t
JOIN agents a ON t.assigned_agent_id = a.id
JOIN projects p ON t.project_id = p.id
WHERE t.id = 'TASK-001';

-- Recent agent activity
SELECT * FROM timeline_events
WHERE agent_id = 'PM_Agent'
ORDER BY timestamp DESC LIMIT 20;

-- Session summary by status
SELECT agent_id, status, COUNT(*) FROM sessions GROUP BY agent_id, status;

-- Task tree (subtasks)
SELECT t.id, t.title, p.title as parent
FROM tasks t
JOIN tasks p ON t.parent_task_id = p.id;
```

## Key Enums

| Column | Values |
|--------|--------|
| `tasks.status` | `pending`, `in_progress`, `blocked`, `completed`, `cancelled` |
| `sessions.status` | `running`, `completed`, `crashed`, `timeout` |
| `timeline_events.event_type` | `BOOT`, `THOUGHT`, `ACTION`, `COMPLETED`, `ERROR`, `HANDOFF` |
| `automations.action_type` | `log`, `alert`, `escalate` |
| `tasks.priority` | INTEGER (higher = more urgent; scripts map 1=low, 2=medium, 3=high, 4=critical) |

## Schema Notes

- `tasks.priority` is INTEGER — higher number = more urgent
- `custom_fields` and `custom_field_definitions` are parallel tables with identical schemas — some scripts write to one, some to the other. Consider consolidating.
- `task_relationships.relationship_type` is freeform — no enforced enum
- `automations.trigger_condition` and `action_config` are JSON strings
- `task_templates.subtasks_template` is a JSON array of subtask titles
