#!/usr/bin/env python3
"""Get the current active cycle."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def get_current_cycle():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, goal, start_date, end_date, status, created_at
        FROM cycles WHERE status = 'active' LIMIT 1
    """)
    row = cursor.fetchone()

    if not row:
        # If no active cycle, return the most recent upcoming one
        cursor.execute("""
            SELECT id, name, goal, start_date, end_date, status, created_at
            FROM cycles ORDER BY start_date DESC LIMIT 1
        """)
        row = cursor.fetchone()

    conn.close()

    if not row:
        print(json.dumps({"status": "error", "message": "No cycles found"}))
        return

    cycle = {
        "id": row[0],
        "name": row[1],
        "goal": row[2],
        "start_date": row[3],
        "end_date": row[4],
        "status": row[5],
        "created_at": row[6]
    }

    print(json.dumps({"status": "success", "cycle": cycle}))


if __name__ == "__main__":
    get_current_cycle()
