#!/usr/bin/env python3
"""Track time on a task (start/stop timer)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def ensure_time_spent_column(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT time_spent FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE tasks ADD COLUMN time_spent INTEGER")
        conn.commit()
    conn.close()


def track_time(task_id: str, action: str):
    config = load_config()
    db_path = config.get("db_path")

    ensure_time_spent_column(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc)

    if action == "start":
        cursor.execute("UPDATE tasks SET started_at = ? WHERE id = ?", (now.isoformat(), task_id))
        if cursor.rowcount == 0:
            print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
            conn.close()
            sys.exit(1)
        conn.commit()
        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "action": "start",
            "started_at": now.isoformat(),
            "message": f"Timer started for {task_id}"
        }))

    elif action == "stop":
        cursor.execute("SELECT started_at FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if not row or not row[0]:
            print(json.dumps({"status": "error", "message": f"Task {task_id} has no start time"}))
            conn.close()
            sys.exit(1)

        started_at = datetime.fromisoformat(row[0].replace('Z', '+00:00'))
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=timezone.utc)

        time_spent = int((now - started_at).total_seconds())
        cursor.execute("UPDATE tasks SET time_spent = ?, updated_at = ? WHERE id = ?",
                       (time_spent, now.isoformat(), task_id))
        conn.commit()

        hours, remainder = divmod(time_spent, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{hours}h {minutes}m {seconds}s" if hours else f"{minutes}m {seconds}s"

        print(json.dumps({
            "status": "success",
            "task_id": task_id,
            "action": "stop",
            "time_spent": time_spent,
            "duration": duration_str,
            "message": f"Timer stopped for {task_id}: {duration_str}"
        }))

    conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Track time on a task")
    parser.add_argument("--task-id", required=True, help="Task ID to track time on")
    parser.add_argument("--action", required=True, choices=["start", "stop"], help="Start or stop the timer")
    args = parser.parse_args()
    track_time(args.task_id, args.action)
