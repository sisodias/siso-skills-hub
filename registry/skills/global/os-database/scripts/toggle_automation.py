#!/usr/bin/env python3
"""Toggle automation enabled/disabled."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def toggle_automation(automation_id: int, enabled: bool):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("UPDATE automations SET enabled = ? WHERE id = ?", (1 if enabled else 0, automation_id))
    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "automation_id": automation_id, "enabled": enabled}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--automation-id", type=int, required=True)
    parser.add_argument("--enabled", type=lambda x: x.lower() == "true", required=True)
    args = parser.parse_args()

    toggle_automation(args.automation_id, args.enabled)
