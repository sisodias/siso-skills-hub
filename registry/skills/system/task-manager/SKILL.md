---
name: task-manager
description: How to use the native siso-tasks SQLite database for cross-agent communication, job routing, and progress persistence.
version: 1.0.0
tags:
  - task-management
  - database
  - cli
---

# `siso-tasks` Agent Skill

**Purpose:** This skill documents how PM Agents and Execution Agents interact with the ecosystem's local task database. We use a lightning-fast native CLI (`siso-tasks.py`) interacting with a SQLite database (`sisosystem.db`) instead of slow API/MCP calls. 

**Database Path:**
The **central** database lives at `SISO_Workspace/.SystemDB/sisosystem.db`. Set the environment variable before running commands:

```bash
export SYSTEM_DB="/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db"
python3 /Users/shaansisodia/SISO_Workspace/Agent_OS/skills/siso-tasks/siso-tasks.py <command>
```

All agents and projects share this central queue.

## 1. Project Managers (PMs) Creating Tasks

When a PM receives a user request that requires the Execution Pipeline, they must insert it into the global queue.

```bash
# 1. Create the global task
./siso-tasks.py create-task \
  --id "TASK-XYZ" \
  --project-id "lumelle" \
  --pipeline-type "execution" \
  --title "Add Dark Mode" \
  --category "feature" \
  --created-by "human" \
  --assigned-to "Developer" \
  --description "Add dark mode to the footer" \
  --metadata '{"dependencies": []}' \
  --priority 10

# 2. Add the DAG steps sequentially for that task
# For execution pipeline, the steps typically are: route -> plan -> setup -> implement -> verify -> test
./siso-tasks.py add-step --id "STEP-1" --task-id "TASK-XYZ" --step-name "route" --role "task-router" --order 1 --input-payload '{"extra": "context"}'
./siso-tasks.py add-step --id "STEP-2" --task-id "TASK-XYZ" --step-name "plan" --role "planner" --order 2
```

## 2. Autonomous Pipeline Agents Checking Inboxes and Pulling Work

Every agent role (e.g. `task-router`, `planner`, `developer`) has an implicit "inbox" formed by steps assigned to them.

**To view your inbox (Task List) without pulling a task:**
```bash
./siso-tasks.py view-inbox --role "developer"

# Output:
# {
#   "status": "success",
#   "role": "developer",
#   "queue_length": 2,
#   "inbox": [
#      {"step_id": "S1", "task_description": "Add dark mode", "status": "pending", "priority": 10},
#      {"step_id": "S2", "task_description": "Fix login bug", "status": "retry", "priority": 5}
#   ]
# }
```

**To actually pull the highest-priority task from your inbox to work on:**
```bash
./siso-tasks.py pull --role "developer"

# Output looks like:
# {
#   "status": "success",
#   "step_id": "STEP-4",
#   "task_id": "TASK-XYZ",
#   "step_name": "implement",
#   "task_description": "Add dark mode...",
#   "input_payload": null
# }
```
**CRITICAL:** If `pull` returns `{"status": "empty"}`, your inbox is empty. You should sleep or transition to lower-priority work (like Meta improvements). Do not retry immediately in a tight loop.

## 3. Completing Work or Handling Failures

Once an agent finishes a step, they MUST update the database so the pipeline can continue to the next step.

```bash
# If successful, pass payload to the next step
./siso-tasks.py update-step --id "STEP-4" --status "done" --output-payload '{"stories_completed": 1}'

# If work failed verification and needs the previous agent to try again
./siso-tasks.py update-step --id "STEP-4" --status "retry" --error-log "Tests failed on line 42"

# If catastrophic failure that needs human/researcher intervention
./siso-tasks.py update-step --id "STEP-4" --status "error" --error-log "Repo doesn't exist"
```

## 4. Reading and Writing Artifacts (Context)

Agents NO LONGER overwrite markdown files on disk like `progress.md`. Doing so causes race conditions.
Instead, use the `artifacts` table.

**To write a progress update:**
```bash
./siso-tasks.py update-artifact \
  --task-id "TASK-XYZ" \
  --step-id "STEP-4" \
  --type "progress_log" \
  --content "# Context Update\nFound standard pattern for dark mode..."
```
*Note: This automatically versions the artifact in the database.*

**To read context from previous agents in the pipeline:**
```bash
# The Planner or Verifier reading the latest version of the Developer's log:
./siso-tasks.py get-artifact --task-id "TASK-XYZ" --type "progress_log"
```

## 5. Advanced Agent State (Memory & Execution Logs)

Based on leading open-source frameworks, the SQLite database acts as your persistent state machine.

**To explicitly save a memory for your next session:**
If you solve a complex bug or learn a structural fact about the repo, store it.
```bash
./siso-tasks.py add-memory \
  --task-id "TASK-XYZ" \
  --session-id "sess-123" \
  --type "learning" \
  --content "The auth router requires a trailing slash."
```

**To log your execution steps (Thought/Action/Observation):**
If completing a complex, multi-step subtask, log it so the PM can review your reasoning later.
```bash
./siso-tasks.py log-execution \
  --step-id "STEP-4" \
  --action-type "tool_call" \
  --details "Ran 'grep -r auth' and found 12 files."
```

**To dynamically query the database:**
If you need specific data (e.g., retrieving previous memories, or checking the status of other tasks), you can run a safe, read-only SQL query:
```bash
./siso-tasks.py query --sql "SELECT content FROM memories WHERE task_id = 'TASK-XYZ'"
```

---

## Tool Availability
The CLI tool is located at `Agent_OS/skills/siso-tasks/siso-tasks.py`. You may need to use `python3 siso-tasks.py` depending on the environment context. Ensure the file has `chmod +x` executable permissions if invoking directly.
