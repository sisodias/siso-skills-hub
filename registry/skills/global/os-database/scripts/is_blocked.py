#!/usr/bin/env python3
"""Check if a task is blocked by another task."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def is_blocked(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, status, blocked_by_task_id
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    task = cursor.fetchone()
    conn.close()

    if not task:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        return

    blocked_by = task[3]

    if blocked_by:
        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "is_blocked": True,
            "blocked_by": blocked_by,
            "message": f"Task is blocked by {blocked_by}"
        }))
    else:
        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "is_blocked": False,
            "message": "Task is not blocked"
        }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task to check")
    args = parser.parse_args()
    is_blocked(args.task_id)
