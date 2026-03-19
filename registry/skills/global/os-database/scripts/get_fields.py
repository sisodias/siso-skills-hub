#!/usr/bin/env python3
"""Get custom field values for a task."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def get_fields(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            d.id, d.name, d.field_key, d.field_type, d.description, d.options,
            v.value, v.created_at, v.updated_at
        FROM custom_field_definitions d
        LEFT JOIN custom_field_values v ON d.id = v.field_id AND v.task_id = ?
        WHERE d.is_global = 1 OR d.project_id = (SELECT project_id FROM tasks WHERE id = ?)
        ORDER BY d.is_global DESC, d.name
    """, (task_id, task_id))

    rows = cursor.fetchall()
    conn.close()

    fields = []
    for row in rows:
        value = None
        if row['value']:
            try:
                value = json.loads(row['value'])
            except json.JSONDecodeError:
                value = row['value']
        options = None
        if row['options']:
            try:
                options = json.loads(row['options'])
            except json.JSONDecodeError:
                pass
        fields.append({
            "id": row['id'],
            "name": row['name'],
            "field_key": row['field_key'],
            "field_type": row['field_type'],
            "description": row['description'],
            "options": options,
            "value": value,
            "created_at": row['created_at'],
            "updated_at": row['updated_at']
        })

    print(json.dumps({"status": "success", "task_id": task_id, "fields": fields}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    args = parser.parse_args()
    get_fields(args.task_id)
