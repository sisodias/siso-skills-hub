#!/usr/bin/env python3
"""Toggle subtask status between pending and completed."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def toggle_subtask(subtask_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("SELECT status FROM subtasks WHERE id = ?", (subtask_id,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Subtask {subtask_id} not found"}))
        conn.close()
        return

    current_status = row[0]
    new_status = 'completed' if current_status == 'pending' else 'pending'

    cursor.execute("""
        UPDATE subtasks SET status = ?, updated_at = ? WHERE id = ?
    """, (new_status, now, subtask_id))

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "subtask_id": subtask_id,
        "old_status": current_status,
        "new_status": new_status
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--subtask-id", type=int, required=True)
    args = parser.parse_args()
    toggle_subtask(args.subtask_id)
