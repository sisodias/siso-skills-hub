#!/usr/bin/env python3
"""Find tasks where all blockers are completed (ready to work)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def get_ready_tasks(db_path, agent_id: str = None):
    """Find tasks that are unblocked and ready to work."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all incomplete tasks
    cursor.execute("SELECT id FROM tasks WHERE status != 'completed'")
    incomplete = {row[0] for row in cursor.fetchall()}

    # Get all blocks relationships
    cursor.execute("""
        SELECT from_task_id, to_task_id
        FROM task_relationships
        WHERE relationship_type = 'blocks'
    """)

    # Build graph: task -> tasks it blocks
    blocks = {}
    for from_t, to_t in cursor.fetchall():
        if from_t not in blocks:
            blocks[from_t] = []
        blocks[from_t].append(to_t)

    # Find tasks that are blocked by incomplete tasks
    blocked_by_incomplete = set()
    for blocker, blocked_list in blocks.items():
        if blocker in incomplete:
            for blocked_task in blocked_list:
                if blocked_task in incomplete:
                    blocked_by_incomplete.add(blocked_task)

    # Get pending tasks
    query = """
        SELECT id, title, description, status, priority, due_date, urgency_score
        FROM tasks
        WHERE status = 'pending'
    """
    if agent_id:
        query += " AND assigned_agent_id = ?"
        cursor.execute(query, (agent_id,))
    else:
        cursor.execute(query)

    rows = cursor.fetchall()
    conn.close()

    # Filter to only ready tasks (not blocked by incomplete)
    ready = []
    for row in rows:
        task_id = row[0]
        if task_id not in blocked_by_incomplete:
            ready.append({
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "due_date": row[5],
                "urgency_score": row[6]
            })

    return ready


def ready_tasks_cmd(agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    if not agent_id:
        agent_id = config.get("agent_id")

    ready = get_ready_tasks(db_path, agent_id)

    print(json.dumps({
        "status": "success",
        "agent_id": agent_id,
        "ready_tasks": ready,
        "count": len(ready)
    }, default=str))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find tasks where all blockers are completed")
    parser.add_argument("--agent-id", help="Filter by agent ID")
    args = parser.parse_args()

    ready_tasks_cmd(args.agent_id)
