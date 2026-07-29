---
name: cli-runner
description: Run SISO CLI commands and interact with agents
version: 1.0.0
tags:
  - cli
  - siso
---

# CLI Runner Skill

Run SISO CLI commands and interact with agents.

## Available CLI Commands

### siso-mini
Fast CLI with MiniMax model.
```bash
siso-mini
# Opens interactive Claude Code session
```

### siso-claude
Claude-powered CLI.
```bash
siso-claude
```

### siso-glm / siso-glm5
GLM-powered CLIs.
```bash
siso-glm
siso-glm5
```

### siso-kimi (1-9)
Kimiverse-powered CLIs.
```bash
siso-kimi
siso-kimi2
# ... up to siso-kimi9
```

## Run Agent

### Via run.sh
Each agent has a run.sh script:
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/agents/<AgentName>
./run.sh
```

### Interactive Session
```bash
# Open PM Agent
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/agents/PM_Agent
./run.sh
```

## Workflow: Create Agent and Interact

### 1. Create Agent
Use agent-builder skill to create new agent.

### 2. Run Agent
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/agents/<AgentName>
./run.sh
```

### 3. Send Message
Once agent is running, you can send messages via the terminal.

## Example: Create and Run Developer Agent

```bash
# 1. Create the agent (see agent-builder skill)
agent-builder create Developer_Agent

# 2. Run it
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/agents/Developer_Agent
./run.sh

# 3. The agent is now running and ready to receive tasks
```

## Key Paths

- **CLI Bin:** `${HOME}/.claude/bin/`
- **Agents:** `${SISO_WORKSPACE}/SISO_Internal_Lab/agents/`
- **Template:** `${SISO_WORKSPACE}/Agent_OS/workspace/__template_agent__/`
