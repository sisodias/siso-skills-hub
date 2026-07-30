#!/usr/bin/env python3
"""Compatibility adapter from legacy siso-tasks commands to SISO Agent Brain.

The adapter owns no database. Configure the service through the normal
SISO_BRAIN_* environment variables and install `siso-brain`, or set
SISO_BRAIN_CLI to an explicit command for tests/packaged environments.
"""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys


def brain_command() -> list[str]:
    return shlex.split(os.environ.get("SISO_BRAIN_CLI", "siso-brain"))


def run_brain(arguments: list[str]) -> int:
    try:
        result = subprocess.run(brain_command() + arguments, text=True)
    except FileNotFoundError:
        print("siso-brain is not installed; set SISO_BRAIN_CLI to its executable", file=sys.stderr)
        return 127
    return result.returncode


def priority_urgency(value: int) -> int:
    return max(0, min(100, value * 10))


def event_type(value: str) -> str:
    return {
        "thought": "THOUGHT", "action": "ACTION", "execute": "ACTION",
        "tool_call": "TOOL_CALL", "error": "ERROR", "handoff": "HANDOFF",
        "completed": "COMPLETED", "boot": "BOOT", "user_prompt": "USER_PROMPT",
    }.get(value.lower(), "ACTION")


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="SISO Tasks compatibility adapter for Agent Brain")
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="Check Agent Brain health; no database is created by this adapter")

    create = sub.add_parser("create-task")
    create.add_argument("--id", required=True); create.add_argument("--project-id", required=True)
    create.add_argument("--pipeline-type", required=True); create.add_argument("--title")
    create.add_argument("--category"); create.add_argument("--created-by"); create.add_argument("--assigned-to")
    create.add_argument("--description", required=True); create.add_argument("--metadata")
    create.add_argument("--priority", type=int, default=1)

    add = sub.add_parser("add-step")
    add.add_argument("--id", required=True); add.add_argument("--task-id", required=True)
    add.add_argument("--step-name", required=True); add.add_argument("--role", required=True)
    add.add_argument("--order", type=int, required=True); add.add_argument("--input-payload")

    pull = sub.add_parser("pull"); pull.add_argument("--role", required=True); pull.add_argument("--claimed-by")
    inbox = sub.add_parser("view-inbox"); inbox.add_argument("--role", required=True)

    update = sub.add_parser("update-step")
    update.add_argument("--id", required=True); update.add_argument("--status", required=True,
        choices=("done", "retry", "error", "in_progress", "pending", "cancelled"))
    update.add_argument("--output-payload"); update.add_argument("--error-log")

    artifact = sub.add_parser("update-artifact")
    artifact.add_argument("--task-id", required=True); artifact.add_argument("--step-id")
    artifact.add_argument("--type", required=True); artifact.add_argument("--content", required=True)
    latest = sub.add_parser("get-artifact")
    latest.add_argument("--task-id", required=True); latest.add_argument("--type", required=True)

    log = sub.add_parser("log-execution")
    log.add_argument("--step-id"); log.add_argument("--session-id"); log.add_argument("--task-id")
    log.add_argument("--action-type", required=True); log.add_argument("--details", required=True)
    log.add_argument("--agent", default=os.environ.get("SISO_AGENT_ID", "task-manager-adapter"))

    memory = sub.add_parser("add-memory")
    memory.add_argument("--task-id"); memory.add_argument("--session-id"); memory.add_argument("--type", required=True)
    memory.add_argument("--content", required=True); memory.add_argument("--agent", default=os.environ.get("SISO_AGENT_ID"))

    query = sub.add_parser("query", help="Retired: use stable Agent Brain commands instead of raw SQL")
    query.add_argument("--sql", required=True)
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "query":
        print("raw SQL is retired; use siso-brain tasks, steps, memory-recall, or artifact-latest", file=sys.stderr)
        raise SystemExit(2)

    command: list[str]
    if args.command == "init":
        command = ["health"]
    elif args.command == "create-task":
        command = ["task-create", "--id", args.id, "--description", args.description,
                   "--project", args.project_id, "--priority", str(args.priority),
                   "--urgency", str(priority_urgency(args.priority))]
        if args.title: command += ["--title", args.title]
        if args.assigned_to: command += ["--agent", args.assigned_to]
        if args.created_by: command += ["--created-by", args.created_by]
    elif args.command == "add-step":
        command = ["step-add", "--id", args.id, "--task", args.task_id, "--name", args.step_name,
                   "--role", args.role, "--order", str(args.order)]
        if args.input_payload: command += ["--input", args.input_payload]
    elif args.command == "pull":
        command = ["step-claim", "--role", args.role]
        if args.claimed_by: command += ["--by", args.claimed_by]
    elif args.command == "view-inbox":
        command = ["steps", "--role", args.role]
    elif args.command == "update-step":
        command = ["step-update", "--id", args.id, "--status", args.status]
        if args.output_payload: command += ["--output", args.output_payload]
        if args.error_log: command += ["--error", args.error_log]
    elif args.command == "update-artifact":
        command = ["artifact-write", "--task", args.task_id, "--type", args.type, "--content", args.content]
        if args.step_id: command += ["--step", args.step_id]
    elif args.command == "get-artifact":
        command = ["artifact-latest", "--task", args.task_id, "--type", args.type]
    elif args.command == "log-execution":
        command = ["timeline", "--agent", args.agent, "--type", event_type(args.action_type), "--message", args.details]
        if args.task_id: command += ["--task", args.task_id]
    elif args.command == "add-memory":
        command = ["memory-write", "--content", args.content, "--type", args.type]
        if args.task_id: command += ["--task", args.task_id]
        if args.agent: command += ["--agent", args.agent]
    else:
        raise AssertionError(args.command)
    raise SystemExit(run_brain(command))


if __name__ == "__main__":
    main()
