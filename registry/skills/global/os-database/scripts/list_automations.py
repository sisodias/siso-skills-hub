#!/usr/bin/env python3
"""List all automations."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def list_automations():
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='automations'")
    if not cursor.fetchone():
        print(json.dumps({"status": "error", "message": "Table 'automations' does not exist in this database schema"}))
        conn.close()
        return

    cursor.execute("""
        SELECT id, name, trigger_event, trigger_condition, action_type, action_config, enabled
        FROM automations
        ORDER BY name
    """)

    rows = cursor.fetchall()
    conn.close()

    automations = []
    for row in rows:
        auto = dict(row)
        try:
            auto["trigger_condition"] = json.loads(auto["trigger_condition"])
        except (json.JSONDecodeError, TypeError):
            pass
        try:
            auto["action_config"] = json.loads(auto["action_config"])
        except (json.JSONDecodeError, TypeError):
            pass
        automations.append(auto)

    print(json.dumps({"status": "success", "count": len(automations), "automations": automations}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="List all automations")
    args = parser.parse_args()
    list_automations()
