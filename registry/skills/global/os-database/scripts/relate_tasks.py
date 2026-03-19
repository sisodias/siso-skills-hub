#!/usr/bin/env python3
"""Relate two tasks with a relationship type."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def relate_tasks(from_task_id: str, to_task_id: str, relationship_type: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO task_relationships (from_task_id, to_task_id, relationship_type, created_at)
        VALUES (?, ?, ?, ?)
    """, (from_task_id, to_task_id, relationship_type, now))

    rel_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "relationship_id": rel_id,
        "from_task_id": from_task_id,
        "to_task_id": to_task_id,
        "relationship_type": relationship_type
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", required=True, dest="from_task_id")
    parser.add_argument("--to", required=True, dest="to_task_id")
    parser.add_argument("--type", required=True, dest="relationship_type")
    args = parser.parse_args()
    relate_tasks(args.from_task_id, args.to_task_id, args.relationship_type)
