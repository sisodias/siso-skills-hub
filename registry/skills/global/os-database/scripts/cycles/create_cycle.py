#!/usr/bin/env python3
"""Create a new cycle/sprint."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def create_cycle(name: str, goal: str, start_date: str, end_date: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO cycles (name, goal, start_date, end_date, status)
        VALUES (?, ?, ?, ?, 'upcoming')
    """, (name, goal, start_date, end_date))

    cycle_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "cycle_id": cycle_id,
        "message": f"Cycle '{name}' created ({start_date} to {end_date})"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Cycle name")
    parser.add_argument("--goal", required=True, help="Cycle goal")
    parser.add_argument("--start", required=True, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY-MM-DD)")
    args = parser.parse_args()
    create_cycle(args.name, args.goal, args.start, args.end)
