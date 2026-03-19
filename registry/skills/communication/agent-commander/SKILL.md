---
name: agent-commander
description: Create workspaces, start agents, and communicate with them via CMUX
version: 1.0.0
tags:
  - agent-management
  - cmux
---

# Agent Commander Skill

Create workspaces, start agents, and communicate with them via CMUX.

## Overview

CMUX allows you to:
1. Create new workspaces
2. Start agents in those workspaces
3. Send messages to agents
4. Manage multiple agents in parallel

## Location

```
CMUX: /Applications/cmux.app/Contents/Resources/bin/cmux
```

---

## List Current Workspaces

```bash
cmux list-workspaces
```

Example output:
```
* workspace:6  INTERNAL: PM
  workspace:3  OS: PM
  workspace:24  INTERNAL: Testing Agent
  workspace:18  META: Task Iterator
```

---

## Create New Agent Workspace

### Step 1: Create workspace
```bash
cmux new-workspace
```

### Step 2: Get workspace ID
```bash
cmux list-workspaces
```

### Step 3: Rename workspace
```bash
cmux rename-workspace --workspace workspace:X "INTERNAL: AgentName"
```

### Step 4: Navigate to agent folder
```bash
cmux send --workspace workspace:X "cd /path/to/agent\n"
```

### Step 5: Start agent (SEPARATE COMMAND!)
```bash
cmux send --workspace workspace:X "siso-mini\n"
```

**⚠️ IMPORTANT: Always send cd and siso-mini as SEPARATE commands!**

---

## Send Message to Agent

### Get workspace info
```bash
cmux list-panes --workspace workspace:X
cmux list-pane-surfaces --workspace workspace:X --pane pane:Y
```

### Send message
```bash
cmux send --workspace workspace:X "Your message here\n"
```

---

## Example: Start Testing Agent

```bash
# 1. Create workspace
cmux new-workspace

# 2. List to get ID (say it's workspace:24)
cmux list-workspaces

# 3. Rename
cmux rename-workspace --workspace workspace:24 "INTERNAL: Testing Agent"

# 4. Navigate to agent (SEPARATE command!)
cmux send --workspace workspace:24 "cd /Users/shaansisodia/SISO_Workspace/SISO_Internal_Lab/agents/Testing_Agent\n"

# 5. Start agent (SEPARATE command!)
cmux send --workspace workspace:24 "siso-mini\n"

# 6. Wait for agent to start, then send message
cmux send --workspace workspace:24 "Hello! Can you hear me?\n"
```

---

## Example: Start Developer Agent

```bash
cmux new-workspace
# (get ID from list-workspaces, say workspace:25)
cmux rename-workspace --workspace workspace:25 "INTERNAL: Dev"
cmux send --workspace workspace:25 "cd /Users/shaansisodia/SISO_Workspace/SISO_Internal_Lab/agents/Developer_Agent\n"
cmux send --workspace workspace:25 "siso-mini\n"
```

---

## Workspace Naming Convention

```
INTERNAL: <name>    - Internal project agents (Testing, Dev, Code Review)
OS: <name>          - OS-level tasks
META: <name>        - Meta/management tasks
```

---

## Available Agents

| Agent | Path |
|-------|------|
| PM_Agent | `/Users/shaansisodia/SISO_Workspace/SISO_Internal_Lab/agents/PM_Agent` |
| Testing_Agent | `/Users/shaansisodia/SISO_Workspace/SISO_Internal_Lab/agents/Testing_Agent` |

To add more agents: use agent-builder skill

---

## Common Issues

### Issue: Commands not working
**Fix:** Always send `cd` first, then `siso-mini` as SEPARATE commands

### Issue: Wrong workspace
**Fix:** Check `cmux list-workspaces` to get correct workspace ID

### Issue: Agent not responding
**Fix:** Make sure agent folder path is correct, check workspace surface shows "Claude Code"

---

## Workflow Summary

```
1. Create workspace:     cmux new-workspace
2. Get ID:             cmux list-workspaces
3. Rename:             cmux rename-workspace --workspace workspace:X "INTERNAL: Name"
4. Navigate:           cmux send --workspace workspace:X "cd /path/to/agent\n"
5. Start agent:        cmux send --workspace workspace:X "siso-mini\n"
6. Send message:       cmux send --workspace workspace:X "message\n"
```
