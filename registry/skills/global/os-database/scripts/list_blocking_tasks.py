#!/usr/bin/env python3
"""List tasks that block a given task."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_blocking_tasks(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get tasks that block this task
    cursor.execute("""
        SELECT t.id, t.title, t.status, t.blocked_by_task_id
        FROM tasks t
        WHERE t.id = ?
    """, (task_id,))

    task = cursor.fetchone()
    if not task:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    blocking_task_id = task[3]

    if not blocking_task_id:
        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "is_blocked": False,
            "blocking_tasks": [],
            "message": "Task is not blocked"
        }))
        conn.close()
        return

    # Get the blocking task details
    cursor.execute("""
        SELECT id, title, status FROM tasks WHERE id = ?
    """, (blocking_task_id,))

    blocker = cursor.fetchone()
    conn.close()

    if blocker:
        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "is_blocked": True,
            "blocking_tasks": [{
                "id": blocker[0],
                "title": blocker[1],
                "status": blocker[2]
            }]
        }))
    else:
        print(json.dumps({
            "status": "error",
            "message": f"Blocking task {blocking_task_id} not found in database"
        }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task to check")
    args = parser.parse_args()
    list_blocking_tasks(args.task_id)
