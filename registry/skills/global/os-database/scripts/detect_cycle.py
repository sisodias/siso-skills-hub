#!/usr/bin/env python3
"""Detect if adding a 'blocks' relationship would create a cycle."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def check_cycle(db_path: str, from_task_id: str, to_task_id: str) -> tuple[bool, list]:
    """
    Check if adding blocks(from_task_id, to_task_id) creates a cycle.
    Returns (has_cycle, path) where path shows the cycle if one exists.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Build adjacency list of blocking relationships
    # blocks: A blocks B means A -> B (A blocks B, so A must complete before B)
    # For cycle detection: if we're adding A blocks B, check if there's a path B -> ... -> A

    cursor.execute("""
        SELECT from_task_id, to_task_id
        FROM task_relationships
        WHERE relationship_type = 'blocks'
    """)

    # Build graph: task -> tasks it blocks
    graph = {}
    for from_t, to_t in cursor.fetchall():
        if from_t not in graph:
            graph[from_t] = []
        graph[from_t].append(to_t)

    # Now check if there's a path from to_task_id to from_task_id
    # Using DFS
    visited = set()
    path = []

    def dfs(node: str) -> bool:
        if node == from_task_id:
            return True
        if node in visited:
            return False
        visited.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if dfs(neighbor):
                return True
        path.pop()
        return False

    cycle_found = dfs(to_task_id)
    conn.close()

    if cycle_found:
        return True, path + [from_task_id]
    return False, []


def detect_cycle(from_task_id: str, to_task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    # Verify both tasks exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id IN (?, ?)", (from_task_id, to_task_id))
    existing = {row[0] for row in cursor.fetchall()}
    conn.close()

    if from_task_id not in existing or to_task_id not in existing:
        print(json.dumps({"status": "error", "message": "One or both tasks not found"}))
        sys.exit(1)

    cycle_found, cycle_path = check_cycle(db_path, from_task_id, to_task_id)

    if cycle_found:
        print(json.dumps({
            "status": "error",
            "message": "Adding this relationship would create a cycle",
            "cycle_detected": True,
            "cycle_path": cycle_path
        }))
        sys.exit(1)
    else:
        print(json.dumps({
            "status": "success",
            "message": "No cycle detected - relationship is safe",
            "cycle_detected": False
        }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Detect if adding blocks relationship would create a cycle")
    parser.add_argument("--from", dest="from_task_id", required=True, help="Source task (will block)")
    parser.add_argument("--to", dest="to_task_id", required=True, help="Target task (will be blocked)")
    args = parser.parse_args()

    detect_cycle(args.from_task_id, args.to_task_id)
