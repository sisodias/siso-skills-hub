#!/usr/bin/env python3
"""Get tasks for current agent - auto-reads config."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared_config import load_config


def compute_virtual_tags(due_date_str, blocked_by_id, status, incomplete_tasks, task_id, db_path, all_blocking_tasks=None):
    """Compute virtual tags for a task.
    If all_blocking_tasks dict is provided, use it to avoid N+1 queries.
    """
    tags = []
    now = datetime.now()

    # Get blocking tasks - use pre-fetched dict if available (fixes N+1 DB connections)
    if all_blocking_tasks is not None:
        blocking_tasks = all_blocking_tasks.get(task_id, [])
    else:
        # Fallback: single query per task (less efficient)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT from_task_id FROM task_relationships
            WHERE relationship_type = 'blocks' AND to_task_id = ?
        """, (task_id,))
        blocking_tasks = [row[0] for row in cursor.fetchall()]
        conn.close()

    # BLOCKED: task has blocked_by_task_id OR has blocks relationship from incomplete task
    is_blocked = False
    if blocked_by_id and blocked_by_id in incomplete_tasks:
        is_blocked = True
    elif any(b in incomplete_tasks for b in blocking_tasks):
        is_blocked = True

    if is_blocked:
        tags.append("BLOCKED")

    # OVERDUE: due_date is in the past
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00'))
            if due_date.replace(tzinfo=None) < now:
                tags.append("OVERDUE")
        except ValueError:
            pass

    # WEEK: due_date is within current week
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            week_end = now + timedelta(days=7)
            if now <= due_date <= week_end:
                tags.append("WEEK")
        except ValueError:
            pass

    # MONTH: due_date is within current month
    if due_date_str:
        try:
            due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
            month_end = now.replace(day=28) + timedelta(days=7)
            if now <= due_date <= month_end:
                tags.append("MONTH")
        except ValueError:
            pass

    # READY: pending AND not blocked AND (no due_date OR due_date <= now)
    if status == "pending":
        if not is_blocked:
            if not due_date_str:
                tags.append("READY")
            else:
                try:
                    due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).replace(tzinfo=None)
                    if due_date <= now:
                        tags.append("READY")
                except ValueError:
                    pass

    return tags


def get_tasks(agent_id=None, tag=None):
    config = load_config()

    if not agent_id:
        agent_id = config.get("agent_id")

    db_path = config.get("db_path")

    if not agent_id:
        print(json.dumps({"status": "error", "message": "agent_id not set in config.json"}))
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get incomplete task IDs for BLOCKED check
    cursor.execute("SELECT id FROM tasks WHERE status != 'completed'")
    incomplete_tasks = {row[0] for row in cursor.fetchall()}

    # Pre-fetch all blocking relationships to avoid N+1 queries (fix for Bug 3)
    cursor.execute("""
        SELECT to_task_id, from_task_id FROM task_relationships
        WHERE relationship_type = 'blocks'
    """)
    all_blocking_tasks = {}
    for to_task, from_task in cursor.fetchall():
        if to_task not in all_blocking_tasks:
            all_blocking_tasks[to_task] = []
        all_blocking_tasks[to_task].append(from_task)

    # Build query
    query = """
        SELECT id, title, description, status, priority, due_date, blocked_by_task_id, urgency_score, tags, created_at
        FROM tasks
        WHERE assigned_agent_id = ?
    """
    params = [agent_id]

    # Note: tag filtering is done in Python after fetching
    cursor.execute(query, params)

    rows = cursor.fetchall()
    conn.close()

    # Compute virtual tags (using pre-fetched blocking tasks to avoid N+1)
    tasks = []
    for row in rows:
        task = dict(row)
        task["virtual_tags"] = compute_virtual_tags(
            task.get("due_date"),
            task.get("blocked_by_task_id"),
            task.get("status"),
            incomplete_tasks,
            task.get("id"),
            db_path,
            all_blocking_tasks
        )

        # Filter by tag if specified
        if tag:
            if tag in task["virtual_tags"]:
                tasks.append(task)
        else:
            tasks.append(task)

    # Sort: urgency_score desc (includes priority, due_date, age, tags), then ready tasks
    tasks.sort(key=lambda t: (
        -(t.get("urgency_score") or 0),
        -1 if "READY" in t.get("virtual_tags", []) else 0,
        t.get("created_at", "")
    ))

    print(json.dumps({
        "status": "success",
        "agent_id": agent_id,
        "tag_filter": tag,
        "count": len(tasks),
        "tasks": tasks
    }, indent=2, default=str))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", choices=["BLOCKED", "OVERDUE", "WEEK", "MONTH", "READY"], help="Filter by virtual tag")
    parser.add_argument("--agent-id", help="Override agent ID")
    args = parser.parse_args()

    get_tasks(args.agent_id, args.tag)
