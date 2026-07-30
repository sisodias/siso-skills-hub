#!/usr/bin/env python3
"""Deprecated PM convenience alias for SISO Agent Brain commands."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys


def run(arguments: list[str]) -> int:
    command = shlex.split(os.environ.get("SISO_BRAIN_CLI", "siso-brain"))
    try:
        return subprocess.run(command + arguments, text=True).returncode
    except FileNotFoundError:
        print("siso-brain is not installed; set SISO_BRAIN_CLI to its executable", file=sys.stderr)
        return 127


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Deprecated PM alias for Agent Brain")
    sub = root.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    sub.add_parser("mine")
    create = sub.add_parser("create"); create.add_argument("title"); create.add_argument("--desc", default=""); create.add_argument("--priority", type=int, default=5)
    update = sub.add_parser("update"); update.add_argument("id"); update.add_argument("status")
    add = sub.add_parser("add-step"); add.add_argument("task_id"); add.add_argument("step_name"); add.add_argument("role"); add.add_argument("--order", type=int, default=1)
    get = sub.add_parser("get"); get.add_argument("id")
    return root


def main() -> None:
    args = parser().parse_args()
    if args.command == "list":
        command = ["tasks", "--all"]
    elif args.command == "mine":
        command = ["tasks", "--agent", "PM_Agent"]
    elif args.command == "create":
        command = ["task-create", "--title", args.title, "--description", args.desc or args.title,
                   "--project", "agent-os", "--agent", "PM_Agent", "--created-by", "PM_Agent",
                   "--priority", str(args.priority), "--urgency", str(max(0, min(100, args.priority * 10)))]
    elif args.command == "update":
        command = ["task-update", "--id", args.id, "--status", args.status]
    elif args.command == "add-step":
        command = ["step-add", "--task", args.task_id, "--name", args.step_name,
                   "--role", args.role, "--order", str(args.order)]
    elif args.command == "get":
        command = ["tasks", "--id", args.id]
    else:
        raise AssertionError(args.command)
    raise SystemExit(run(command))


if __name__ == "__main__":
    main()
