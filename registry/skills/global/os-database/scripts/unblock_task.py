#!/usr/bin/env python3
"""Remove blocking dependency from a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def unblock_task(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT id, blocked_by_task_id FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()

    if not task:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    if not task[1]:
        print(json.dumps({"status": "success", "message": f"Task {task_id} was not blocked"}))
        conn.close()
        return

    cursor.execute(
        "UPDATE tasks SET blocked_by_task_id = NULL, updated_at = ? WHERE id = ?",
        (datetime.now(timezone.utc).isoformat(), task_id)
    )

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "message": f"Task {task_id} is now unblocked"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task to unblock")
    args = parser.parse_args()
    unblock_task(args.task_id)
