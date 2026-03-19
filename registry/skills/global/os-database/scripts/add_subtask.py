#!/usr/bin/env python3
"""Add a subtask to a task."""
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


def add_subtask(task_id: str, title: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Get next sort_order
    cursor.execute("SELECT COALESCE(MAX(sort_order), 0) + 1 FROM subtasks WHERE task_id = ?", (task_id,))
    sort_order = cursor.fetchone()[0]

    cursor.execute("""
        INSERT INTO subtasks (task_id, title, status, sort_order, created_at, updated_at)
        VALUES (?, ?, 'pending', ?, ?, ?)
    """, (task_id, title, sort_order, now, now))

    subtask_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "subtask_id": subtask_id,
        "task_id": task_id,
        "title": title,
        "sort_order": sort_order
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Parent task ID")
    parser.add_argument("--title", required=True, help="Subtask title")
    args = parser.parse_args()
    add_subtask(args.task_id, args.title)
