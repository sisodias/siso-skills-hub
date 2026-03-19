#!/usr/bin/env python3
"""Find all tasks that block a given task (transitive closure)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def find_blockers_recursive(db_path, task_id: str):
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
    blockers = []
    visited = set()

    def dfs(task: str):
        if task in visited:
            return
        visited.add(task)
        for blocker in blocked_by.get(task, []):
            blockers.append(blocker)
            dfs(blocker)

    dfs(task_id)
    conn.close()
    return blockers


def find_blocking_chain(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    blockers = find_blockers_recursive(db_path, task_id)

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocking_tasks": blockers,
        "count": len(blockers)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID")
    args = parser.parse_args()
    find_blocking_chain(args.task_id)
