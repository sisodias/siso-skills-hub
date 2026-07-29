---
name: workspace
description: Understand and navigate the SISO Internal Lab workspace
version: 1.0.0
tags:
  - navigation
  - workspace
---

# Workspace Skill

Understand and navigate the SISO Internal Lab workspace.

## Workspace Location

```
${SISO_WORKSPACE}/SISO_Internal_Lab/
```

## Directory Structure

```
SISO_Internal_Lab/
├── agents/              # Agent modules
│   └── PM_Agent/       # This agent (Project Manager)
│
├── codebase/            # Main application code
│   ├── src/            # React frontend
│   ├── api/            # Backend API
│   ├── public/         # Static assets
│   └── package.json    # Dependencies
│
├── swarms/             # Pipeline workflows
│   └── execution_pipeline/
│
├── docs/               # Documentation
│
├── inbox/              # External tasks
│
├── .tasks/            # Task backlog system
│   ├── backlog/       # Pending tasks
│   ├── in_progress/   # Active tasks
│   └── completed/     # Done tasks
│
├── .claude/           # Claude config
│
└── workspace-map.md    # Workspace overview
```

## Key Files

- `CLAUDE.md` - Project context for Claude
- `AGENTS.md` - Agent definitions
- `SOUL.md` - Agent mindset

## Commands

### List Agents
```bash
ls ${SISO_WORKSPACE}/SISO_Internal_Lab/agents/
```

### List Codebase Structure
```bash
ls ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase/
```

### Check Tasks
```bash
ls ${SISO_WORKSPACE}/SISO_Internal_Lab/.tasks/
```

## Running the App

### Development
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
npm run dev
```

### Production Build
```bash
cd ${SISO_WORKSPACE}/SISO_Internal_Lab/codebase
npm run build
```

## External Integrations

- **GitHub:** Lordsisodia/siso-agency-internal
- **Vercel:** siso-internal (auto-deploys on push to main)
- **Database:** SQLite at .SystemDB/sisosystem.db
