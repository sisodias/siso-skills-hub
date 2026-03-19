#!/usr/bin/env python3
"""Use a saved context to get filtered tasks."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def use_context(name: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get the context
    cursor.execute("SELECT id, name, filter_query FROM contexts WHERE name = ?", (name,))
    row = cursor.fetchone()

    if not row:
        print(json.dumps({
            "status": "error",
            "message": f"Context '{name}' not found"
        }))
        conn.close()
        return

    context_id, context_name, filter_query = row

    # Parse the filter query
    try:
        filters = json.loads(filter_query)
    except json.JSONDecodeError:
        print(json.dumps({
            "status": "error",
            "message": "Invalid filter query JSON"
        }))
        conn.close()
        return

    # Build the query dynamically
    query = "SELECT id, title, description, status, priority, assigned_agent_id, project_id, created_at FROM tasks WHERE 1=1"
    params = []

    for key, value in filters.items():
        if value is not None:
            query += f" AND {key} = ?"
            params.append(value)

    query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "assigned_agent_id": row[5],
            "project_id": row[6],
            "created_at": row[7]
        })

    print(json.dumps({
        "status": "success",
        "context": {
            "id": context_id,
            "name": context_name,
            "filter_query": filters
        },
        "tasks": tasks,
        "count": len(tasks)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Use a saved context to filter tasks")
    parser.add_argument("--name", required=True, help="Context name to use")
    args = parser.parse_args()
    use_context(args.name)
