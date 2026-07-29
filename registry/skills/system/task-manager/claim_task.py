#!/usr/bin/env python3
"""
claim_task.py - Atomically claim a task for an agent

Usage:
    python scripts/claim_task.py TASK-0001              # Claim for current agent
    python scripts/claim_task.py TASK-0001 --force      # Force claim (override)
    python scripts/claim_task.py TASK-0001 --unclaim    # Release claim

Uses file locking to prevent race conditions.
"""

import json
import os
import sys
import fcntl
import time
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(os.environ.get("SISO_WORKSPACE", Path.home() / "SISO_Workspace")).expanduser()
TASKS_DIR = Path(os.environ.get("SISO_TASKS_DIR", WORKSPACE / ".agents" / "tasks")).expanduser()
LOCK_DIR = TASKS_DIR / ".locks"


def get_agent_name():
    """Get current agent name from environment or default."""
    return os.environ.get("AGENT_NAME", "unknown_agent")


def acquire_lock(task_id, timeout=10):
    """Acquire exclusive lock for a task."""
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    lock_file = LOCK_DIR / f"{task_id}.lock"

    lock_fp = open(lock_file, 'w')
    start_time = time.time()

    while time.time() - start_time < timeout:
        try:
            fcntl.flock(lock_fp.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return lock_fp
        except BlockingIOError:
            time.sleep(0.1)

    lock_fp.close()
    raise TimeoutError(f"Could not acquire lock for {task_id} within {timeout}s")


def release_lock(lock_fp, task_id):
    """Release the lock."""
    try:
        fcntl.flock(lock_fp.fileno(), fcntl.LOCK_UN)
        lock_fp.close()
        (LOCK_DIR / f"{task_id}.lock").unlink(missing_ok=True)
    except Exception:
        pass


def load_task(task_id):
    """Load task from backlog/in_progress/completed."""
    for dir_name in ["backlog", "in_progress", "completed"]:
        task_file = TASKS_DIR / dir_name / task_id / "task.json"
        if task_file.exists():
            with open(task_file) as f:
                return json.load(f), dir_name
    return None, None


def save_task(task, dir_name):
    """Save task to directory."""
    task_id = task["id"]
    task_file = TASKS_DIR / dir_name / task_id / "task.json"
    with open(task_file, 'w') as f:
        json.dump(task, f, indent=2)


def claim_task(task_id, agent_name, force=False):
    """Atomically claim a task."""
    task, dir_name = load_task(task_id)

    if not task:
        print(f"Error: Task {task_id} not found")
        return False

    if dir_name == "completed":
        print(f"Error: Cannot claim completed task {task_id}")
        return False

    # Check if already claimed
    current_assignee = task.get("assigned_to")
    if current_assignee and current_assignee != agent_name and not force:
        print(f"Error: Task {task_id} already claimed by {current_assignee}")
        return False

    if force:
        print(f"Force claiming {task_id} (was claimed by {current_assignee})")

    # Update task
    task["assigned_to"] = agent_name
    task["status"] = "in_progress"

    # Add to execution log
    if "execution_log" not in task:
        task["execution_log"] = []

    task["execution_log"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "action": "claimed",
        "notes": f"{'force ' if force else ''}claimed task"
    })

    # Move to in_progress if currently in backlog
    if dir_name == "backlog":
        import shutil
        src = TASKS_DIR / "backlog" / task_id
        dst = TASKS_DIR / "in_progress" / task_id
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            shutil.move(str(f), str(dst / f.name))
        src.rmdir()
        dir_name = "in_progress"

    save_task(task, dir_name)
    print(f"✓ Claimed {task_id} for {agent_name}")
    return True


def unclaim_task(task_id, agent_name):
    """Release claim on a task."""
    task, dir_name = load_task(task_id)

    if not task:
        print(f"Error: Task {task_id} not found")
        return False

    if task.get("assigned_to") != agent_name:
        print(f"Error: Task {task_id} not claimed by {agent_name}")
        return False

    # Move back to backlog
    if dir_name == "in_progress":
        import shutil
        src = TASKS_DIR / "in_progress" / task_id
        dst = TASKS_DIR / "backlog" / task_id
        dst.mkdir(parents=True, exist_ok=True)
        for f in src.iterdir():
            shutil.move(str(f), str(dst / f.name))
        src.rmdir()
        dir_name = "backlog"

    task["assigned_to"] = None
    task["status"] = "backlog"

    # Add to execution log
    if "execution_log" not in task:
        task["execution_log"] = []

    task["execution_log"].append({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "agent": agent_name,
        "action": "unclaimed",
        "notes": "released claim"
    })

    save_task(task, dir_name)
    print(f"✓ Released claim on {task_id}")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Atomically claim a task")
    parser.add_argument("task_id", help="Task ID (e.g., TASK-0001)")
    parser.add_argument("--force", action="store_true", help="Force claim (override current assignee)")
    parser.add_argument("--unclaim", action="store_true", help="Release claim instead")
    parser.add_argument("--agent", default=None, help="Agent name (default: from AGENT_NAME env)")
    args = parser.parse_args()

    agent_name = args.agent or get_agent_name()

    try:
        lock_fp = acquire_lock(args.task_id)
        try:
            if args.unclaim:
                success = unclaim_task(args.task_id, agent_name)
            else:
                success = claim_task(args.task_id, agent_name, args.force)
            sys.exit(0 if success else 1)
        finally:
            release_lock(lock_fp, args.task_id)
    except TimeoutError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
