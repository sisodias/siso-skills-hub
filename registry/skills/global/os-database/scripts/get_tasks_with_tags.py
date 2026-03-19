#!/usr/bin/env python3
"""Virtual tags helper - computes tags at query time."""
import sqlite3
import json
import os
from datetime import datetime, timedelta

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def compute_virtual_tags(due_date_str, blocked_by_id, status, all_task_ids):
    """Compute virtual tags for a task."""
    tags = []
    now = datetime.now()

    # BLOCKED: task has blocked_by_task_id pointing to incomplete task
    if blocked_by_id and blocked_by_id in all_task_ids:
        # Check if blocking task is incomplete
        tags.append("BLOCKED")

    # OVERDUE: due_date is in the past
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            if due_date < now:
                tags.append("OVERDUE")
        except ValueError:
            pass

    # WEEK: due_date is within current week
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            now = datetime.now()
            week_end = now + timedelta(days=7)
            if now <= due_date <= week_end:
                tags.append("WEEK")
        except ValueError:
            pass

    # MONTH: due_date is within current month
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            now = datetime.now()
            if now <= due_date <= now.replace(day=28) + timedelta(days=7):  # rough month check
                tags.append("MONTH")
        except ValueError:
            pass

    # READY: pending AND not blocked AND (no due_date OR due_date <= now)
    if status == "pending":
        is_blocked = blocked_by_id and blocked_by_id in all_task_ids
        has_due = bool(due_date_str)
        if not is_blocked:
            if not has_due:
                tags.append("READY")
            else:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
                    if due_date <= now:
                        tags.append("READY")
                except ValueError:
                    pass

    return tags


def get_tasks_with_virtual_tags(agent_id=None, project_id=None, tag=None):
    """Get tasks with computed virtual tags."""
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get all task IDs that are incomplete (for BLOCKED check)
    cursor.execute("SELECT id FROM tasks WHERE status != 'completed'")
    incomplete_tasks = {row[0] for row in cursor.fetchall()}

    # Base query
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

    # Compute virtual tags for each task
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

    # Filter by tag if specified
    if tag:
        tasks = [t for t in tasks if tag in t["virtual_tags"]]

    return tasks


def list_tasks(tag=None, agent_id=None, project_id=None):
    """CLI entry point for listing tasks with virtual tags."""
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
    parser.add_argument("--tag", choices=["BLOCKED", "OVERDUE", "WEEK", "MONTH", "READY"], help="Filter by virtual tag")
    parser.add_argument("--agent-id", help="Filter by agent ID")
    parser.add_argument("--project-id", help="Filter by project ID")
    args = parser.parse_args()

    list_tasks(args.tag, args.agent_id, args.project_id)
