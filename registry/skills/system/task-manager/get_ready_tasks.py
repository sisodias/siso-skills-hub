#!/usr/bin/env python3
"""
get_ready_tasks.py - Lists tasks with all dependencies completed

Usage:
    python scripts/get_ready_tasks.py              # List all ready tasks
    python scripts/get_ready_tasks.py --json       # JSON output
    python scripts/get_ready_tasks.py --project X  # Filter by project
"""

import json
import os
import sys
from pathlib import Path

WORKSPACE = Path(os.environ.get("SISO_WORKSPACE", Path.home() / "SISO_Workspace")).expanduser()
TASKS_DIR = Path(os.environ.get("SISO_TASKS_DIR", WORKSPACE / ".agents" / "tasks")).expanduser()


def load_tasks():
    """Load all tasks from backlog/ and in_progress/ directories."""
    tasks = []

    for dir_name in ["backlog", "in_progress"]:
        dir_path = TASKS_DIR / dir_name
        if not dir_path.exists():
            continue

        for task_dir in dir_path.glob("TASK-*"):
            if not task_dir.is_dir():
                continue
            task_file = task_dir / "task.json"
            if task_file.exists():
                with open(task_file) as f:
                    task = json.load(f)
                    task["_dir"] = dir_name  # Track where it lives
                    tasks.append(task)

    return tasks


def get_task_status(task_id):
    """Get the status of a task by ID."""
    for dir_name in ["backlog", "in_progress", "completed"]:
        task_file = TASKS_DIR / dir_name / task_id / "task.json"
        if task_file.exists():
            with open(task_file) as f:
                return json.load(f).get("status")

    return None


def is_ready(task):
    """Check if task is ready (all dependencies completed)."""
    status = task.get("status")

    # Must be backlog to be ready
    if status != "backlog":
        return False

    # Check all dependencies
    dependencies = task.get("dependencies", [])
    if not dependencies:
        return True

    for dep_id in dependencies:
        dep_status = get_task_status(dep_id)
        if dep_status != "completed":
            return False

    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="List ready-to-work tasks")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--project", help="Filter by target project")
    parser.add_argument("--assigned-to", help="Filter by assignee")
    parser.add_argument("--my-tasks", action="store_true", help="Show tasks assigned to current agent")
    args = parser.parse_args()

    tasks = load_tasks()

    # Filter by assignee
    if args.my_tasks:
        agent_name = os.environ.get("AGENT_NAME", "unknown_agent")
        tasks = [t for t in tasks if t.get("assigned_to") == agent_name]
    elif args.assigned_to:
        tasks = [t for t in tasks if t.get("assigned_to") == args.assigned_to]

    ready_tasks = [t for t in tasks if is_ready(t)]

    # Filter by project if specified
    if args.project:
        ready_tasks = [t for t in ready_tasks if args.project in t.get("target_project", "")]

    # Sort by priority (critical > high > medium > low)
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    ready_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 2))

    if args.json:
        print(json.dumps(ready_tasks, indent=2))
    else:
        if not ready_tasks:
            print("No ready tasks found.")
            return

        print("READY TASKS:\n")
        for task in ready_tasks:
            deps = task.get("dependencies", [])
            dep_info = f" (deps: {', '.join(deps)})" if deps else ""
            print(f"  {task['id']} [{task['priority']}]{dep_info}")
            print(f"    {task['title']}\n")


if __name__ == "__main__":
    main()
