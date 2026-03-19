#!/usr/bin/env python3
"""List archived tasks, optionally filtered by agent."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_archived(agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if agent_id:
        cursor.execute("""
            SELECT id, title, status, archived_at, assigned_agent_id, created_at
            FROM tasks
            WHERE archived_at IS NOT NULL AND assigned_agent_id = ?
            ORDER BY archived_at DESC
        """, (agent_id,))
    else:
        cursor.execute("""
            SELECT id, title, status, archived_at, assigned_agent_id, created_at
            FROM tasks
            WHERE archived_at IS NOT NULL
            ORDER BY archived_at DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    tasks = [dict(row) for row in rows]
    print(json.dumps({"status": "success", "count": len(tasks), "tasks": tasks}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent-id", help="Filter by agent ID")
    args = parser.parse_args()

    list_archived(args.agent_id)
