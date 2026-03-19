#!/usr/bin/env python3
"""Initialize agent session - auto-reads config, writes state."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
STATE_PATH = os.path.join(SCRIPT_DIR, "state.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, 'w') as f:
        json.dump(state, f, indent=2)


def init_agent(task_id: str = None):
    config = load_config()

    agent_id = config.get("agent_id")
    role = config.get("role", "")
    department = config.get("department", "")
    root_path = config.get("root_path", "")
    db_path = config.get("db_path")

    if not agent_id:
        print(json.dumps({"status": "error", "message": "agent_id not set in config.json"}))
        return

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Register/update agent
    cursor.execute("SELECT run_count FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()

    if row is None:
        cursor.execute("""
            INSERT INTO agents (id, role, department, root_path, status, run_count)
            VALUES (?, ?, ?, ?, 'working', 1)
        """, (agent_id, role, department, root_path))
        run_number = 1
    else:
        run_number = row[0] + 1
        cursor.execute("UPDATE agents SET status = 'working', run_count = ?, updated_at = ? WHERE id = ?",
                       (run_number, now, agent_id))

    # Create session
    session_id = f"SESS-{agent_id}-{run_number}"
    cursor.execute("""
        INSERT INTO sessions (id, agent_id, task_id, run_number, status, start_time)
        VALUES (?, ?, ?, ?, 'running', ?)
    """, (session_id, agent_id, task_id, run_number, now))

    # Update task if provided
    if task_id:
        cursor.execute("UPDATE tasks SET status = 'in_progress', assigned_agent_id = ?, started_at = ? WHERE id = ?",
                       (agent_id, now, task_id))

    conn.commit()

    # Save state
    state = {
        "current_session_id": session_id,
        "current_task_id": task_id,
        "run_number": run_number,
        "session_started_at": now
    }
    save_state(state)

    conn.close()

    print(json.dumps({
        "status": "success",
        "agent_id": agent_id,
        "session_id": session_id,
        "run_number": run_number,
        "task_id": task_id
    }))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id")
    args = parser.parse_args()
    init_agent(args.task_id)
