#!/usr/bin/env python3
"""Relate two tasks with a relationship type."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")

VALID_TYPES = ('blocks', 'blocked_by', 'relates_to', 'duplicates', 'parent', 'child')


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def relate_tasks(from_task_id: str, to_task_id: str, relationship_type: str):
    if relationship_type not in VALID_TYPES:
        print(json.dumps({"status": "error", "message": f"Invalid type. Must be one of: {VALID_TYPES}"}))
        sys.exit(1)

    config = load_config()
    db_path = config.get("db_path")

    # For 'blocks' relationship, check for cycles before creating
    if relationship_type == 'blocks':
        # Import detect_cycle function
        import importlib.util
        detect_cycle_path = os.path.join(SCRIPT_DIR, "scripts", "detect_cycle.py")
        spec = importlib.util.spec_from_file_location("detect_cycle", detect_cycle_path)
        detect_cycle_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(detect_cycle_module)

        has_cycle, cycle_path = detect_cycle_module.check_cycle(db_path, from_task_id, to_task_id)
        if has_cycle:
            print(json.dumps({
                "status": "error",
                "message": "Cannot create blocks relationship - would create cycle",
                "cycle_detected": True,
                "cycle_path": cycle_path
            }))
            sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Verify both tasks exist
    cursor.execute("SELECT id FROM tasks WHERE id IN (?, ?)", (from_task_id, to_task_id))
    existing = {row[0] for row in cursor.fetchall()}
    if from_task_id not in existing or to_task_id not in existing:
        print(json.dumps({"status": "error", "message": "One or both tasks not found"}))
        sys.exit(1)

    try:
        cursor.execute(
            "INSERT INTO task_relationships (from_task_id, to_task_id, relationship_type) VALUES (?, ?, ?)",
            (from_task_id, to_task_id, relationship_type)
        )
        conn.commit()
        relationship_id = cursor.lastrowid
        conn.close()
        print(json.dumps({
            "status": "success",
            "relationship_id": relationship_id,
            "from_task_id": from_task_id,
            "to_task_id": to_task_id,
            "relationship_type": relationship_type
        }))
    except sqlite3.IntegrityError as e:
        conn.close()
        print(json.dumps({"status": "error", "message": f"Relationship already exists: {e}"}))
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--from", dest="from_task_id", required=True, help="Source task ID")
    parser.add_argument("--to", dest="to_task_id", required=True, help="Target task ID")
    parser.add_argument("--type", dest="relationship_type", required=True,
                        choices=VALID_TYPES, help="Relationship type")
    args = parser.parse_args()

    relate_tasks(args.from_task_id, args.to_task_id, args.relationship_type)
