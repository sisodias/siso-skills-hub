#!/usr/bin/env python3
"""Set time estimate for a task."""
import sqlite3
import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def estimate_task(task_id: str, minutes: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("UPDATE tasks SET estimated_minutes = ?, updated_at = ? WHERE id = ?",
                   (minutes, now, task_id))

    if cursor.rowcount == 0:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        return

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "estimated_minutes": minutes,
        "message": f"Estimate set to {minutes} minutes"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID (e.g., TASK-001)")
    parser.add_argument("--minutes", type=int, required=True, help="Estimated time in minutes")
    args = parser.parse_args()
    estimate_task(args.task_id, args.minutes)
