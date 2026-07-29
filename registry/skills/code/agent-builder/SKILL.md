---
name: agent-builder
description: Create new agents from the SISO v3 agent template
version: 1.0.0
tags:
  - agent-management
  - template
  - creation
---

# Agent Builder Skill

Create new agents from the SISO v3 agent template.

## Template Location

```
${SISO_WORKSPACE}/agent_os/module_templates/agents/live/v3/
```

## Agent Structure

```
<agent-name>/
├── .a0proj/
│   ├── project.json       # Agent config
│   └── goals/            # Agent goals
├── config/
│   └── identity.md        # Built from AGENTS.md + SOUL.md
├── inbox/                # Task inbox
├── memory/               # Agent memory
│   ├── README.md
│   └── sessions/.gitignore
├── skills/
│   └── registry.md       # Agent-specific skills
├── AGENTS.md            # What the agent does
├── SOUL.md              # How the agent thinks
├── CLAUDE.md            # Claude context
├── STYLE.md             # Communication style
├── TOOLS.md             # Available tools
└── USER.md              # System-level user preferences
```

## Create New Agent

### 1. Copy Template
```bash
cp -r ${SISO_WORKSPACE}/agent_os/module_templates/agents/live/v3/ \
      ${SISO_WORKSPACE}/agent_os/agents/<AgentName>
```

### 2. Update Files
Customize these core files:
- `AGENTS.md` — Role definition
- `SOUL.md` — Persona/core truths
- `CLAUDE.md` — Runtime behavior
- `config/identity.md` — Agent identity

### 3. Add Skills (optional)
Create `skills/registry.md` with agent-specific skills.

## Agents Location

All meta agents go in:
```
${SISO_WORKSPACE}/agent_os/agents/
```

## Available Models

- `MiniMax-M2.5-highspeed` - Fast
- `claude-sonnet-4-6` - Claude Sonnet
