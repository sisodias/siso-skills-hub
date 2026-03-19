#!/usr/bin/env python3
"""Update a cycle's status."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(os.path.dirname(SCRIPT_DIR), "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def update_cycle(cycle_id: int, status: str = None, name: str = None, goal: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
    if name:
        updates.append("name = ?")
        params.append(name)
    if goal:
        updates.append("goal = ?")
        params.append(goal)

    if not updates:
        print(json.dumps({"status": "error", "message": "No updates provided"}))
        return

    params.append(cycle_id)
    cursor.execute(f"UPDATE cycles SET {', '.join(updates)} WHERE id = ?", params)

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "message": f"Cycle {cycle_id} updated"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle-id", type=int, required=True)
    parser.add_argument("--status", choices=['active', 'upcoming', 'completed'])
    parser.add_argument("--name", help="New name")
    parser.add_argument("--goal", help="New goal")
    args = parser.parse_args()
    update_cycle(args.cycle_id, args.status, args.name, args.goal)
