#!/usr/bin/env python3
"""Get task details with its subtasks."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def get_task_with_subtasks(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, description, status, priority, assigned_agent_id,
               created_at, updated_at, completed_at
        FROM tasks WHERE id = ?
    """, (task_id,))

    task_row = cursor.fetchone()
    if not task_row:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    task = dict(task_row)

    cursor.execute("""
        SELECT id, task_id, title, status, sort_order, created_at, updated_at
        FROM subtasks WHERE task_id = ?
        ORDER BY sort_order, id
    """, (task_id,))

    subtasks = [dict(row) for row in cursor.fetchall()]
    conn.close()

    completed = sum(1 for s in subtasks if s['status'] == 'completed')
    total = len(subtasks)
    progress = round(completed / total * 100, 1) if total > 0 else 0

    print(json.dumps({
        "task": task,
        "subtasks": subtasks,
        "progress": {"completed": completed, "total": total, "percentage": progress}
    }, default=str))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    get_task_with_subtasks(args.task_id)
