# Skills Hub

Central registry for all SISO agent skills. 23 skills across 7 categories, all documented, versioned, and installable.

## Quick Start

```bash
# List all skills
python3 skills_hub/scripts/skills list

# Search for a skill
python3 skills_hub/scripts/skills search github

# See skill details
python3 skills_hub/scripts/skills info gitsearch

# Check skill health (needs usage data)
python3 skills_hub/scripts/skills health

# Install a skill
python3 skills_hub/scripts/skills install gitsearch

# Link a skill (live updates from hub)
python3 skills_hub/scripts/skills install gitsearch --link

# Resolve dependencies
python3 skills_hub/scripts/skills depsolve multisearch

# Get recommendations
python3 skills_hub/scripts/skills recommend gitsearch

# Run a pipeline
python3 skills_hub/scripts/skills pipeline run pipelines/analyze-and-implement.yml --input "build auth"

# List pipelines
python3 skills_hub/scripts/skills pipeline list
```

---

## Structure

```
skills_hub/
├── registry/
│   ├── skills_registry.json   # Machine-readable registry (23 skills)
│   ├── INDEX.md              # Human-readable index
│   └── skills/              # Skill directories by category
│       ├── devops/          # Infrastructure & deployment
│       ├── code/            # Code generation & implementation
│       ├── data/            # Search & discovery
│       ├── communication/   # Inter-agent messaging
│       ├── testing/         # QA & verification
│       ├── system/          # OS, workspace, task management
│       └── global/          # Cross-cutting concerns
├── scripts/
│   ├── skills               # Main CLI (python3 skills ...)
│   ├── skills_telemetry.py  # Telemetry SDK
│   ├── skills_deps.py       # Dependency graph
│   ├── skills_recommend.py  # Co-invocation recommendations
│   ├── skills_pipeline.py   # Pipeline runner
│   └── agent_skill_tracker.py  # Agent telemetry wrapper
├── pipelines/               # Example pipelines
│   ├── analyze-and-implement.yml
│   └── research-and-deploy.yml
├── templates/skill/         # New skill scaffold
├── docs/                   # Integration docs
├── data/                   # (local skill_events.db — deprecated, now in sisosystem.db)
└── templates/skill/        # New skill scaffold
```

---

## Categories

| Category | Skills |
|----------|--------|
| **devops** | cmux, cmux-browser, github, gitsearch, vercel |
| **code** | agent-builder, agent-setup, analyze_task, implement_story, verify_story |
| **data** | multisearch, websearch, xsearch |
| **communication** | agent-commander, cli-runner, meta-commander |
| **testing** | playwright, verify_story |
| **system** | pm-tasks, task-commander, task-manager, workspace |
| **global** | os-database, subagents |

---

## Standard Skill Structure

Every skill follows this structure:

```
skill-name/
├── SKILL.md           # Required — skill definition with YAML frontmatter
├── README.md          # Optional — long-form docs
├── install.sh         # Optional — installation hook
├── scripts/           # Optional — executable scripts
│   └── main.py
├── config/            # Optional — configuration files
└── examples/         # Optional — usage examples
```

### SKILL.md Frontmatter Schema

```yaml
---
name: skill-id
description: One sentence description
version: 1.0.0
tags: [tag1, tag2]
---
```

---

## Skill Registry Schema

Each skill in `skills_registry.json`:

```json
{
  "skill_id": "gitsearch",
  "name": "GitHub Search",
  "description": "Search GitHub for code, repos, issues, and PRs",
  "category": "devops",
  "tags": ["search", "github", "code-discovery"],
  "version": "1.0.0",
  "dependencies": {
    "skills": ["cli-runner"],
    "packages": ["gh"]
  },
  "install_commands": {
    "system": "brew install gh",
    "skill": "echo 'No additional setup'"
  },
  "metadata": {
    "user_invocable": true,
    "status": "stable"
  }
}
```

---

## Telemetry

Every skill invocation is logged to `~/.SystemDB/sisostem.db` (skill_events table).

```python
from skills_telemetry import track
track("gitsearch", success=True, duration_ms=150, agent_id="my-agent")
```

Health scores are computed from telemetry:

```
health = usage_freq × success_rate × latency_score × context_diversity
```

---

## Building a New Skill

1. Copy the template:
   ```bash
   cp -r skills_hub/templates/skill/ skills_hub/registry/skills/<new-skill>/
   ```

2. Fill in `SKILL.md` with frontmatter and description

3. Add to registry:
   ```bash
   # Edit skills_registry.json manually, or:
   python3 skills_hub/scripts/skills validate <new-skill>
   ```

4. Test:
   ```bash
   python3 skills_hub/scripts/skills validate <new-skill>
   python3 skills_hub/scripts/skills info <new-skill>
   ```

---

## Pipeline DSL

Chain skills together with data passing:

```yaml
pipeline: analyze-and-implement
error_mode: stop  # stop on first failure, or "continue"
steps:
  - skill: analyze_task
    input: "{input}"
  - skill: implement_story
    input: "{steps[0].output}"
  - skill: verify_story
    input: "{steps[1].output}"
```

Run with:
```bash
python3 skills_hub/scripts/skills pipeline run pipelines/analyze-and-implement.yml \
  --input "build a login form"
```

---

## Architecture

- **Registry**: `skills_registry.json` — single source of truth
- **Canonical DB**: `~/.SystemDB/sisostem.db` — task + skill telemetry in one DB
- **CLI**: `skills_hub/scripts/skills` — all commands
- **Telemetry**: `skills_telemetry.py` SDK → `sisostem.db.skill_events`
- **Docs**: This directory + `HUB_DESIGN.md` + `STRATEGIC_ROADMAP.md`
