#!/usr/bin/env python3
"""Search tasks by title, description, or executive_summary - scoped to agent."""
import sqlite3
import json
import os
import argparse

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def search_tasks(query, agent_id=None):
    config = load_config()

    if not agent_id:
        agent_id = config.get("agent_id")

    db_path = config.get("db_path")

    if not agent_id:
        print(json.dumps({"status": "error", "message": "agent_id not set in config.json and --agent-id not provided"}))
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Search in title, description, executive_summary
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
    parser = argparse.ArgumentParser(description="Search tasks by title, description, or executive_summary")
    parser.add_argument("--query", required=True, help="Search term")
    parser.add_argument("--agent-id", help="Override agent ID (defaults to config.json)")
    args = parser.parse_args()

    search_tasks(args.query, args.agent_id)
