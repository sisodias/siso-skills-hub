#!/usr/bin/env python3
"""Create a task template."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def create_template(name: str, title_template: str, description_template: str = None,
                    default_priority: str = 'medium', default_tags: str = None,
                    default_due_days: int = 7, subtasks_template: str = None,
                    created_by_agent_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Handle subtasks_template - can be JSON string or plain string
    subtasks_json = subtasks_template
    if subtasks_template and not subtasks_template.startswith('['):
        # It's a comma-separated list, convert to JSON
        items = [s.strip() for s in subtasks_template.split(',')]
        subtasks_json = json.dumps(items)

    try:
        cursor.execute("""
            INSERT INTO task_templates (
                name, title_template, description_template, default_priority,
                default_tags, default_due_days, subtasks_template, created_by_agent_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, title_template, description_template, default_priority,
              default_tags or '', default_due_days, subtasks_json, created_by_agent_id,
              now, now))

        conn.commit()
        template_id = cursor.lastrowid

        print(json.dumps({
            "status": "success",
            "template_id": template_id,
            "name": name,
            "message": f"Template '{name}' created successfully"
        }))
    except sqlite3.IntegrityError as e:
        print(json.dumps({
            "status": "error",
            "message": f"Template '{name}' already exists"
        }))
    finally:
        conn.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a task template")
    parser.add_argument("--name", required=True, help="Template name (unique)")
    parser.add_argument("--title-template", required=True, help="Title template with {placeholders}")
    parser.add_argument("--description-template", help="Description template")
    parser.add_argument("--default-priority", choices=['low', 'medium', 'high'], default='medium')
    parser.add_argument("--default-tags", help="Comma-separated tags")
    parser.add_argument("--default-due-days", type=int, default=7, help="Default due days from creation")
    parser.add_argument("--subtasks-template", help='Subtasks as JSON array or comma-separated (e.g., "[\"Investigate\",\"Fix\"]" or "Investigate,Fix")')
    parser.add_argument("--created-by-agent-id", help="Agent ID creating this template")
    args = parser.parse_args()
    create_template(args.name, args.title_template, args.description_template,
                    args.default_priority, args.default_tags, args.default_due_days,
                    args.subtasks_template, args.created_by_agent_id)
