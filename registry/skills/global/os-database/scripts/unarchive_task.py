#!/usr/bin/env python3
"""Unarchive a task (restore from archive)."""
import sqlite3
import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def unarchive_task(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Check if task exists
    cursor.execute("SELECT id, archived_at FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    if row[1] is None:
        print(json.dumps({"status": "error", "message": f"Task {task_id} is not archived"}))
        conn.close()
        return

    # Unarchive the task
    cursor.execute(
        "UPDATE tasks SET archived_at = NULL, status = 'pending', updated_at = ? WHERE id = ?",
        (now, task_id)
    )
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "task_id": task_id, "unarchived": True}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID to unarchive")
    args = parser.parse_args()

    unarchive_task(args.task_id)
