---
name: os-database
description: Core Agent OS Database API. Handles telemetry, task state, and timeline logging.
version: 1.0.0
tags:
  - database
  - telemetry
  - system
allowed-tools:
  - Bash(python3 .claude/skills/os-database/scripts/*.py)
---

# Agent OS Database

This skill connects you to the central Agent OS database.

## Structure

```
.claude/skills/os-database/
├── config.json      # Your identity (edit before use)
├── state.json      # Auto-managed session state
├── schema.sql     # DB reference for errors
├── DATABASE.md    # Full schema documentation (READ THIS)
├── scripts/        # Atomic tools
├── workflows/      # SOPs (boot, complete, subtask)
└── rules/         # Agent habits (mandatory)
```

**Read DATABASE.md first** to understand the data model.

## Rules (Must Follow)

| Rule | When |
|------|------|
| `01-secretary-reflex.md` | Always log THOUGHT/ACTION silently |
| `02-escalation.md` | Escalate after 3 failures |
| `03-context-check.md` | Verify goal before complex tasks |

## Workflows

| Workflow | When |
|----------|------|
| `boot-sequence.md` | Run first when booting |
| `complete-task.md` | Follow when finishing |
| `create-subtask.md` | Break down complex work |

## Scripts

```bash
# Boot
python3 .claude/skills/os-database/scripts/init_session.py

# Log (use constantly)
python3 .claude/skills/os-database/scripts/log_event.py --type "THOUGHT" --msg "..."

# Get work
python3 .claude/skills/os-database/scripts/get_my_tasks.py

# Search tasks
python3 .claude/skills/os-database/scripts/search_tasks.py --query "keyword"

# Create task (simple - no workspace)
python3 .claude/skills/os-database/scripts/create_task.py --project-id "PRJ-XXX" --title "Task" --description "Do X"

# Create task (deep - with workspace)
python3 .claude/skills/os-database/scripts/create_task.py --project-id "PRJ-XXX" --title "Task" --description "Do X" --workspace

# Complete
python3 .claude/skills/os-database/scripts/update_task.py --status "completed" --summary "..."

# Context
python3 .claude/skills/os-database/scripts/query_context.py

# Search tasks
python3 .claude/skills/os-database/scripts/search_tasks.py --query "keyword"

# Bulk update
python3 .claude/skills/os-database/scripts/bulk_update.py --task-ids "TASK-001,TASK-002" --status "completed"

# Archive/unarchive
python3 .claude/skills/os-database/scripts/archive_task.py --task-id "TASK-XXX"
python3 .claude/skills/os-database/scripts/unarchive_task.py --task-id "TASK-XXX"
python3 .claude/skills/os-database/scripts/list_archived.py

# Saved Contexts (saved filter/query like dstask)
python3 .claude/skills/os-database/scripts/contexts/create_context.py --name "work" --filter-query '{"project_id": "work", "status": "pending"}'
python3 .claude/skills/os-database/scripts/contexts/list_contexts.py
python3 .claude/skills/os-database/scripts/contexts/use_context.py --name "work"

# Tags
python3 .claude/skills/os-database/scripts/add_tag.py --task-id "TASK-XXX" --tag "bug"
python3 .claude/skills/os-database/scripts/remove_tag.py --task-id "TASK-XXX" --tag "bug"
python3 .claude/skills/os-database/scripts/list_tags.py --task-id "TASK-XXX"
python3 .claude/skills/os-database/scripts/list_tags.py  # all tags

# Dependencies
python3 .claude/skills/os-database/scripts/add_blocked_by.py --task-id "TASK-002" --blocked-by "TASK-001"
python3 .claude/skills/os-database/scripts/is_blocked.py --task-id "TASK-002"
python3 .claude/skills/os-database/scripts/list_blocking_tasks.py --task-id "TASK-002"
python3 .claude/skills/os-database/scripts/unblock_task.py --task-id "TASK-002"

# Task Relationships (flexible links: blocks, blocked_by, relates_to, duplicates, parent, child)
python3 .claude/skills/os-database/scripts/relate_tasks.py --from "TASK-001" --to "TASK-002" --type relates_to
python3 .claude/skills/os-database/scripts/list_relationships.py --task-id "TASK-001"
python3 .claude/skills/os-database/scripts/remove_relationship.py --relationship-id 1

# Multi-directional Dependencies (using task_relationships table)
# Cycle detection - prevents creating blocking loops
python3 .claude/skills/os-database/scripts/detect_cycle.py --from "TASK-001" --to "TASK-002
# Find all tasks that block a given task (transitive)
python3 .claude/skills/os-database/scripts/find_blocking_chain.py --task-id "TASK-003"
# Find all tasks blocked by a given task (transitive)
python3 .claude/skills/os-database/scripts/find_blocked_chain.py --task-id "TASK-001"
# Find tasks where all blockers are completed
python3 .claude/skills/os-database/scripts/ready_tasks.py
python3 .claude/skills/os-database/scripts/ready_tasks.py --agent-id "PM_Agent"
# When task completes, find tasks that are now unblocked
python3 .claude/skills/os-database/scripts/propagate_unblock.py --task-id "TASK-001"

# Archive
python3 .claude/skills/os-database/scripts/archive_task.py --task-id "TASK-XXX"
python3 .claude/skills/os-database/scripts/unarchive_task.py --task-id "TASK-XXX"
python3 .claude/skills/os-database/scripts/list_archived.py
python3 .claude/skills/os-database/scripts/list_archived.py --agent-id "agent-id"

# Virtual Tags (filter when getting tasks)
python3 .claude/skills/os-database/scripts/get_my_tasks.py --tag OVERDUE
python3 .claude/skills/os-database/scripts/get_my_tasks.py --tag BLOCKED
python3 .claude/skills/os-database/scripts/get_my_tasks.py --tag READY

# Urgency Score
python3 .claude/skills/os-database/scripts/update_urgency.py

# Time Tracking (estimates)
python3 .claude/skills/os-database/scripts/create_task.py --project-id "PRJ-XXX" --title "Task" --description "Do X" --estimate 60
python3 .claude/skills/os-database/scripts/update_task.py --task-id "TASK-001" --estimate 120
python3 .claude/skills/os-database/scripts/estimate_task.py --task-id "TASK-001" --minutes 60
python3 .claude/skills/os-database/scripts/time_report.py --task-id "TASK-001"
python3 .claude/skills/os-database/scripts/compare_estimates.py

# Bulk Update (multiple tasks at once - scoped to agent)
python3 .claude/skills/os-database/scripts/bulk_update.py --task-ids "TASK-001,TASK-002" --status "completed"
python3 .claude/skills/os-database/scripts/bulk_update.py --task-ids "TASK-001,TASK-002" --priority "high"

# Subtasks (lightweight checklists within tasks)
python3 .claude/skills/os-database/scripts/add_subtask.py --task-id "TASK-001" --title "Research existing solutions"
python3 .claude/skills/os-database/scripts/list_subtasks.py --task-id "TASK-001"
python3 .claude/skills/os-database/scripts/toggle_subtask.py --subtask-id 1
python3 .claude/skills/os-database/scripts/delete_subtask.py --subtask-id 1
python3 .claude/skills/os-database/scripts/get_task_with_subtasks.py --task-id "TASK-001"

# Task Templates (reusable task patterns)
python3 .claude/skills/os-database/scripts/create_template.py --name "Bug Fix" --title-template "Fix {issue}" --description-template "Root cause: {root_cause}" --default-priority "high" --default-tags "bug,fix" --default-due-days 3 --subtasks-template '["Investigate","Fix","Test","Verify"]'
python3 .claude/skills/os-database/scripts/list_templates.py
python3 .claude/skills/os-database/scripts/use_template.py --template-name "Bug Fix" --project-id PRJ-XXX --custom-fields '{"issue":"Login bug","root_cause":"Null pointer"}'

# Cycles/Sprints
python3 .claude/skills/os-database/scripts/cycles/create_cycle.py --name "Sprint 1" --goal "Ship auth" --start 2026-03-18 --end 2026-03-25
python3 .claude/skills/os-database/scripts/cycles/list_cycles.py
python3 .claude/skills/os-database/scripts/cycles/update_cycle.py --cycle-id 1 --status active
python3 .claude/skills/os-database/scripts/cycles/assign_to_cycle.py --task-id TASK-001 --cycle-id 1
python3 .claude/skills/os-database/scripts/cycles/get_cycle_tasks.py --cycle-id 1
python3 .claude/skills/os-database/scripts/cycles/get_current_cycle.py

# Custom Fields (flexible metadata on tasks)
# Add a global URL field
python3 .claude/skills/os-database/scripts/add_field.py --name "PR Link" --type url --field-key pr_link --global --description "Link to pull request"

# Add a select field with options
python3 .claude/skills/os-database/scripts/add_field.py --name "Severity" --type select --field-key severity --global --options '[{"label":"Critical","value":"critical"},{"label":"High","value":"high"}]'

# Add a number field
python3 .claude/skills/os-database/scripts/add_field.py --name "Story Points" --type number --field-key story_points --global

# Set field value on task
python3 .claude/skills/os-database/scripts/set_field.py --task-id TASK-001 --field pr_link --value "https://github.com/..."

# Get all field values for a task
python3 .claude/skills/os-database/scripts/get_fields.py --task-id TASK-001

# Query tasks by field value
python3 .claude/skills/os-database/scripts/query_by_field.py --field severity --value critical

# Create task with initial field values
python3 .claude/skills/os-database/scripts/create_task.py --project-id PRJ-XXX --title "Task" --description "Desc" --fields '{"severity":"high","story_points":5}'
```

## Task Types

| Type | Flag | Use When |
|------|------|----------|
| simple | (no --workspace) | Quick one-off tasks, just tick off |
| deep | --workspace | Multi-step, files, research |

## Event Types

BOOT, THOUGHT, ACTION, TOOL_CALL, ERROR, HANDOFF, COMPLETED

## Automations

Automations trigger actions based on task events. They run automatically when `update_task.py` changes status.

### Create Automation

```bash
python3 .claude/skills/os-database/scripts/create_automation.py \
  --name "Alert when blocked" \
  --trigger-event "task.status_changed" \
  --trigger-condition '{"field":"new_status","op":"eq","value":"blocked"}' \
  --action-type "log" \
  --action-config '{"event_type":"ACTION","msg":"Task blocked - requires attention"}'
```

### List Automations

```bash
python3 .claude/skills/os-database/scripts/list_automations.py
python3 .claude/skills/os-database/scripts/list_automations.py --enabled-only
```

### Toggle Automation

```bash
python3 .claude/skills/os-database/scripts/toggle_automation.py --automation-id 1 --enabled true
python3 .claude/skills/os-database/scripts/toggle_automation.py --automation-id 1 --enabled false
```

### Run Automations Manually

```bash
python3 .claude/skills/os-database/scripts/run_automations.py \
  --event "task.status_changed" \
  --data '{"task_id":"TASK-001","new_status":"blocked"}'
```

### Condition Operators

| Op | Meaning |
|----|---------|
| eq | equals |
| ne | not equals |
| gt | greater than |
| lt | less than |
| contains | contains string |
| in | in list |

### Example Automations

- **Log completion**: Triggers on `new_status=completed`, logs to timeline
- **Alert when blocked**: Triggers on `new_status=blocked`, logs alert
- **Escalate after 3 errors**: Triggers on `error_count>=3`, escalates

## Error Recovery

If a tool fails, run with --help for correct usage.
