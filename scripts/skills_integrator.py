#!/usr/bin/env python3
"""
Skills Integrator - Reads placements from backlog/placements/ and installs skills to agents.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

HUB_ROOT = Path(__file__).parent.parent
PLACEMENTS_DIR = HUB_ROOT / "backlog" / "placements"
SKILLS_CLI = Path(__file__).parent / "skills"


def load_placements() -> list[dict]:
    """Load all placement JSON files from backlog/placements/."""
    placements = []

    if not PLACEMENTS_DIR.exists():
        PLACEMENTS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Created placements directory: {PLACEMENTS_DIR}")
        return placements

    for file in PLACEMENTS_DIR.glob("*.json"):
        try:
            with open(file) as f:
                data = json.load(f)
                if isinstance(data, list):
                    placements.extend(data)
                else:
                    placements.append(data)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in {file}: {e}")
        except Exception as e:
            print(f"Warning: Error reading {file}: {e}")

    return placements


def install_skill_to_agent(skill_id: str, agent_name: str, dry_run: bool = False) -> bool:
    """Install a skill to an agent via the skills CLI."""
    cmd = [
        "python3",
        str(SKILLS_CLI),
        "install",
        skill_id,
        "--agent",
        agent_name
    ]

    if dry_run:
        print(f"[DRY-RUN] Would execute: {' '.join(cmd)}")
        return True

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=HUB_ROOT
        )
        if result.returncode == 0:
            print(f"✓ Installed {skill_id} -> {agent_name}")
            return True
        else:
            print(f"✗ Failed to install {skill_id} -> {agent_name}")
            print(f"  Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ Timeout installing {skill_id} -> {agent_name}")
        return False
    except Exception as e:
        print(f"✗ Error installing {skill_id} -> {agent_name}: {e}")
        return False


def process_placements(dry_run: bool = False) -> dict:
    """Process all placements and install skills to agents."""
    placements = load_placements()

    if not placements:
        print("No placements found.")
        return {"success": True, "installed": 0, "failed": 0}

    print(f"Found {len(placements)} placement(s) to process\n")

    results = {
        "success": True,
        "installed": 0,
        "failed": 0,
        "details": []
    }

    for placement in placements:
        skill_id = placement.get("skill_id") or placement.get("skill")
        agent = placement.get("agent") or placement.get("target_agent")

        if not skill_id:
            print(f"Warning: Placement missing skill_id: {placement}")
            results["failed"] += 1
            results["details"].append({
                "placement": placement,
                "status": "skipped",
                "reason": "missing skill_id"
            })
            continue

        if not agent:
            print(f"Warning: Placement missing agent: {placement}")
            results["failed"] += 1
            results["details"].append({
                "placement": placement,
                "status": "skipped",
                "reason": "missing agent"
            })
            continue

        success = install_skill_to_agent(skill_id, agent, dry_run)

        if success:
            results["installed"] += 1
            results["details"].append({
                "skill_id": skill_id,
                "agent": agent,
                "status": "installed"
            })
        else:
            results["failed"] += 1
            results["success"] = False
            results["details"].append({
                "skill_id": skill_id,
                "agent": agent,
                "status": "failed"
            })

    return results


def list_placements():
    """List all pending placements."""
    placements = load_placements()

    if not placements:
        print("No placements found.")
        return

    print(f"{'SKILL ID':<25} {'AGENT':<30} {'STATUS'}")
    print("-" * 60)

    for p in placements:
        skill_id = p.get("skill_id") or p.get("skill", "N/A")
        agent = p.get("agent") or p.get("target_agent", "N/A")
        status = p.get("status", "pending")
        print(f"{skill_id:<25} {agent:<30} {status}")


def main():
    parser = argparse.ArgumentParser(prog="skills_integrator")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be installed without actually installing")
    parser.add_argument("--list", action="store_true",
                        help="List pending placements")
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    if args.list:
        list_placements()
        return 0

    results = process_placements(dry_run=args.dry_run)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*50}")
        print(f"Results: {results['installed']} installed, {results['failed']} failed")
        if args.dry_run:
            print("(dry-run mode - no actual changes made)")

    return 0 if results["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
