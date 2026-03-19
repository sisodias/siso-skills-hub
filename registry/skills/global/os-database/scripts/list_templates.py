#!/usr/bin/env python3
"""List all task templates."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_templates():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, name, title_template, description_template, default_priority,
               default_tags, default_due_days, subtasks_template, created_at
        FROM task_templates
        ORDER BY name
    """)

    templates = []
    for row in cursor.fetchall():
        templates.append({
            "id": row[0],
            "name": row[1],
            "title_template": row[2],
            "description_template": row[3],
            "default_priority": row[4],
            "default_tags": row[5],
            "default_due_days": row[6],
            "subtasks_template": row[7],
            "created_at": row[8]
        })

    conn.close()

    if not templates:
        print(json.dumps({"status": "success", "templates": [], "message": "No templates found"}))
    else:
        print(json.dumps({"status": "success", "templates": templates}))


if __name__ == "__main__":
    list_templates()
