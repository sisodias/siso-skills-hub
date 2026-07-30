#!/usr/bin/env python3
"""Initialize agent session - auto-reads config, writes state."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config, load_state, save_state


def init_agent(task_id: str = None):
    config = load_config()
    state = load_state()
    db_path = config.get("db_path")

    agent_id = config.get("agent_id")
    role = config.get("role", "agent")
    department = config.get("department", "general")
    root_path = config.get("root_path", os.getcwd())

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Get or create agent record
    cursor.execute("SELECT run_count FROM agents WHERE id = ?", (agent_id,))
    row = cursor.fetchone()

    if not row:
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
    new_state = {
        "current_session_id": session_id,
        "current_task_id": task_id,
        "run_number": run_number,
        "session_started_at": now
    }
    state.update(new_state)
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
