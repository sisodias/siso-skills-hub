#!/usr/bin/env python3
"""When a task completes, notify all blocked tasks (transitive)."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def propagate_unblock(db_path, task_id: str):
    """Find all tasks that were blocked by this task and are now unblocked."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify task exists
    cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    if not task:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        conn.close()
        sys.exit(1)

    # Get all blocks relationships from this task
    cursor.execute("""
        SELECT from_task_id, to_task_id
        FROM task_relationships
        WHERE relationship_type = 'blocks' AND from_task_id = ?
    """, (task_id,))

    # Build graph: task -> tasks it blocks
    blocks = {}
    for from_t, to_t in cursor.fetchall():
        if from_t not in blocks:
            blocks[from_t] = []
        blocks[from_t].append(to_t)

    # Get all incomplete tasks
    cursor.execute("SELECT id FROM tasks WHERE status != 'completed'")
    incomplete = {row[0] for row in cursor.fetchall()}

    # Find all blocked tasks recursively and check if now unblocked
    visited = set()
    newly_unblocked = []

    def check_unblocked(task: str):
        for blocked_task in blocks.get(task, []):
            if blocked_task not in visited:
                visited.add(blocked_task)

                # Check if all blockers for this task are now complete
                cursor.execute("""
                    SELECT from_task_id
                    FROM task_relationships
                    WHERE relationship_type = 'blocks' AND to_task_id = ?
                """, (blocked_task,))

                blockers = [row[0] for row in cursor.fetchall()]
                all_blockers_complete = all(b not in incomplete for b in blockers)

                if all_blockers_complete:
                    # Get task details
                    cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (blocked_task,))
                    row = cursor.fetchone()
                    if row:
                        newly_unblocked.append({
                            "id": row[0],
                            "title": row[1],
                            "previous_status": row[2],
                            "message": "All blockers completed - task is now ready"
                        })

                # Continue checking transitive blocked tasks
                check_unblocked(blocked_task)

    check_unblocked(task_id)
    conn.close()

    return newly_unblocked


def propagate_unblock_cmd(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    unblocked = propagate_unblock(db_path, task_id)

    print(json.dumps({
        "status": "success",
        "completed_task_id": task_id,
        "newly_unblocked_tasks": unblocked,
        "count": len(unblocked)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Find tasks that are now unblocked after task completion")
    parser.add_argument("--task-id", required=True, help="Task ID that completed")
    args = parser.parse_args()

    propagate_unblock_cmd(args.task_id)
