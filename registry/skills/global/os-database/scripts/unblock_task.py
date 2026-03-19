#!/usr/bin/env python3
"""Remove blocking dependency from a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def unblock_task(task_id: str, blocked_by_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM task_relationships
        WHERE from_task_id = ? AND to_task_id = ? AND relationship_type = 'blocks'
    """, (blocked_by_id, task_id))

    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "deleted": deleted, "task_id": task_id, "unblocked_by": blocked_by_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--blocked-by", required=True)
    args = parser.parse_args()
    unblock_task(args.task_id, args.blocked_by)
