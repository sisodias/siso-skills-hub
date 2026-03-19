#!/usr/bin/env python3
"""
Check task progress by polling linked beads.

Usage:
    python check_task_progress.py TASK-0003
"""

import json
import sys
import subprocess
from pathlib import Path

def get_bead_status(bead_id, project_path):
    """Get status of a single bead."""
    try:
        result = subprocess.run(
            ["bd", "show", bead_id, "--json"],
            cwd=project_path,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("status", "unknown")
    except Exception as e:
        return f"error: {e}"
    return "not_found"

def main():
    if len(sys.argv) < 2:
        print("Usage: python check_task_progress.py <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]

    # Find task
    task_path = Path(f"/Users/shaansisodia/SISO_Workspace/Agent_OS/.tasks/backlog/{task_id}/task.json")
    if not task_path.exists():
        task_path = Path(f"/Users/shaansisodia/SISO_Workspace/Agent_OS/.tasks/completed/{task_id}/task.json")

    if not task_path.exists():
        print(f"Error: Task {task_id} not found")
        sys.exit(1)

    with open(task_path) as f:
        task = json.load(f)

    beads = task.get("beads", [])
    if not beads:
        print(f"No beads linked to {task_id}")
        sys.exit(0)

    bead_project = task.get("bead_project", "")
    if not bead_project:
        print("Error: No bead_project specified")
        sys.exit(1)

    project_path = f"/Users/shaansisodia/SISO_Workspace/{bead_project}"

    print(f"Checking {len(beads)} beads for {task_id}:")
    print("-" * 40)

    all_done = True
    for bead_id in beads:
        status = get_bead_status(bead_id, project_path)
        print(f"  {bead_id}: {status}")
        if status != "done":
            all_done = False

    print("-" * 40)
    if all_done:
        print(f"✓ All beads done - task can be completed")
    else:
        print(f"✗ Still in progress")

    return 0 if all_done else 1

if __name__ == "__main__":
    sys.exit(main())
