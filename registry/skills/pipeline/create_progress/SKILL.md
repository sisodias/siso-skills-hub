---
name: create-progress
description: Initialize or update progress.md for a pipeline run
user-invocable: true
---

# Create Progress Skill

Create or update the progress.md file for the current pipeline run.

## Usage

```
/create-progress <run_dir> <task_description>
```

## Steps

1. Create run directory if it doesn't exist: `pipeline_runs/<TASK_ID>/`
2. Create `progress.md` with header:
   ```markdown
   # Progress Log
   Run: <RUN_ID>
   Task: <description>
   Started: <timestamp>

   ## Codebase Patterns
   (add patterns here as you discover them)

   ---
   ```
3. Return the path to progress.md

## Update Progress

After completing work, rewrite progress.md to add:
```markdown
## <date/time> - <story_id>: <title>
- What was implemented
- Files changed
- Learnings: codebase patterns, gotchas, useful context
---
```
