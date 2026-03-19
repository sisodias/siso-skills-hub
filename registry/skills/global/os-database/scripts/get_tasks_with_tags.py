#!/usr/bin/env python3
"""Get tasks with virtual tags computed at query time."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def compute_virtual_tags(due_date_str, blocked_by_id, status, incomplete_tasks):
    tags = []
    now = datetime.now()

    if blocked_by_id and blocked_by_id in incomplete_tasks:
        tags.append("BLOCKED")

    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            if due_date.replace(tzinfo=None) < now:
                tags.append("OVERDUE")
            week_end = now + timedelta(days=7)
            if now <= due_date.replace(tzinfo=None) <= week_end:
                tags.append("WEEK")
        except ValueError:
            pass

    if status == "pending":
        is_blocked = blocked_by_id and blocked_by_id in incomplete_tasks
        if not is_blocked:
            if not due_date_str:
                tags.append("READY")
            else:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    if due_date.replace(tzinfo=None) <= now:
                        tags.append("READY")
                except ValueError:
                    pass

    return tags


def get_tasks_with_virtual_tags(agent_id=None, project_id=None, tag=None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM tasks WHERE status != 'completed'")
    incomplete_tasks = {row[0] for row in cursor.fetchall()}

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if agent_id:
        query += " AND assigned_agent_id = ?"
        params.append(agent_id)
    if project_id:
        query += " AND project_id = ?"
        params.append(project_id)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        task = dict(row)
        task["virtual_tags"] = compute_virtual_tags(
            task.get("due_date"),
            task.get("blocked_by_task_id"),
            task.get("status"),
            incomplete_tasks
        )
        tasks.append(task)

    if tag:
        tasks = [t for t in tasks if tag in t["virtual_tags"]]

    return tasks


def list_tasks(tag=None, agent_id=None, project_id=None):
    config = load_config()
    if not agent_id:
        agent_id = config.get("agent_id")

    tasks = get_tasks_with_virtual_tags(agent_id, project_id, tag)

    print(json.dumps({
        "status": "success",
        "tag_filter": tag,
        "agent_id": agent_id,
        "count": len(tasks),
        "tasks": tasks
    }, indent=2, default=str))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Get tasks with virtual tags")
    parser.add_argument("--tag", choices=["BLOCKED", "OVERDUE", "WEEK", "MONTH", "READY"])
    parser.add_argument("--agent-id")
    parser.add_argument("--project-id")
    args = parser.parse_args()
    list_tasks(args.tag, args.agent_id, args.project_id)
