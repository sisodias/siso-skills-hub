#!/usr/bin/env python3
"""Hook script to log events to os-database"""
import sys
import os
import uuid
from datetime import datetime

# Add scripts to path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

def log_event(agent_id, event_type, message, metadata=None):
    """Log an event to the timeline_events table"""
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    event_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat() + "+00:00"

    cursor.execute("""
        INSERT INTO timeline_events (id, agent_id, event_type, message, metadata, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event_id, agent_id, event_type, message, metadata, timestamp))

    conn.commit()
    conn.close()
    print(f"Logged {event_type}: {message}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: log_hook.py <agent_id> <event_type> <message> [metadata]")
        sys.exit(1)

    agent_id = sys.argv[1]
    event_type = sys.argv[2]
    message = sys.argv[3]
    metadata = sys.argv[4] if len(sys.argv) > 4 else None

    log_event(agent_id, event_type, message, metadata)
