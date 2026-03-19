---
name: Complete Task
description: Mark a task as complete, bubble up learnings, and clean up. Follow this when finishing work.
---

# Procedure: Complete Task

You have finished your work. Follow these steps exactly.

## Step 1: Synthesize Learnings
- **Action:** Review your timeline events and workspace files
- **Goal:** Write a concise executive_summary (1-2 paragraphs) covering:
  - What was accomplished
  - Key decisions made
  - Any learnings or issues encountered

## Step 2: Update Task Status
- **Action:** Mark task complete in database
```bash
python3 .claude/skills/os-database/scripts/update_task.py --task-id "YOUR_TASK_ID" --status "completed" --summary "Your executive summary here"
```

## Step 3: Log Completion
- **Action:** Log final timeline event
```bash
python3 .claude/skills/os-database/scripts/log_event.py --type "COMPLETED" --msg "Task complete. Summary logged."
```

## Step 4: Clean Workspace (Optional)
- **Action:** List and remove temp files in workspace/
- **Goal:** Leave environment clean for next agent

---

**IMPORTANT:** Always provide an executive_summary. This is how the PM knows what happened without reading your code.
