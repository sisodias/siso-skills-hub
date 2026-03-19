#!/usr/bin/env python3
"""List all relationships for a task."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_relationships(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get relationships where task is either source or target
    cursor.execute("""
        SELECT id, from_task_id, to_task_id, relationship_type, created_at
        FROM task_relationships
        WHERE from_task_id = ? OR to_task_id = ?
        ORDER BY created_at DESC
    """, (task_id, task_id))

    relationships = []
    for row in cursor.fetchall():
        relationships.append({
            "id": row[0],
            "from_task_id": row[1],
            "to_task_id": row[2],
            "relationship_type": row[3],
            "created_at": row[4]
        })

    conn.close()
    print(json.dumps({"task_id": task_id, "relationships": relationships, "count": len(relationships)}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID to list relationships for")
    args = parser.parse_args()

    list_relationships(args.task_id)
