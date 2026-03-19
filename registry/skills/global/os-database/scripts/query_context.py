#!/usr/bin/env python3
"""Query task context - auto-reads config for db_path."""
import sqlite3
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    with open(CONFIG_PATH) as f:
        return json.load(f)


def get_context(task_id: str = None):
    config = load_config()
    db_path = config.get("db_path")

    # If no task_id provided, try to get from state
    if not task_id:
        STATE_PATH = os.path.join(os.path.dirname(CONFIG_PATH), "state.json")
        if os.path.exists(STATE_PATH):
            with open(STATE_PATH) as f:
                state = json.load(f)
                task_id = state.get("current_task_id")

    if not task_id:
        print(json.dumps({"status": "error", "message": "No task_id provided and none in state.json"}))
        return

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "error", "message": f"Task {task_id} not found"}))
        return

    task = dict(row)

    goal = None
    if task.get('goal_id'):
        cursor.execute("SELECT * FROM goals WHERE id = ?", (task['goal_id'],))
        row = cursor.fetchone()
        goal = dict(row) if row else None

    mission = None
    if goal and goal.get('mission_id'):
        cursor.execute("SELECT * FROM missions WHERE id = ?", (goal['mission_id'],))
        row = cursor.fetchone()
        mission = dict(row) if row else None

    project = None
    if mission and mission.get('project_id'):
        cursor.execute("SELECT * FROM projects WHERE id = ?", (mission['project_id'],))
        row = cursor.fetchone()
        project = dict(row) if row else None

    blocker = None
    if task.get('blocked_by_task_id'):
        cursor.execute("SELECT id, title, status FROM tasks WHERE id = ?", (task['blocked_by_task_id'],))
        row = cursor.fetchone()
        blocker = dict(row) if row else None

    conn.close()

    print(json.dumps({
        "status": "success",
        "task": task,
        "goal": goal,
        "mission": mission,
        "project": project,
        "blocker": blocker
    }, indent=2))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id")
    args = parser.parse_args()
    get_context(args.task_id)
