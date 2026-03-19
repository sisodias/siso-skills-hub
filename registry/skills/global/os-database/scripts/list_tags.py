#!/usr/bin/env python3
"""List tags for a task or all tags."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def list_tags(task_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if task_id:
        cursor.execute("""
            SELECT t.tag, t.created_at, t.task_id
            FROM task_tags t
            WHERE t.task_id = ?
            ORDER BY t.created_at DESC
        """, (task_id,))
    else:
        cursor.execute("""
            SELECT tag, COUNT(*) as count
            FROM task_tags
            GROUP BY tag
            ORDER BY count DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    tags = [dict(row) for row in rows]
    print(json.dumps({"status": "success", "task_id": task_id, "tags": tags, "count": len(tags)}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id")
    args = parser.parse_args()
    list_tags(args.task_id)
