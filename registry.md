# Skills Hub Registry

Central registry of skills available to all agents in the SISO ecosystem.

## Core Skills

| Skill | Description | Location |
|-------|-------------|----------|
| os-database | Task management, logging, tags, dependencies, urgency, subtasks | `registry/skills/global/os-database/SKILL.md` |
| timeline | Track thought process, actions, decisions across sessions | `timeline/SKILL.md` |

## Adding New Skills

1. Create a new folder in `skills_hub/`
2. Add a `SKILL.md` file with the skill definition
3. Update this registry
4. Run migration SQL if the skill needs new database tables (put in `tasks/migrations/`)

## Skill Format

Skills use the SKILL.md format with frontmatter:

```yaml
---
name: skill-name
description: What the skill does
user-invocable: true  # if agents can invoke it directly
---
```
