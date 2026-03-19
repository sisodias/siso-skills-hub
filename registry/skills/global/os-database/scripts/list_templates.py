#!/usr/bin/env python3
"""List all task templates."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def list_templates():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_templates'")
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": "Table 'task_templates' does not exist in this database schema"}))
        conn.close()
        return

    cursor.execute("""
        SELECT id, name, title_template, description_template, default_priority,
               default_tags, default_due_days, subtasks_template, created_at
        FROM task_templates ORDER BY name
    """)

    templates = []
    for row in cursor.fetchall():
        templates.append(dict(row))

    conn.close()

    if not templates:
        print(json.dumps({"status": "success", "templates": [], "message": "No templates found"}))
    else:
        print(json.dumps({"status": "success", "templates": templates}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="List all task templates")
    args = parser.parse_args()
    list_templates()
