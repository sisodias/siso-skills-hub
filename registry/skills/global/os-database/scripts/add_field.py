#!/usr/bin/env python3
"""Add a custom field definition."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def add_field(name: str, field_type: str, field_key: str, description: str = None, is_global: bool = False, project_id: str = None, options: str = None, is_required: bool = False):
    config = load_config()
    db_path = config.get("db_path")

    options_json = json.dumps(json.loads(options)) if options else None

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO custom_field_definitions (name, field_type, field_key, description, is_global, project_id, options, is_required)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (name, field_type, field_key, description, 1 if is_global else 0, project_id, options_json, 1 if is_required else 0))

    field_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "field_id": field_id,
        "field_key": field_key,
        "message": f"Field '{name}' created with key '{field_key}'"
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Field display name")
    parser.add_argument("--type", required=True, dest="field_type",
                        choices=['text', 'number', 'date', 'select', 'multi_select', 'url', 'checkbox'],
                        help="Field type")
    parser.add_argument("--field-key", required=True, dest="field_key", help="Unique field key")
    parser.add_argument("--description", help="Field description")
    parser.add_argument("--global", dest="is_global", action="store_true", help="Make field global")
    parser.add_argument("--project-id", dest="project_id", help="Project-specific field")
    parser.add_argument("--options", help="JSON array of options for select/multi_select types")
    parser.add_argument("--required", dest="is_required", action="store_true", help="Field is required")
    args = parser.parse_args()
    add_field(args.name, args.field_type, args.field_key, args.description,
              args.is_global, args.project_id, args.options, args.is_required)
