#!/usr/bin/env python3
"""Find all tasks blocked by a given task (transitive closure)."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def find_blocked_chain(db_path: str, task_id: str) -> list:
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
    visited = set()
    blocked = []

    def find_blocked(task: str):
        for blocked_task in blocks.get(task, []):
            if blocked_task not in visited:
                visited.add(blocked_task)
                # Get task details
                cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (blocked_task,))
                row = cursor.fetchone()
                if row:
                    blocked.append({
                        "id": row[0],
                        "title": row[1],
                        "status": row[2]
                    })
                find_blocked(blocked_task)

    # Get source task details
    cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (task_id,))
    target = cursor.fetchone()
    if not target:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        sys.exit(1)

    find_blocked(task_id)
    conn.close()

    return blocked


def find_blocked_chain_cmd(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    blocked = find_blocked_chain(db_path, task_id)

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "blocked_tasks": blocked,
        "count": len(blocked)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find all tasks blocked by a given task (transitive)")
    parser.add_argument("--task-id", required=True, help="Task ID to find blocked tasks for")
    args = parser.parse_args()

    find_blocked_chain_cmd(args.task_id)
