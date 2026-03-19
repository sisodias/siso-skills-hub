#!/usr/bin/env python3
"""List all saved contexts."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def list_contexts(agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if agent_id:
        cursor.execute("""
            SELECT id, name, filter_query, agent_id, created_at
            FROM contexts
            WHERE agent_id = ? OR agent_id IS NULL
            ORDER BY name
        """, (agent_id,))
    else:
        cursor.execute("""
            SELECT id, name, filter_query, agent_id, created_at
            FROM contexts
            ORDER BY name
        """)

    rows = cursor.fetchall()
    conn.close()

    contexts = []
    for row in rows:
        contexts.append({
            "id": row[0],
            "name": row[1],
            "filter_query": row[2],
            "agent_id": row[3],
            "created_at": row[4]
        })

    print(json.dumps({
        "status": "success",
        "contexts": contexts,
        "count": len(contexts)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="List saved contexts")
    parser.add_argument("--agent-id", help="Filter by agent ID")
    args = parser.parse_args()
    list_contexts(args.agent_id)
