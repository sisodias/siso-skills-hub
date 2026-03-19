#!/usr/bin/env python3
"""List all cycles."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_cycles():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, goal, start_date, end_date, status, created_at
        FROM cycles ORDER BY start_date DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    cycles = []
    for row in rows:
        cycles.append({
            "id": row[0],
            "name": row[1],
            "goal": row[2],
            "start_date": row[3],
            "end_date": row[4],
            "status": row[5],
            "created_at": row[6]
        })

    print(json.dumps({"status": "success", "cycles": cycles}))


if __name__ == "__main__":
    list_cycles()
