#!/usr/bin/env python3
"""Find all tasks that block a given task (transitive closure)."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def find_blocking_chain(db_path: str, task_id: str) -> list:
    """Find all tasks that block this task, recursively."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all blocks relationships: A blocks B means A is a blocker
    cursor.execute("""
        SELECT from_task_id, to_task_id
        FROM task_relationships
        WHERE relationship_type = 'blocks'
    """)

    # Build reverse graph: task -> tasks that block it
    blocked_by = {}
    for from_t, to_t in cursor.fetchall():
        if to_t not in blocked_by:
            blocked_by[to_t] = []
        blocked_by[to_t].append(from_t)

    # Find all blockers recursively
    visited = set()
    blockers = []

    def find_blockers(task: str):
        for blocker in blocked_by.get(task, []):
            if blocker not in visited:
                visited.add(blocker)
                # Get task details
                cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (blocker,))
                row = cursor.fetchone()
                if row:
                    blockers.append({
                        "id": row[0],
                        "title": row[1],
                        "status": row[2]
                    })
                find_blockers(blocker)

    # Get target task details
    cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (task_id,))
    target = cursor.fetchone()
    if not target:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        sys.exit(1)

    find_blockers(task_id)
    conn.close()

    return blockers


def find_blocking_chain_cmd(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    blockers = find_blocking_chain(db_path, task_id)

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocking_tasks": blockers,
        "count": len(blockers)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find all tasks blocking a given task (transitive)")
    parser.add_argument("--task-id", required=True, help="Task ID to find blockers for")
    args = parser.parse_args()

    find_blocking_chain_cmd(args.task_id)
