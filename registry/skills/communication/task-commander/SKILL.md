---
name: task-commander
description: Log tasks and communicate with agents using the SISO task database
version: 1.0.0
tags:
  - task-management
  - database
  - communication
---

# Task Commander Skill

Log tasks and communicate with agents using the SISO task database.

## Task Database

Location: `/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db`

Query tasks:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT id, title, assigned_to, status, priority FROM tasks ORDER BY priority DESC LIMIT 10')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

---

## Workflow: Assign Task to Agent

### 1. Get Pending Tasks
Check tasks assigned to an agent:
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db')
cursor = conn.cursor()
cursor.execute(\"SELECT id, title, status, priority FROM tasks WHERE assigned_to LIKE '%Testing%' AND status='pending' ORDER BY priority DESC\")
for row in cursor.fetchall():
    print(f'{row[0]}: {row[1]} (priority: {row[3]})')
conn.close()
"
```

### 2. Build Task Message
Include task details when messaging agent:
```
Task: <task_id>
Title: <title>
Priority: <priority>
Description: <description>

Please complete this task.
```

### 3. Send to Agent
```bash
cmux send --workspace workspace:X "Task: TASK-0001\nTitle: Implement Auth\nPriority: 5\n\nPlease work on this task.\n"
```

---

## Example: Assign Task to Testing Agent

### Step 1: Find task for Testing Agent
```bash
python3 -c "
import sqlite3
conn = sqlite3.connect('/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db')
cursor = conn.cursor()
cursor.execute(\"SELECT id, title, status FROM tasks WHERE assigned_to LIKE '%Testing%' AND status='pending'\")
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

### Step 2: Send to Testing Agent (workspace:24)
```bash
cmux send --workspace workspace:24 "TASK: TEST-0001\nTask: Test task: Add documentation\nPriority: 5\n\nPlease test the app and add documentation.\n"
```

---

## Create New Task

```bash
export SYSTEM_DB="/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db"
python3 /Users/shaansisodia/SISO_Workspace/Agent_OS/skills/siso-tasks/siso-tasks.py create-task \
  --id TASK-XXXX \
  --project-id siso-internal \
  --pipeline-type execution \
  --title "Your task title" \
  --category feature \
  --created-by human \
  --assigned-to Testing_Agent \
  --description "Task description" \
  --priority 5
```

---

## Update Task Status

```bash
export SYSTEM_DB="/Users/shaansisodia/SISO_Workspace/.SystemDB/sisosystem.db"
python3 /Users/shaansisodia/SISO_Workspace/Agent_OS/skills/siso-tasks/siso-tasks.py update-step \
  --step-id <step_id> \
  --status completed
```

---

## Quick Reference

1. Query tasks: Check task DB
2. Build message: Include task details
3. Send to agent: Via CMUX
4. Update status: Mark task complete
