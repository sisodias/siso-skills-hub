#!/usr/bin/env python3
"""Remove a tag from a task."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def remove_tag(task_id: str, tag: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM task_tags WHERE task_id = ? AND tag = ?", (task_id, tag))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted > 0:
        result = {"status": "success", "task_id": task_id, "tag": tag, "message": f"Tag '{tag}' removed from {task_id}"}
    else:
        result = {"status": "not_found", "task_id": task_id, "tag": tag, "message": f"Tag '{tag}' not found on {task_id}"}

    print(json.dumps(result))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument("--tag", required=True, help="Tag to remove")
    args = parser.parse_args()
    remove_tag(args.task_id, args.tag)
