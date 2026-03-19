#!/usr/bin/env python3
"""Set a custom field value for a task."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def set_field(task_id: str, field: str, value: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Find field by field_key
    cursor.execute("SELECT id, field_type FROM custom_field_definitions WHERE field_key = ?", (field,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Field '{field}' not found"}))
        conn.close()
        return

    field_id, field_type = row

    # Check if task exists
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": f"Task '{task_id}' not found"}))
        conn.close()
        return

    # Validate value based on field type
    try:
        if field_type == 'number':
            float(value)  # Validate it's a number
        elif field_type == 'checkbox':
            if value.lower() not in ('true', 'false', '1', '0', 'yes', 'no'):
                raise ValueError("Checkbox must be true/false")
        value_json = json.dumps(value)
    except (json.JSONDecodeError, ValueError) as e:
        print(json.dumps({"status": "error", "message": f"Invalid value for field type {field_type}: {e}"}))
        conn.close()
        return

    # Upsert the value
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
