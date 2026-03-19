#!/usr/bin/env python3
"""Delete a subtask."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def delete_subtask(subtask_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "deleted": deleted, "subtask_id": subtask_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--subtask-id", type=int, required=True)
    args = parser.parse_args()
    delete_subtask(args.subtask_id)
