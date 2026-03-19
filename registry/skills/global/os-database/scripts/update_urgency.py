#!/usr/bin/env python3
"""Calculate and update urgency scores for all tasks."""
import sqlite3
import json
import os
from datetime import datetime, date

DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

PRIORITY_SCORES = {
    "critical": 8,
    "high": 6,
    "medium": 4,
    "low": 2,
    "": 0,
    None: 0,
}

def calculate_urgency(task):
    score = 0
    today = date.today()

    # Priority score
    priority = task.get("priority", "").lower()
    score += PRIORITY_SCORES.get(priority, 0)

    # Due date score
    due_date = task.get("due_date")
    if due_date:
        try:
            if isinstance(due_date, str):
                due = datetime.fromisoformat(due_date.replace("Z", "+00:00")).date()
            else:
                due = due_date

            days_until = (due - today).days

            if days_until < 0:
                score += 10  # Overdue
            elif days_until == 0:
                score += 8   # Due today
            elif days_until <= 7:
                score += 6   # Due this week
            elif days_until <= 30:
                score += 4   # Due this month
        except Exception:
            pass

    # Age score: +1 per day since created
    created_at = task.get("created_at")
    if created_at:
        try:
            if isinstance(created_at, str):
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                created = created_at

            age_days = (datetime.now(created.tzinfo) - created).days
            score += max(0, age_days)
        except Exception:
            pass

    # Tags score: +2 per tag
    tags = task.get("tags", "")
    if tags:
        tag_list = [t.strip() for t in str(tags).split(",") if t.strip()]
        score += len(tag_list) * 2

    return score


def update_urgency():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    updated = 0
    for task in tasks:
        task_dict = dict(task)
        urgency = calculate_urgency(task_dict)

        cursor.execute(
            "UPDATE tasks SET urgency_score = ? WHERE id = ?",
            (urgency, task["id"])
        )
        updated += 1

    conn.commit()
    conn.close()

    print(f"Updated urgency scores for {updated} tasks")


if __name__ == "__main__":
    update_urgency()
