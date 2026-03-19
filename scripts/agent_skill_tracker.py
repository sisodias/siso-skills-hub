#!/usr/bin/env python3
"""
Lightweight wrapper to track agent skill invocations.

Usage:
    python3 agent_skill_tracker.py <skill_id> <success> [duration_ms] [agent_id]

Examples:
    python3 agent_skill_tracker.py websearch true 150 agent-123
    python3 agent_skill_tracker.py os-database true 42
    python3 agent_skill_tracker.py gitsearch false 0

Environment variables:
    AGENT_ID: Used as agent_id if not provided as arg

This script is meant to be called before/around skill invocations:
    python3 scripts/agent_skill_tracker.py websearch true 0 && \
        python3 ${CLAUDE_SKILL_DIR}/scripts/perplexity_search.py "$ARGUMENTS"
"""
import sys
import os

# Add skills_hub/scripts to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills_telemetry import track


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: agent_skill_tracker.py <skill_id> <success> [duration_ms] [agent_id]")
        print("  success: 'true' or 'false'")
        print("  duration_ms: optional, integer")
        print("  agent_id: optional, defaults to AGENT_ID env var or 'unknown'")
        sys.exit(1)

    skill_id = sys.argv[1]
    success = sys.argv[2].lower() == 'true'
    duration_ms = int(sys.argv[3]) if len(sys.argv) > 3 else None
    agent_id = sys.argv[4] if len(sys.argv) > 4 else os.environ.get('AGENT_ID', 'unknown')

    track(
        skill_id,
        success=success,
        agent_id=agent_id,
        duration_ms=duration_ms,
        context="agent_invocation"
    )

    print(f"Tracked: {skill_id} success={success} agent={agent_id}")
