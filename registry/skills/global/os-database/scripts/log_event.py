#!/usr/bin/env python3
"""Log timeline event - auto-reads agent_id and task_id from state/config."""
import sqlite3
import json
import os
import sys
import uuid
from datetime import datetime, timezone

# Add scripts directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _shared_config import load_config, load_state

VALID_TYPES = ['BOOT', 'THOUGHT', 'ACTION', 'TOOL_CALL', 'ERROR', 'HANDOFF', 'COMPLETED']


def log_event(event_type: str, message: str, metadata: dict = None):
    config = load_config()
    state = load_state()

    agent_id = config.get("agent_id")
    task_id = state.get("current_task_id")
    db_path = config.get("db_path")

    if not agent_id:
        print(json.dumps({"status": "error", "message": "agent_id not set in config.json"}))
        return

    if event_type not in VALID_TYPES:
        print(json.dumps({"status": "error", "message": f"Invalid type. Must be: {VALID_TYPES}"}))
        return

    event_id = str(uuid.uuid4())
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO timeline_events (id, task_id, agent_id, event_type, message, metadata, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event_id, task_id, agent_id, event_type, message, json.dumps(metadata) if metadata else None, now))

    conn.commit()
    conn.close()

    print(json.dumps({"status": "success", "event_id": event_id, "event_type": event_type, "task_id": task_id}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=VALID_TYPES)
    parser.add_argument("--msg", required=True)
    parser.add_argument("--meta", help="JSON string")
    args = parser.parse_args()

    metadata = None
    if args.meta:
        try:
            metadata = json.loads(args.meta)
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Invalid JSON in --meta"}))
            sys.exit(1)

    log_event(args.type, args.msg, metadata)
