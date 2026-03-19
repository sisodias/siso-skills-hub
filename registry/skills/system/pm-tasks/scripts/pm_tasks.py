#!/usr/bin/env python3
"""PM Task Manager - Simple wrapper for PM_Agent task management"""

import subprocess
import sys
import os

# Path to the task system
SISO_TASKS = "/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/registry/skills/task-manager/siso-tasks.py"
DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

def run(cmd):
    env = os.environ.copy()
    env["SISO_SYSTEM_DB"] = DB_PATH
    result = subprocess.run(
        ["python3", SISO_TASKS] + cmd,
        capture_output=True, text=True, env=env
    )
    return result.stdout + result.stderr

def main():
    if len(sys.argv) < 2:
        print("PM Task Manager")
        print("================")
        print("Usage: pm_tasks.py <command>")
        print("")
        print("Commands:")
        print("  list                    # List all tasks")
        print("  mine                    # List my pending tasks")
        print("  create <title> [--desc <desc>] [--priority <n>]")
        print("                         # Create a new task")
        print("  update <id> <status>   # Update task status")
        print("  add-step <task-id> <step-name> <role>")
        print("                         # Add a step to a task")
        print("  get <id>               # Get task details")
        print("")
        print("Examples:")
        print("  pm_tasks.py list")
        print("  pm_tasks.py create 'Build login feature' --priority 8")
        print("  pm_tasks.py update TASK-001 in_progress")
        print("  pm_tasks.py add-step TASK-001 plan planner")
        return

    cmd = sys.argv[1:]

    if cmd[0] == "list":
        print(run(["query", "--sql", "SELECT id, title, status, priority, assigned_to FROM tasks ORDER BY priority DESC"]))

    elif cmd[0] == "mine":
        print(run(["query", "--sql", "SELECT id, title, status, priority FROM tasks WHERE assigned_to = 'PM_Agent' AND status != 'completed' ORDER BY priority DESC"]))

    elif cmd[0] == "create":
        title = cmd[1] if len(cmd) > 1 else "New Task"
        desc = ""
        priority = 5

        # Parse args
        i = 2
        while i < len(cmd):
            if cmd[i] == "--desc" and i + 1 < len(cmd):
                desc = cmd[i + 1]
                i += 2
            elif cmd[i] == "--priority" and i + 1 < len(cmd):
                priority = cmd[i + 1]
                i += 2
            else:
                i += 1

        # Generate ID
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tasks")
        count = cursor.fetchone()[0] + 1
        task_id = f"TASK-{count:03d}"
        conn.close()

        print(f"Creating task: {task_id}")
        print(run(["create-task",
            "--id", task_id,
            "--project-id", "agent-os",
            "--pipeline-type", "meta",
            "--title", title,
            "--category", "pm",
            "--created-by", "PM_Agent",
            "--assigned-to", "PM_Agent",
            "--description", desc,
            "--priority", str(priority)]))

    elif cmd[0] == "update" and len(cmd) >= 3:
        task_id = cmd[1]
        status = cmd[2]
        print(run(["update-step", "--id", task_id, "--status", status]))

    elif cmd[0] == "add-step" and len(cmd) >= 4:
        task_id = cmd[1]
        step_name = cmd[2]
        role = cmd[3]
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM task_steps")
        count = cursor.fetchone()[0] + 1
        step_id = f"STEP-{count:03d}"
        conn.close()
        print(run(["add-step", "--id", step_id, "--task-id", task_id, "--step-name", step_name, "--role", role, "--order", "1"]))

    elif cmd[0] == "get" and len(cmd) >= 2:
        task_id = cmd[1]
        print(run(["query", "--sql", "SELECT * FROM tasks WHERE id = '" + task_id + "'"]))

    else:
        print(f"Unknown command: {' '.join(cmd)}")
        print("Run pm_tasks.py for help")

if __name__ == "__main__":
    main()
