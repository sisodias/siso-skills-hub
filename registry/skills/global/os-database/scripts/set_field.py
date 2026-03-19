#!/usr/bin/env python3
"""Set a custom field value for a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def set_field(task_id: str, field: str, value: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Resolve field key to field_id
    cursor.execute("SELECT id FROM custom_fields WHERE field_key = ?", (field,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Field '{field}' not found"}))
        conn.close()
        return

    field_id = row[0]

    # Try to interpret value as JSON, else store as string
    try:
        value_json = json.dumps(json.loads(value))
    except (json.JSONDecodeError, TypeError):
        value_json = json.dumps(value)

    cursor.execute("""
        INSERT INTO custom_field_values (task_id, field_id, value, created_at, updated_at)
        VALUES (?, ?, ?, datetime('now'), datetime('now'))
        ON CONFLICT(task_id, field_id) DO UPDATE SET value = excluded.value, updated_at = datetime('now')
    """, (task_id, field_id, value_json))

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "field": field,
        "value": value,
        "message": f"Field '{field}' set to '{value}' for task {task_id}"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True, dest="task_id", help="Task ID")
    parser.add_argument("--field", required=True, help="Field key")
    parser.add_argument("--value", required=True, help="Field value")
    args = parser.parse_args()
    set_field(args.task_id, args.field, args.value)
