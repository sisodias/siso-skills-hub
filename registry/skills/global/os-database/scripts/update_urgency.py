#!/usr/bin/env python3
"""Calculate and update urgency scores for all tasks."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def calculate_urgency(due_date_str, priority, status, blocked_by_id):
    """Calculate urgency score (0-100) for a task."""
    score = 0
    now = datetime.now(timezone.utc)

    # Base score from priority
    priority_scores = {"critical": 40, "high": 30, "medium": 20, "low": 10}
    score += priority_scores.get(priority, 15)

    # Overdue tasks get max urgency boost
    if due_date_str:
        try:
            due = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            if due.tzinfo:
                due = due.replace(tzinfo=None)
            if due < now:
                score += 50
            else:
                days_until = (due - now).total_seconds() / 86400
                if days_until <= 1:
                    score += 30
                elif days_until <= 3:
                    score += 20
                elif days_until <= 7:
                    score += 10
        except ValueError:
            pass

    # Blocked tasks get a slight reduction
    if blocked_by_id:
        score = max(0, score - 10)

    return min(100, score)


def update_urgency():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Ensure urgency_score column exists
    try:
        cursor.execute("SELECT urgency_score FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE tasks ADD COLUMN urgency_score INTEGER DEFAULT 0")
        conn.commit()

    cursor.execute("SELECT id, due_date, priority, status, blocked_by_task_id FROM tasks")
    rows = cursor.fetchall()

    updated = 0
    for row in rows:
        score = calculate_urgency(
            row['due_date'],
            row['priority'],
            row['status'],
            row['blocked_by_task_id']
        )
        cursor.execute("UPDATE tasks SET urgency_score = ? WHERE id = ?", (score, row['id']))
        updated += 1

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "updated": updated,
        "message": f"Urgency scores updated for {updated} tasks"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Calculate and update urgency scores for all tasks")
    args = parser.parse_args()
    update_urgency()
