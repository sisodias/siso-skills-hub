#!/usr/bin/env python3
"""Show all tasks with estimate vs actual comparison."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def compare_estimates():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, estimated_minutes, time_spent, status
        FROM tasks
        WHERE estimated_minutes > 0 OR time_spent > 0
        ORDER BY completed_at DESC, created_at DESC
        LIMIT 50
    """)

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print(json.dumps({"status": "success", "message": "No tasks with time tracking data", "tasks": []}))
        return

    tasks = []
    total_estimated = 0
    total_actual = 0

    for row in rows:
        task_id, title, estimated, time_spent, status = row
        estimated = estimated or 0
        time_spent = time_spent or 0

        if estimated > 0:
            variance = time_spent - estimated
            variance_pct = round((variance / estimated) * 100, 1)
        else:
            variance = None
            variance_pct = None

        task = {
            "task_id": task_id,
            "title": title[:50] + "..." if len(title) > 50 else title,
            "status": status,
            "estimated_minutes": estimated,
            "time_spent_minutes": time_spent,
        }

        if variance is not None:
            task["variance_minutes"] = variance
            task["variance_percent"] = variance_pct

        tasks.append(task)
        total_estimated += estimated
        total_actual += time_spent

    if total_estimated > 0:
        total_variance = total_actual - total_estimated
        total_variance_pct = round((total_variance / total_estimated) * 100, 1)
    else:
        total_variance = None
        total_variance_pct = None

    result = {
        "status": "success",
        "summary": {
            "total_estimated_minutes": total_estimated,
            "total_time_spent_minutes": total_actual,
        },
    }

    if total_variance is not None:
        result["summary"]["total_variance_minutes"] = total_variance
        result["summary"]["total_variance_percent"] = total_variance_pct

    result["tasks"] = tasks
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Compare estimates vs actual time across tasks")
    args = parser.parse_args()
    compare_estimates()
