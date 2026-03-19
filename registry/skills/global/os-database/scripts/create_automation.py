#!/usr/bin/env python3
"""Create a new automation."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def create_automation(name: str, trigger_event: str, trigger_condition: str, action_type: str, action_config: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO automations (name, trigger_event, trigger_condition, action_type, action_config)
        VALUES (?, ?, ?, ?, ?)
    """, (name, trigger_event, trigger_condition, action_type, action_config))

    automation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "automation_id": automation_id, "name": name}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--trigger-event", required=True)
    parser.add_argument("--trigger-condition", required=True)
    parser.add_argument("--action-type", required=True)
    parser.add_argument("--action-config", required=True)
    args = parser.parse_args()
    create_automation(args.name, args.trigger_event, args.trigger_condition, args.action_type, args.action_config)
