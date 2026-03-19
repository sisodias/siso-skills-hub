#!/usr/bin/env python3
"""Add a blocking dependency to a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def add_blocked_by(task_id: str, blocked_by_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO task_relationships (from_task_id, to_task_id, relationship_type, created_at)
        VALUES (?, ?, 'blocks', ?)
    """, (blocked_by_id, task_id, now))

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocked_by": blocked_by_id
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task that is blocked")
    parser.add_argument("--blocked-by", required=True, help="Task that blocks it")
    args = parser.parse_args()
    add_blocked_by(args.task_id, args.blocked_by)
