#!/usr/bin/env python3
"""List tags for a task or all tags."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_tags(task_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if task_id:
        cursor.execute("SELECT tag, created_at FROM task_tags WHERE task_id = ? ORDER BY created_at", (task_id,))
        tags = [{"tag": row[0], "created_at": row[1]} for row in cursor.fetchall()]
        result = {"status": "success", "task_id": task_id, "tags": tags}
    else:
        cursor.execute("SELECT DISTINCT tag FROM task_tags ORDER BY tag")
        tags = [row[0] for row in cursor.fetchall()]
        result = {"status": "success", "all_tags": tags}

    conn.close()
    print(json.dumps(result))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", help="Task ID (optional, lists all tags if omitted)")
    args = parser.parse_args()
    list_tags(args.task_id)
