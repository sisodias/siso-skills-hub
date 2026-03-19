#!/usr/bin/env python3
"""Add a tag to a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def add_tag(task_id: str, tag: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO task_tags (task_id, tag, created_at)
        VALUES (?, ?, ?)
    """, (task_id, tag, now))

    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "task_id": task_id, "tag": tag}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--tag", required=True)
    args = parser.parse_args()
    add_tag(args.task_id, args.tag)
