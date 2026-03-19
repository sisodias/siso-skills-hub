#!/usr/bin/env python3
"""Create subtask - auto-reads config."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def create_subtask(parent_id: str, task_id: str, title: str, description: str, assigned_agent: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO tasks (id, parent_task_id, title, description, assigned_agent_id, status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?)
    """, (task_id, parent_id, title, description, assigned_agent, now, now))

    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "task_id": task_id, "parent_id": parent_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--parent-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--assign")
    args = parser.parse_args()
    create_subtask(args.parent_id, args.task_id, args.title, args.description, args.assign)
