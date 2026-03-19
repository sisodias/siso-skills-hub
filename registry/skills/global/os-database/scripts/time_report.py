#!/usr/bin/env python3
"""Show time estimate vs actual for a task."""
import sqlite3
import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def time_report(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, estimated_minutes, time_spent, status, created_at, completed_at
        FROM tasks WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        return

    task_id, title, estimated, time_spent, status, created_at, completed_at = row
    estimated = estimated or 0
    time_spent = time_spent or 0

    # Calculate variance
    if estimated > 0:
        variance = time_spent - estimated
        variance_pct = round((variance / estimated) * 100, 1)
    else:
        variance = None
        variance_pct = None

    result = {
        "status": "success",
        "task_id": task_id,
        "title": title,
        "estimated_minutes": estimated,
        "time_spent_minutes": time_spent,
        "status": status,
    }

    if variance is not None:
        result["variance_minutes"] = variance
        result["variance_percent"] = variance_pct
        if variance > 0:
            result["verdict"] = f"Over by {variance} min ({variance_pct}%)"
        elif variance < 0:
            result["verdict"] = f"Under by {abs(variance)} min ({abs(variance_pct)}%)"
        else:
            result["verdict"] = "On time"
    else:
        result["verdict"] = "No estimate set"

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID (e.g., TASK-001)")
    args = parser.parse_args()
    time_report(args.task_id)
