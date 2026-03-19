#!/usr/bin/env python3
"""Get tasks for a cycle with progress percentage."""
import sqlite3
import json
import os
import sys

# Import shared config from scripts directory
_SCRIPTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPTS_DIR)
from _shared_config import load_config


def get_cycle_tasks(cycle_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get cycle info
    cursor.execute("SELECT id, name, goal, start_date, end_date, status FROM cycles WHERE id = ?", (cycle_id,))
    cycle = cursor.fetchone()
    if not cycle:
        print(json.dumps({"status": "error", "message": f"Cycle {cycle_id} not found"}))
        return

    # Get tasks
    cursor.execute("""
        SELECT id, title, status, priority, created_at, completed_at
        FROM tasks WHERE cycle_id = ? ORDER BY created_at
    """, (cycle_id,))
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    completed = 0
    total = len(rows)

    for row in rows:
        task_status = row[2]
        tasks.append({
            "id": row[0],
            "title": row[1],
            "status": task_status,
            "priority": row[3],
            "created_at": row[4],
            "completed_at": row[5]
        })
        if task_status == "completed":
            completed += 1

    progress = (completed / total * 100) if total > 0 else 0

    print(json.dumps({
        "status": "success",
        "cycle": {
            "id": cycle[0],
            "name": cycle[1],
            "goal": cycle[2],
            "start_date": cycle[3],
            "end_date": cycle[4],
            "status": cycle[5]
        },
        "tasks": tasks,
        "summary": {
            "total": total,
            "completed": completed,
            "progress_percent": round(progress, 1)
        }
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycle-id", type=int, required=True)
    args = parser.parse_args()
    get_cycle_tasks(args.cycle_id)
