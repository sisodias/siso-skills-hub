#!/usr/bin/env python3
"""Update task status - auto-reads config for db_path."""
import sqlite3
import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def run_automations_for_task(event: str, task_id: str, old_status: str = None, new_status: str = None):
    """Run automations for task events."""
    config = load_config()
    db_path = config.get("db_path")

    # Build data payload
    data = {"task_id": task_id}
    if old_status:
        data["old_status"] = old_status
    if new_status:
        data["new_status"] = new_status

    # Import and run automations
    run_automation_script = os.path.join(SCRIPT_DIR, "scripts", "run_automations.py")
    import subprocess
    subprocess.run(["python3", run_automation_script, "--event", event, "--data", json.dumps(data)],
                  capture_output=True, text=True)


def update_task(task_id: str, status: str = None, executive_summary: str = None,
                blocked_by: str = None, assigned_agent: str = None, estimated_minutes: int = None):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    # Get old status before update
    old_status = None
    if status:
        cursor.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            old_status = row[0]

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
        if status == "completed":
            updates.append("completed_at = ?")
            params.append(now)

    if executive_summary:
        updates.append("executive_summary = ?")
        params.append(executive_summary)

    if blocked_by:
        updates.append("blocked_by_task_id = ?")
        params.append(blocked_by)

    if assigned_agent:
        updates.append("assigned_agent_id = ?")
        params.append(assigned_agent)

    if estimated_minutes is not None:
        updates.append("estimated_minutes = ?")
        params.append(estimated_minutes)

    updates.append("updated_at = ?")
    params.append(now)
    params.append(task_id)

    cursor.execute(f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?", params)
    conn.commit()
    conn.close()

    # Run automations for status change
    if status and status != old_status:
        run_automations_for_task("task.status_changed", task_id, old_status, status)

    print(json.dumps({"status": "success", "task_id": task_id, "updated": {"status": status, "summary": executive_summary}}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--status", choices=["pending", "in_progress", "blocked", "review", "completed", "failed"])
    parser.add_argument("--summary", help="Executive summary")
    parser.add_argument("--blocked-by", help="Task ID this is blocked by")
    parser.add_argument("--assign", help="Agent ID to assign")
    parser.add_argument("--estimate", type=int, help="Estimated time in minutes")
    args = parser.parse_args()

    update_task(args.task_id, args.status, args.summary, args.blocked_by, args.assign, args.estimate)
