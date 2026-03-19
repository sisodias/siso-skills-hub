#!/usr/bin/env python3
"""Hook script to log events to os-database."""
import sqlite3
import json
import os
import sys
import uuid
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def log_event(agent_id: str, event_type: str, message: str, metadata: str = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    event_id = str(uuid.uuid4())
    timestamp = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO timeline_events (id, agent_id, event_type, message, metadata, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event_id, agent_id, event_type, message, metadata, timestamp))

    conn.commit()
    conn.close()
    print(f"Logged {event_type}: {message}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Log an event to the timeline")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--event-type", required=True, help="Event type (e.g., THOUGHT, ACTION)")
    parser.add_argument("--message", required=True, help="Event message")
    parser.add_argument("--metadata", help="Optional metadata as JSON")
    args = parser.parse_args()

    log_event(args.agent_id, args.event_type, args.message, args.metadata)
