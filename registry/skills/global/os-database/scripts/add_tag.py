#!/usr/bin/env python3
"""Add a tag to a task."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def add_tag(task_id: str, tag: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO task_tags (task_id, tag) VALUES (?, ?)", (task_id, tag))
        conn.commit()
        result = {"status": "success", "task_id": task_id, "tag": tag, "message": f"Tag '{tag}' added to {task_id}"}
    except sqlite3.IntegrityError:
        result = {"status": "exists", "task_id": task_id, "tag": tag, "message": f"Tag '{tag}' already exists on {task_id}"}
    finally:
        conn.close()

    print(json.dumps(result))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID")
    parser.add_argument("--tag", required=True, help="Tag to add")
    args = parser.parse_args()
    add_tag(args.task_id, args.tag)
