---
name: pm-tasks
description: Task management skill for PM_Agent using the centralized SQLite task database
version: 1.0.0
tags:
  - task-management
  - pm
  - database
---

# PM Tasks Skill

Task management skill for PM_Agent using the centralized SQLite task database.

## Database

**Location:** `${SISO_WORKSPACE}/.SystemDB/sisosystem.db`

## Quick Usage

```bash
# List all tasks
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py list

# List my pending tasks
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py mine

# Create a new task
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py create "Build feature X" --priority 8

# Create task with description
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py create "Add dark mode" --desc "Implement dark theme for settings" --priority 7

# Update task status
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py update TASK-001 in_progress
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py update TASK-001 completed
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py update TASK-001 blocked

# Add a step (for breaking into pipeline)
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py add-step TASK-001 plan planner
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py add-step TASK-001 implement developer

# Get task details
python3 skills_hub/registry/skills/pm-tasks/scripts/pm_tasks.py get TASK-001
```

## Workflow

### 1. Brainstorm & Queue
When user gives you a big task, break it down and queue it:
```
pm_tasks.py create "Implement user auth system"
pm_tasks.py create "Build dashboard UI"
pm_tasks.py create "Add database migrations"
```

### 2. Break Down
Add subtasks/steps for execution:
```
pm_tasks.py add-step TASK-001 plan planner
pm_tasks.py add-step TASK-001 implement developer
pm_tasks.py add-step TASK-001 verify verifier
```

### 3. Work
Update status as you progress:
```
pm_tasks.py update TASK-001 in_progress  # Start working
pm_tasks.py update TASK-001 completed   # Done
```

### 4. Track
Check what's pending:
```
pm_tasks.py mine  # My pending tasks
pm_tasks.py list # All tasks
```

## Task Statuses

- `pending` - Not started
- `in_progress` - Currently working
- `completed` - Done
- `blocked` - Stuck, needs help
- `cancelled` - Won't do

## Priority

- 1-10 scale (10 = highest)
- Default: 5

## For Complex Tasks

Use the full siso-tasks.py for:
- Execution logs: `log-execution`
- Artifacts: `update-artifact`
- Memories: `add-memory`

See: `skills_hub/registry/skills/task-manager/SKILL.md`
