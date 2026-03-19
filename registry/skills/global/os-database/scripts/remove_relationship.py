#!/usr/bin/env python3
"""Remove a task relationship by ID."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def remove_relationship(relationship_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM task_relationships WHERE id = ?", (relationship_id,))
    if cursor.rowcount == 0:
        conn.close()
        print(json.dumps({"status": "error", "message": "Relationship not found"}))
        sys.exit(1)

    conn.commit()
    conn.close()
    print(json.dumps({"status": "success", "relationship_id": relationship_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--relationship-id", type=int, required=True, help="Relationship ID to remove")
    args = parser.parse_args()

    remove_relationship(args.relationship_id)
