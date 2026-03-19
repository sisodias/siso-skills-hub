---
name: skills-hub-usage
description: Navigate, discover, install, and use skills from the SISO Skills Hub
disable-model-invocation: false
user-invocable: true
context: agent
agent: general-purpose
allowed-tools: Bash, Read, Write, Edit
---

# Skills Hub Usage Skill

You help agents discover, understand, and use the SISO Skills Hub.

## What the Skills Hub Provides

The Skills Hub is a central registry of all SISO agent skills. Every skill has:
- **SKILL.md** — definition with frontmatter (name, description, version, tags)
- **README.md** — long-form documentation
- **scripts/** — executable Python/bash scripts
- **config/** — optional configuration
- **examples/** — usage examples

## How to Use the Hub CLI

All commands are run via: `python3 $SISO_HUB/scripts/skills <command>`

### Discovery Commands

```bash
# List all skills, optionally filtered by category
python3 $SISO_HUB/scripts/skills list [--category devops]

# Search skills by name, description, or tag
python3 $SISO_HUB/scripts/skills search github

# Show full details of a specific skill
python3 $SISO_HUB/scripts/skills info gitsearch

# Get health scores (needs usage data first)
python3 $SISO_HUB/scripts/skills health [--skill <id>]
```

### Installation Commands

```bash
# Install a skill (copy to ~/.claude/skills/)
python3 $SISO_HUB/scripts/skills install gitsearch

# Symlink instead (updates sync from hub automatically)
python3 $SISO_HUB/scripts/skills install gitsearch --link

# Validate a skill's structure
python3 $SISO_HUB/scripts/skills validate gitsearch
```

### Dependency Commands

```bash
# Show install order including all transitive dependencies
python3 $SISO_HUB/scripts/skills depsolve multisearch

# Get co-invocation recommendations
python3 $SISO_HUB/scripts/skills recommend gitsearch
```

### Pipeline Commands

```bash
# List available pipelines
python3 $SISO_HUB/scripts/skills pipeline list

# Run a pipeline
python3 $SISO_HUB/scripts/skills pipeline run \
  $SISO_HUB/pipelines/analyze-and-implement.yml \
  --input "build a login form"
```

### Publishing & Diagnosis

```bash
# Publish a new version
python3 $SISO_HUB/scripts/skills publish my-skill --version 1.0.0

# Check skill versions
python3 $SISO_HUB/scripts/skills versions gitsearch

# Diagnose a skill (error clustering, health report)
python3 $SISO_HUB/scripts/skills diagnose gitsearch [--days 30]
```

## Discovery Patterns

**By category:** If you need skills for deployment, try `devops`. For testing, try `testing`.

**By tag:** Search for what you need — `python3 skills search browser` finds `playwright`.

**By dependency:** If you install `multisearch`, run `depsolve multisearch` first to see what it needs.

## Skill Categories

| Category | What it contains |
|----------|-----------------|
| **devops** | git, github, cmux, vercel, gitsearch |
| **code** | agent-builder, agent-setup, analyze_task, implement_story, verify_story |
| **data** | websearch, xsearch, multisearch |
| **communication** | agent-commander, cli-runner, meta-commander, task-commander |
| **testing** | playwright, verify_story |
| **system** | workspace, task-manager, pm-tasks |
| **global** | os-database, subagents |

## Telemetry

Every skill invocation is tracked in `~/.SystemDB/sisostem.db`. You can see skill health:

```bash
python3 $SISO_HUB/scripts/skills health
```

Health = usage × success rate × latency × context diversity. Skills with low health may need attention.

## When You Need a New Skill

1. Check if it already exists: `skills search <keyword>`
2. Check the backlog: `skills_hub/backlog/requests.md`
3. Build it from the template: `cp -r $SISO_HUB/templates/skill/ $SISO_HUB/registry/skills/<new-skill>/`
4. Fill in SKILL.md with name, description, version, tags
5. Publish it: `skills publish <new-skill> --version 1.0.0`

## Your Task

When the user or another agent asks about using skills from the hub, use the commands above to help them:
- List available skills
- Search for relevant skills
- Show skill details
- Help install or link skills
- Run pipelines when appropriate
