---
name: Create Subtask
description: Break a large task into smaller pieces and delegate to other agents.
---

# Procedure: Create Subtask

A task is too complex. Break it down.

## Step 1: Identify the Split Point
- **Action:** Determine what can be parallelized
- **Goal:** Identify a self-contained piece of work

## Step 2: Create Subtask
- **Action:** Create the subtask in database
```bash
python3 .claude/skills/os-database/scripts/create_subtask.py \
  --parent-id "PARENT_TASK_ID" \
  --task-id "NEW_SUBTASK_ID" \
  --title "Clear, specific title" \
  --description "What this subtask entails"
```

## Step 3: Log the Handoff
- **Action:** Log that you're breaking down work
```bash
python3 .claude/skills/os-database/scripts/log_event.py --type "ACTION" --msg "Created subtask NEW_SUBTASK_ID for parallel execution"
```

## Step 4: Assign (Optional)
- **Action:** If you know who should take it, assign now
```bash
python3 .claude/skills/os-database/scripts/update_task.py --task-id "NEW_SUBTASK_ID" --assign "OtherAgent"
```

---

**Tip:** Use naming convention `PARENT-ID-A`, `PARENT-ID-B` for subtasks.
