#!/usr/bin/env python3
"""Create a task from a template."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timedelta, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def use_template(template_name: str, project_id: str, custom_fields: str = None, created_by_agent_id: str = None):
    config = load_config()
    if not created_by_agent_id:
        created_by_agent_id = config.get("agent_id", "SYSTEM")

    db_path = config.get("db_path")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    fields = {}
    if custom_fields:
        try:
            fields = json.loads(custom_fields)
        except json.JSONDecodeError:
            pass

    cursor.execute("""
        SELECT id, title_template, description_template, default_priority,
               default_tags, default_due_days, subtasks_template
        FROM task_templates WHERE name = ?
    """, (template_name,))

    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Template '{template_name}' not found"}))
        conn.close()
        return

    template_id, title_template, description_template, default_priority, \
        default_tags, default_due_days, subtasks_template = row

    # Fill in placeholders
    title = title_template
    description = description_template or ""

    for key, value in fields.items():
        placeholder = f"{{{key}}}"
        title = title.replace(placeholder, str(value))
        description = description.replace(placeholder, str(value))

    # Calculate due date
    due_date = None
    if default_due_days:
        due_dt = datetime.now(timezone.utc) + timedelta(days=default_due_days)
        due_date = due_dt.isoformat()

    # Generate task ID
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0] + 1
    task_id = f"TASK-{count:03d}"

    now = datetime.now(timezone.utc).isoformat()

    # Create task
    cursor.execute("""
        INSERT INTO tasks (
            id, project_id, title, description, status, priority,
            due_date, tags, created_by_agent_id, created_at, updated_at
        ) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
    """, (task_id, project_id, title, description, default_priority,
          due_date, default_tags, created_by_agent_id, now, now))

    # Create subtasks if any
    subtasks_created = []
    if subtasks_template:
        try:
            subtasks = json.loads(subtasks_template)
            for i, subtask_title in enumerate(subtasks):
                for key, value in fields.items():
                    subtask_title = subtask_title.replace(f"{{{key}}}", str(value))

                subtask_id = f"{task_id}.{i+1}"
                cursor.execute("""
                    INSERT INTO tasks (
                        id, parent_task_id, title, description, status,
                        priority, project_id, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
                """, (subtask_id, task_id, subtask_title, '', default_priority,
                      project_id, now, now))
                subtasks_created.append(subtask_id)
        except json.JSONDecodeError:
            pass

    conn.commit()
    conn.close()

    result = {
        "status": "success",
        "task_id": task_id,
        "title": title,
        "message": f"Task created from template '{template_name}'"
    }
    if subtasks_created:
        result["subtasks"] = subtasks_created

    print(json.dumps(result))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Create a task from a template")
    parser.add_argument("--template-name", required=True, help="Template name to use")
    parser.add_argument("--project-id", required=True, help="Project ID to assign task to")
    parser.add_argument("--custom-fields", help='Custom fields as JSON (e.g., \'{"issue":"Login bug"}\')')
    parser.add_argument("--created-by-agent-id", help="Agent ID creating this task")
    args = parser.parse_args()
    use_template(args.template_name, args.project_id, args.custom_fields, args.created_by_agent_id)
