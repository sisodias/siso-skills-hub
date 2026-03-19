#!/usr/bin/env python3
"""Bulk update tasks - update multiple tasks at once."""
import sqlite3
import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def bulk_update(task_ids: list, agent_id: str = None, status: str = None, priority: str = None):
    config = load_config()
    db_path = config.get("db_path")

    if not agent_id:
        agent_id = config.get("agent_id")

    if not agent_id:
        print(json.dumps({"status": "error", "message": "agent_id not set in config.json"}))
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Build update query - must be scoped to agent
    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
        if status == "completed":
            updates.append("completed_at = ?")
            params.append(now)

    if priority:
        updates.append("priority = ?")
        params.append(priority)

    if not updates:
        print(json.dumps({"status": "error", "message": "No fields to update. Use --status or --priority"}))
        return

    updates.append("updated_at = ?")
    params.append(now)

    # Convert task_ids to comma-separated string for SQL IN clause
    placeholders = ",".join("?" * len(task_ids))
    params.extend(task_ids)

    # Update only tasks assigned to this agent
    query = f"UPDATE tasks SET {', '.join(updates)} WHERE id IN ({placeholders}) AND assigned_agent_id = ?"
    params.append(agent_id)

    cursor.execute(query, params)
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "updated_count": updated_count,
        "task_ids": task_ids,
        "updates": {"status": status, "priority": priority}
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-ids", required=True, help="Comma-separated task IDs (e.g., TASK-001,TASK-002)")
    parser.add_argument("--status", choices=["pending", "in_progress", "blocked", "review", "completed", "failed"])
    parser.add_argument("--priority", choices=["low", "medium", "high", "critical"])
    parser.add_argument("--agent-id", help="Override agent ID")
    args = parser.parse_args()

    task_ids = [tid.strip() for tid in args.task_ids.split(",")]
    bulk_update(task_ids, args.agent_id, args.status, args.priority)
