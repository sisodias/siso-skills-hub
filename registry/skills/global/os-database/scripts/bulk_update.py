#!/usr/bin/env python3
"""Bulk update tasks - update multiple tasks at once."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def bulk_update(task_ids: list, status: str = None, priority: str = None, assigned_agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    if not task_ids:
        print(json.dumps({"status": "error", "message": "No task IDs provided"}))
        return

    placeholders = ','.join('?' * len(task_ids))
    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
    if priority:
        updates.append("priority = ?")
        params.append(priority)
    if assigned_agent_id:
        updates.append("assigned_agent_id = ?")
        params.append(assigned_agent_id)

    updates.append("updated_at = ?")
    params.append(now)
    params.extend(task_ids)

    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id IN ({placeholders})"
    cursor.execute(query, params)

    count = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "updated": count, "task_ids": task_ids}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-ids", required=True, help="Comma-separated task IDs")
    parser.add_argument("--status", choices=['pending', 'in_progress', 'completed', 'cancelled', 'archived'])
    parser.add_argument("--priority", choices=['low', 'medium', 'high', 'critical'])
    parser.add_argument("--assign", help="Agent ID to assign")
    args = parser.parse_args()
    task_ids = [t.strip() for t in args.task_ids.split(',')]
    bulk_update(task_ids, args.status, args.priority, args.assign)
