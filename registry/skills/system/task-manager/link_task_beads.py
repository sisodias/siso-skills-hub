#!/usr/bin/env python3
"""
Link beads to a task.

Usage:
    python link_task_beads.py TASK-0003 agency_app-1 agency_app-2
"""

import json
import sys
import os
from pathlib import Path

def main():
    if len(sys.argv) < 3:
        print("Usage: python link_task_beads.py <task_id> <bead_id> [<bead_id> ...]")
        sys.exit(1)

    task_id = sys.argv[1]
    bead_ids = sys.argv[2:]

    # Find task in backlog or completed
    task_path = Path(f"/Users/shaansisodia/SISO_Workspace/Agent_OS/.tasks/backlog/{task_id}/task.json")
    if not task_path.exists():
        task_path = Path(f"/Users/shaansisodia/SISO_Workspace/Agent_OS/.tasks/completed/{task_id}/task.json")

    if not task_path.exists():
        print(f"Error: Task {task_id} not found")
        sys.exit(1)

    with open(task_path) as f:
        task = json.load(f)

    # Add beads
    if "beads" not in task:
        task["beads"] = []

    for bead_id in bead_ids:
        if bead_id not in task["beads"]:
            task["beads"].append(bead_id)

    # Add execution log
    task.setdefault("execution_log", []).append({
        "timestamp": "2026-03-11T18:00:00Z",
        "action": f"Linked beads: {bead_ids}",
        "by": "link_task_beads.py"
    })

    with open(task_path, "w") as f:
        json.dump(task, f, indent=2)

    print(f"Linked {len(bead_ids)} beads to {task_id}")
    print(f"Beads: {task.get('beads', [])}")

if __name__ == "__main__":
    main()
