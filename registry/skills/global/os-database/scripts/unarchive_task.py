#!/usr/bin/env python3
"""Unarchive a task (restore from archive)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def unarchive_task(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        UPDATE tasks SET status = 'pending', archived_at = NULL, updated_at = ? WHERE id = ?
    """, (now, task_id))

    updated = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "updated": updated, "task_id": task_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    unarchive_task(args.task_id)
