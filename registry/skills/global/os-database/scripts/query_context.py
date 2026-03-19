#!/usr/bin/env python3
"""Query task context - auto-reads config for db_path."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def query_context(task_id: str = None, agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    if not agent_id:
        agent_id = config.get("agent_id")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get tasks for agent
    query = "SELECT id, title, description, status, priority, created_at FROM tasks WHERE 1=1"
    params = []
    if agent_id:
        query += " AND assigned_agent_id = ?"
        params.append(agent_id)
    if task_id:
        query += " AND id = ?"
        params.append(task_id)
    query += " ORDER BY updated_at DESC LIMIT 20"

    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]
    conn.close()

    print(json.dumps({"status": "success", "agent_id": agent_id, "tasks": tasks, "count": len(tasks)}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id")
    parser.add_argument("--agent-id")
    args = parser.parse_args()
    query_context(args.task_id, args.agent_id)
