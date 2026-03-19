#!/usr/bin/env python3
"""List all relationships for a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def list_relationships(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, from_task_id, to_task_id, relationship_type, created_at
        FROM task_relationships
        WHERE from_task_id = ? OR to_task_id = ?
        ORDER BY created_at DESC
    """, (task_id, task_id))

    relationships = [dict(row) for row in cursor.fetchall()]
    conn.close()
    print(json.dumps({"task_id": task_id, "relationships": relationships, "count": len(relationships)}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    list_relationships(args.task_id)
