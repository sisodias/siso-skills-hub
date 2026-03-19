#!/usr/bin/env python3
"""Show recent timeline events"""
import sqlite3
import os
import sys
from datetime import datetime, timedelta

DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

def get_recent_events(period='1 hour', agent_id=None, limit=20):
    """Get recent events from timeline_events"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Parse period
    if period.endswith('m'):
        interval = f"-{period[:-1]} minutes"
    elif period.endswith('h'):
        interval = f"-{period[:-1]} hours"
    elif period.endswith('d'):
        interval = f"-{period[:-1]} days"
    else:
        interval = "-1 hour"  # default

    query = """
        SELECT agent_id, event_type, message, timestamp
        FROM timeline_events
        WHERE timestamp >= datetime('now', ?)
    """
    params = [interval]

    if agent_id:
        query += " AND agent_id = ?"
        params.append(agent_id)

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return rows

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Show recent timeline events')
    parser.add_argument('--period', '-p', default='1 hour',
                        help='Time period (e.g., 5m, 2h, 24h, 7d)')
    parser.add_argument('--agent', '-a', default=None,
                        help='Filter by agent_id')
    parser.add_argument('--limit', '-l', type=int, default=20,
                        help='Number of events to show')

    args = parser.parse_args()

    events = get_recent_events(args.period, args.agent, args.limit)

    if not events:
        print(f"No events in the last {args.period}")
        sys.exit(0)

    print(f"=== Last {args.period} ===\n")
    for row in events:
        print(f"[{row['timestamp']}] {row['agent_id']}")
        print(f"  {row['event_type']}: {row['message']}")
        print()
