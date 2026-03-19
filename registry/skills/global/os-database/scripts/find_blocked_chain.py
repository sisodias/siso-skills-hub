#!/usr/bin/env python3
"""Find all tasks blocked by a given task (transitive closure)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def find_blocked_recursive(db_path, task_id: str):
    """Find all tasks blocked by this task, recursively."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all blocks relationships: A blocks B means A blocks B
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

    # Find all blocked tasks recursively
    blocked = []
    visited = set()

    def dfs(task: str):
        if task in visited:
            return
        visited.add(task)
        for blocked_task in blocks.get(task, []):
            blocked.append(blocked_task)
            dfs(blocked_task)

    dfs(task_id)
    conn.close()
    return blocked


def find_blocked_chain(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    blocked = find_blocked_recursive(db_path, task_id)

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocked_tasks": blocked,
        "count": len(blocked)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, help="Task ID")
    args = parser.parse_args()
    find_blocked_chain(args.task_id)
