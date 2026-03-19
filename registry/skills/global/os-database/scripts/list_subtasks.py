#!/usr/bin/env python3
"""List subtasks for a task."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_subtasks(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, task_id, title, status, sort_order, created_at, updated_at
        FROM subtasks
        WHERE task_id = ?
        ORDER BY sort_order, id
    """, (task_id,))

    rows = cursor.fetchall()
    conn.close()

    subtasks = [dict(row) for row in rows]
    print(json.dumps({
        "task_id": task_id,
        "subtasks": subtasks,
        "count": len(subtasks)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID to list subtasks for")
    args = parser.parse_args()
    list_subtasks(args.task_id)
