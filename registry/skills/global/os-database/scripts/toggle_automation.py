#!/usr/bin/env python3
"""Toggle automation enabled/disabled."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def toggle_automation(automation_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT enabled FROM automations WHERE id = ?", (automation_id,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Automation {automation_id} not found"}))
        conn.close()
        return

    new_enabled = 0 if row[0] else 1
    cursor.execute("UPDATE automations SET enabled = ? WHERE id = ?", (new_enabled, automation_id))
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "automation_id": automation_id,
        "enabled": bool(new_enabled)
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--automation-id", type=int, required=True)
    args = parser.parse_args()
    toggle_automation(args.automation_id)
