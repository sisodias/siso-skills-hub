#!/usr/bin/env python3
"""Create a saved context (filter/query) for tasks."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def create_context(name: str, filter_query: str, agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    try:
        cursor.execute("""
            INSERT INTO contexts (name, filter_query, agent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, filter_query, agent_id, now, now))
        conn.commit()
        context_id = cursor.lastrowid

        print(json.dumps({
            "status": "success",
            "context_id": context_id,
            "name": name,
            "filter_query": filter_query,
            "message": f"Context '{name}' created"
        }))
    except sqlite3.IntegrityError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Context '{name}' already exists"
        }))
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a saved context for tasks")
    parser.add_argument("--name", required=True, help="Context name (e.g., 'work', 'urgent')")
    parser.add_argument("--filter-query", required=True, help="Filter query as JSON string (e.g., '{\"project_id\": \"work\", \"status\": \"pending\"}')")
    parser.add_argument("--agent-id", help="Optional agent ID to scope context to")
    args = parser.parse_args()
    create_context(args.name, args.filter_query, args.agent_id)
