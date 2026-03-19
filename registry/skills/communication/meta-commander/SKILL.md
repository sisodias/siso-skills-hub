---
name: meta-commander
description: Communicate with META agents in the SISO ecosystem
version: 1.0.0
tags:
  - agent-management
  - meta
---

# Meta Commander Skill

Communicate with META agents in the SISO ecosystem.

## META Workspaces

| Agent | Workspace | Purpose |
|-------|-----------|---------|
| META: Skills | workspace:13 | Manage and improve skills |
| META: Agent Creator | workspace:17 | Create new agents |
| META: Task Iterator | workspace:18 | Task management |
| META: Agent Template | workspace:7 | Agent templates |
| META: Memory | workspace:11 | Memory systems |
| META: Plugins | workspace:16 | Plugin management |
| META: Project Template | workspace:10 | Project templates |
| META: CLAUDE.md | workspace:12 | CLAUDE.md management |
| META: GitHub Storage | workspace:15 | GitHub integration |
| META: Token Team | workspace:14 | Token management |

---

## Send Message to META Agent

### Get workspace info
```bash
cmux list-workspaces
```

### Find the agent workspace
Look for "META: <Name>" in the list.

### Get pane and surface
```bash
cmux list-panes --workspace workspace:X
cmux list-pane-surfaces --workspace workspace:X --pane pane:Y
```

### Send message
```bash
cmux send --workspace workspace:X "Your message here\n"
```

---

## Example: Message META: Skills

```bash
# 1. Find workspace
cmux list-workspaces
# Look for "META: Skills" - say it's workspace:13

# 2. Get pane/surface
cmux list-panes --workspace workspace:13
cmux list-pane-surfaces --workspace workspace:13 --pane pane:30

# 3. Send message
cmux send --workspace workspace:13 "Hello! I need help creating a new skill.\n"
```

---

## Quick Reference: Known META Workspaces

```
META: Skills         → workspace:13
META: Agent Creator → workspace:17
META: Task Iterator → workspace:18
```

---

## Use Cases

- Need new skills created → message META: Skills
- Need new agent → message META: Agent Creator
- Need help with tasks → message META: Task Iterator
