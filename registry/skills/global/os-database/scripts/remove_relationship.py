#!/usr/bin/env python3
"""Remove a task relationship by ID."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def remove_relationship(relationship_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM task_relationships WHERE id = ?", (relationship_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "deleted": deleted, "relationship_id": relationship_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--relationship-id", type=int, required=True)
    args = parser.parse_args()
    remove_relationship(args.relationship_id)
