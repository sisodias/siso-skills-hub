#!/usr/bin/env python3
"""Search tasks by title, description, or executive_summary - scoped to agent."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def search_tasks(query: str, agent_id: str = None):
    config = load_config()
    if not agent_id:
        agent_id = config.get("agent_id")

    db_path = config.get("db_path")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    search_pattern = f"%{query}%"
    cursor.execute("""
        SELECT id, title, description, status, priority, due_date, assigned_agent_id, executive_summary, created_at
        FROM tasks
        WHERE assigned_agent_id = ?
        AND (title LIKE ? OR description LIKE ? OR executive_summary LIKE ?)
        ORDER BY updated_at DESC
    """, (agent_id, search_pattern, search_pattern, search_pattern))

    rows = cursor.fetchall()
    conn.close()

    tasks = [dict(row) for row in rows]

    print(json.dumps({
        "status": "success",
        "agent_id": agent_id,
        "query": query,
        "count": len(tasks),
        "tasks": tasks
    }, indent=2, default=str))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Search tasks by title, description, or executive_summary")
    parser.add_argument("--query", required=True, help="Search term")
    parser.add_argument("--agent-id", help="Override agent ID (defaults to config.json)")
    args = parser.parse_args()

    search_tasks(args.query, args.agent_id)
