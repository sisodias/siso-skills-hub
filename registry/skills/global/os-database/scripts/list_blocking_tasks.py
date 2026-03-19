#!/usr/bin/env python3
"""List tasks that block a given task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def list_blocking_tasks(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, status, blocked_by_task_id FROM tasks WHERE id = ?
    """, (task_id,))

    task = cursor.fetchone()
    if not task:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    blocking_task_id = dict(task).get('blocked_by_task_id')

    if not blocking_task_id:
        print(json.dumps({
            "task_id": task_id, "is_blocked": False, "blocking_tasks": []
        }))
        conn.close()
        return

    cursor.execute("""
        SELECT id, title, status FROM tasks WHERE id = ?
    """, (blocking_task_id,))

    blocker = cursor.fetchone()
    conn.close()

    if blocker:
        print(json.dumps({
            "task_id": task_id,
            "is_blocked": True,
            "blocking_tasks": [dict(blocker)]
        }))
    else:
        print(json.dumps({"status": "error", "message": f"Blocking task {blocking_task_id} not found"}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    list_blocking_tasks(args.task_id)
