#!/usr/bin/env python3
"""List all automations."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def list_automations(enabled_only: bool = False):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = "SELECT id, name, trigger_event, trigger_condition, action_type, action_config, enabled, created_at FROM automations"
    if enabled_only:
        query += " WHERE enabled = 1"

    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    automations = []
    for row in rows:
        automations.append({
            "id": row[0],
            "name": row[1],
            "trigger_event": row[2],
            "trigger_condition": row[3],
            "action_type": row[4],
            "action_config": row[5],
            "enabled": bool(row[6]),
            "created_at": row[7]
        })

    print(json.dumps(automations, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--enabled-only", action="store_true", help="Show only enabled automations")
    args = parser.parse_args()

    list_automations(args.enabled_only)
