#!/usr/bin/env python3
"""Add a blocking dependency to a task."""
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


def add_blocked_by(task_id: str, blocked_by_task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify both tasks exist
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    cursor.execute("SELECT id, status FROM tasks WHERE id = ?", (blocked_by_task_id,))
    blocker = cursor.fetchone()
    if not blocker:
        print(json.dumps({"status": "error", "message": f"Blocking task {blocked_by_task_id} not found"}))
        conn.close()
        return

    # Check if blocker is completed
    if blocker[1] != 'completed':
        print(json.dumps({
            "status": "warning",
            "message": f"Blocking task {blocked_by_task_id} is not completed (status: {blocker[1]})"
        }))

    # Add the dependency
    cursor.execute(
        "UPDATE tasks SET blocked_by_task_id = ?, updated_at = ? WHERE id = ?",
        (blocked_by_task_id, datetime.now(timezone.utc).isoformat(), task_id)
    )

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocked_by": blocked_by_task_id,
        "message": f"Task {task_id} is now blocked by {blocked_by_task_id}"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task that is blocked")
    parser.add_argument("--blocked-by", required=True, help="Task that blocks it")
    args = parser.parse_args()
    add_blocked_by(args.task_id, args.blocked_by)
