#!/usr/bin/env python3
"""Get task details with its subtasks."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_task_with_subtasks(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get task
    cursor.execute("""
        SELECT id, title, description, status, priority, assigned_agent_id,
               created_at, updated_at, completed_at
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    task_row = cursor.fetchone()

    if not task_row:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        sys.exit(1)

    task = dict(task_row)

    # Get subtasks
    cursor.execute("""
        SELECT id, task_id, title, status, sort_order, created_at, updated_at
        FROM subtasks
        WHERE task_id = ?
        ORDER BY sort_order, id
    """, (task_id,))

    subtasks = [dict(row) for row in cursor.fetchall()]
    conn.close()

    # Calculate progress
    completed = sum(1 for s in subtasks if s['status'] == 'completed')
    total = len(subtasks)
    progress = (completed / total * 100) if total > 0 else 0

    print(json.dumps({
        "task": task,
        "subtasks": subtasks,
        "progress": {
            "completed": completed,
            "total": total,
            "percentage": round(progress, 1)
        }
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID to fetch")
    args = parser.parse_args()
    get_task_with_subtasks(args.task_id)
