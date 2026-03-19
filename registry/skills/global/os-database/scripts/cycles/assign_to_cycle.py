#!/usr/bin/env python3
"""Assign a task to a cycle."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def assign_to_cycle(task_id: str, cycle_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        return

    # Check cycle exists
    cursor.execute("SELECT id FROM cycles WHERE id = ?", (cycle_id,))
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": f"Cycle {cycle_id} not found"}))
        return

    cursor.execute("UPDATE tasks SET cycle_id = ? WHERE id = ?", (cycle_id, task_id))

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "message": f"Task {task_id} assigned to cycle {cycle_id}"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--cycle-id", type=int, required=True)
    args = parser.parse_args()
    assign_to_cycle(args.task_id, args.cycle_id)
