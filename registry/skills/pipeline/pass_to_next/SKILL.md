---
name: pass-to-next
description: Pass context to the next agent in the pipeline
user-invocable: true
---

# Pass to Next Agent Skill

Hand off work to the next agent in the pipeline by writing output files.

## Usage

```
/pass-to-next <agent_name> <output_file>
```

## Steps

1. Determine the next agent based on workflow:
   - Task Router → Planner
   - Planner → Setup
   - Setup → Developer
   - Developer → Verifier
   - Verifier → Developer (retry) or Tester
   - Tester → PR Agent
   - PR Agent → Reviewer
   - Reviewer → Human (done)

2. Write output to the appropriate location:
   - For next agent's `inbox/current_task.json`
   - Or to the shared `pipeline_runs/<TASK_ID>/` directory

3. Format the handoff:
   ```json
   {
     "from": "planner",
     "to": "setup",
     "task_id": "TASK-0001",
     "data": {
       "stories": [...],
       "repo": "/path/to/repo",
       "branch": "feature-xyz"
     },
     "status": "done"
   }
   ```

4. Signal completion with STATUS: done in the required format
