#!/usr/bin/env python3
"""Create a new automation."""
import sqlite3
import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def create_automation(name: str, trigger_event: str, trigger_condition: str,
                     action_type: str, action_config: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO automations (name, trigger_event, trigger_condition, action_type, action_config)
                      VALUES (?, ?, ?, ?, ?)""",
                   (name, trigger_event, trigger_condition, action_type, action_config))

    automation_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "automation_id": automation_id, "name": name}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True, help="Automation name")
    parser.add_argument("--trigger-event", required=True, help="Event that triggers the automation")
    parser.add_argument("--trigger-condition", required=True, help="JSON condition to match")
    parser.add_argument("--action-type", required=True, help="Action type (log, alert, escalate)")
    parser.add_argument("--action-config", required=True, help="JSON config for the action")
    args = parser.parse_args()

    create_automation(args.name, args.trigger_event, args.trigger_condition,
                     args.action_type, args.action_config)
