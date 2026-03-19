#!/usr/bin/env python3
"""Create a task and its workspace folder."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
STATE_PATH = os.path.join(SCRIPT_DIR, "state.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def create_task(project_id: str, title: str, description: str, assigned_agent: str = None, priority: str = 'medium', due_date: str = None, create_workspace: bool = False, estimated_minutes: int = None, fields: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Generate task ID
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0] + 1
    task_id = f"TASK-{count:03d}"

    # Create workspace folder only if requested
    workspace_path = None
    if create_workspace:
        agent_root = config.get("root_path")
        workspace_path = f"{agent_root}/workspace/{task_id}"
        os.makedirs(workspace_path, exist_ok=True)
        os.makedirs(f"{workspace_path}/input", exist_ok=True)
        os.makedirs(f"{workspace_path}/output", exist_ok=True)
        os.makedirs(f"{workspace_path}/work", exist_ok=True)

    # Insert task
    cursor.execute("""
        INSERT INTO tasks (id, project_id, title, description, assigned_agent_id, status, priority, due_date, workspace_path, created_at, updated_at, estimated_minutes)
        VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?, ?, ?, ?)
    """, (task_id, project_id, title, description, assigned_agent, priority, due_date, workspace_path, now, now, estimated_minutes))

    # Insert custom field values if provided
    if fields:
        try:
            fields_dict = json.loads(fields)
            for field_key, field_value in fields_dict.items():
                # Find field by field_key
                cursor.execute("SELECT id FROM custom_field_definitions WHERE field_key = ?", (field_key,))
                field_row = cursor.fetchone()
                if field_row:
                    field_id = field_row[0]
                    cursor.execute("""
                        INSERT INTO custom_field_values (task_id, field_id, value, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (task_id, field_id, json.dumps(field_value), now, now))
        except json.JSONDecodeError as e:
            print(json.dumps({"status": "error", "message": f"Invalid JSON in fields: {e}"}))
            conn.close()
            return

    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "workspace_path": workspace_path,
        "message": f"Task created" + (f" at {workspace_path}" if workspace_path else " (no workspace)")
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description", required=True)
    parser.add_argument("--assign", help="Agent ID to assign")
    parser.add_argument("--priority", choices=['low', 'medium', 'high'], default='medium', help="Task priority")
    parser.add_argument("--due-date", help="Due date (optional, ISO format)")
    parser.add_argument("--workspace", action="store_true", help="Create workspace folder for this task")
    parser.add_argument("--estimate", type=int, help="Estimated time in minutes")
    parser.add_argument("--fields", help="JSON object of field_key: value pairs")
    args = parser.parse_args()
    create_task(args.project_id, args.title, args.description, args.assign, args.priority, args.due_date, args.workspace, args.estimate, args.fields)
