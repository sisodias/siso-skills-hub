#!/usr/bin/env python3
"""Query tasks by custom field value."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def query_by_field(field: str, value: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Resolve field key to field_id
    cursor.execute("SELECT id FROM custom_fields WHERE field_key = ?", (field,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Field '{field}' not found"}))
        conn.close()
        return

    field_id = row[0]

    cursor.execute("""
        SELECT t.id, t.title, t.status, t.project_id, t.priority, v.value, v.updated_at
        FROM tasks t
        JOIN custom_field_values v ON t.id = v.task_id
        WHERE v.field_id = ?
        ORDER BY v.updated_at DESC
    """, (field_id,))

    rows = cursor.fetchall()
    conn.close()

    tasks = []
    for row in rows:
        task_value = None
        if row['value']:
            try:
                task_value = json.loads(row['value'])
            except json.JSONDecodeError:
                task_value = row['value']

        if value and str(task_value).lower() != value.lower():
            continue

        tasks.append({
            "task_id": row['id'],
            "title": row['title'],
            "status": row['status'],
            "project_id": row['project_id'],
            "priority": row['priority'],
            "field_value": task_value,
            "updated_at": row['updated_at']
        })

    print(json.dumps({
        "status": "success",
        "field": field,
        "filter_value": value,
        "count": len(tasks),
        "tasks": tasks
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--field", required=True, help="Field key to query")
    parser.add_argument("--value", help="Filter by specific value")
    args = parser.parse_args()
    query_by_field(args.field, args.value)
