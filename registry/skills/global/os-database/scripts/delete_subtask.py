#!/usr/bin/env python3
"""Delete a subtask."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def delete_subtask(subtask_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check exists
    cursor.execute("SELECT id, title FROM subtasks WHERE id = ?", (subtask_id,))
    row = cursor.fetchone()

    if not row:
        print(json.dumps({"status": "error", "message": f"Subtask {subtask_id} not found"}))
        conn.close()
        sys.exit(1)

    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "subtask_id": subtask_id,
        "deleted_title": row[0]
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--subtask-id", type=int, required=True, help="Subtask ID to delete")
    args = parser.parse_args()
    delete_subtask(args.subtask_id)
