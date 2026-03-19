---
name: agent-setup
description: Create a new agent from the V4 template with memory system pre-configured
version: 1.0.0
tags:
  - agent-management
  - setup
  - template
---

# Agent Setup Skill

Create a new agent from the V4 template with memory system pre-configured.

## What It Does

1. Copies the latest V4 agent template
2. Sets up claude-mem-lite memory system
3. Configures hooks.json with absolute paths
4. Creates .mcp.json for MCP server
5. Initializes the memory database

## Usage

```bash
/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/registry/skills/agent-setup/scripts/setup.sh <agent_dir> <agent_name>

# Example: Create Developer_Agent
/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/registry/skills/agent-setup/scripts/setup.sh \
    "/Users/shaansisodia/SISO_Workspace/agent_os/agents/Developer_Agent" \
    Developer_Agent
```

## Output

Creates agent with:
```
<agent_dir>/
├── .claude/
│   ├── claude-mem-lite/   # Memory system
│   ├── hooks/hooks.json   # Hook config
│   └── memory/            # Memory DB
├── .mcp.json             # MCP config
├── identity.yaml          # Edit this!
├── inbox/                # Task inbox
├── outbox/               # Task outbox
└── workspace/            # Working directory
```

## After Setup

1. Edit `identity.yaml` with agent details
2. Start Claude Code in the agent folder
3. Run `/mcp` to verify mem shows ✅ connected
