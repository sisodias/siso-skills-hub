---
name: check-status
description: Check the current status of a pipeline run
user-invocable: true
---

# Check Status Skill

Check the current state of a pipeline run by reading progress files.

## Usage

```
/check-status <task_id>
```

## Steps

1. Look in `pipeline_runs/<TASK_ID>/`
2. Read available files:
   - `JobTicket.json` - original task
   - `progress.md` - current progress
   - `stories.json` - story list (if Planner ran)
3. Determine current state:
   - Which stories completed
   - Which agent last ran
   - Any blockers

## Output

```
TASK: TASK-0001
STATUS: executing
CURRENT_AGENT: developer
STORIES_COMPLETED: 2/5
LAST_ACTION: Implemented US-002
BLOCKERS: none
```
