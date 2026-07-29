# Skills Hub Audit Report

**Date:** 2026-03-19
**Auditor:** skills_builder_agent
**Location:** `${SISO_WORKSPACE}/agent_os/skills_hub/`

---

## 1. Directory Structure

```
skills_hub/
├── registry/               # Live skills
│   ├── INDEX.md           # Central skill list (22 skills)
│   └── skills/            # 22 skill directories
├── backlog/               # Requested but not built
│   └── requests.md        # Empty template
├── in_progress/           # Skills being built
│   └── README.md          # Just a placeholder
├── registry.md            # Hub-level registry doc
├── README.md              # Hub usage guide
├── scripts/               # Hub-level helper scripts
│   ├── agent-tmux-helpers.sh
│   └── spawn-agent.sh
└── timeline/              # (not explored)
```

---

## 2. All Skills (22 Total)

| Skill | SKILL.md | README.md | Scripts | Subdirs | Other Files |
|-------|----------|-----------|---------|---------|-------------|
| agent-builder | YES | YES | - | - | TESTING_AGENT.md |
| agent-commander | YES | YES | - | - | - |
| agent-setup | YES | - | setup.sh | scripts/ | - |
| analyze_task | YES | YES | - | - | - |
| cli-runner | YES | YES | - | - | - |
| cmux | YES | YES | - | - | - |
| cmux-browser | YES | YES | - | - | - |
| github | YES | YES | - | - | - |
| gitsearch | YES | YES | - | examples/ | gitsearch_examples.md |
| implement_story | YES | YES | - | - | - |
| meta-commander | YES | YES | - | - | - |
| multisearch | YES | YES | - | - | - |
| playwright | YES | YES | - | - | - |
| pm-tasks | YES | - | pm_tasks.py | scripts/ | - |
| task-commander | YES | YES | - | - | - |
| task-manager | YES | YES | siso-tasks.py, *.py (5) | scripts/ | siso_tasks.db-shm, siso_tasks.db-wal |
| verify_story | YES | YES | - | - | - |
| vercel | YES | YES | - | - | deploy.md |
| websearch | YES | YES | perplexity_search.py | examples/ | websearch_examples.md |
| workspace | YES | YES | - | - | - |
| xsearch | YES | YES | - | - | - |
| global/os-database | YES | YES | 50+ Python scripts | scripts/, rules/, workflows/ | config.json, state.json, schema.sql, DATABASE.md, symlinks |
| global/subagents | YES | YES | - | templates/ | parallel-spawn.md, research.md |

**Note:** INDEX.md lists `memory-setup` as skill #21 but no corresponding directory exists.

---

## 3. Documentation Quality

### Well-Documented (have SKILL.md + README.md)
agent-builder, agent-commander, analyze_task, cli-runner, cmux, cmux-browser, github, gitsearch, implement_story, meta-commander, multisearch, playwright, task-commander, task-manager, verify_story, vercel, websearch, workspace, xsearch

### Minimal Documentation (SKILL.md only, no README.md)
agent-setup, pm-tasks

### Missing Documentation
- `global/` skills: os-database (well documented but has symlinks that could break), subagents
- `memory-setup` listed in INDEX but has no directory

---

## 4. Naming Conventions

- **Skill names:** kebab-case (e.g., `agent-builder`, `gitsearch`, `cmux-browser`)
- **Directories:** kebab-case matching skill name
- **SKILL.md:** CamelCase or kebab-case for the skill name in frontmatter
- **Scripts:** snake_case Python files, kebab-case shell scripts

---

## 5. Skill Structure Patterns

### Pattern A: Minimal (most skills)
```
skill-name/
├── SKILL.md       # Required
└── README.md      # Optional
```

### Pattern B: With Scripts
```
skill-name/
├── SKILL.md
├── README.md
├── script.py
└── scripts/
    └── script.py
```

### Pattern C: Complex (os-database)
```
global/skill-name/
├── SKILL.md
├── README.md
├── config.json
├── state.json
├── schema.sql
├── *.sh
├── requirements.txt
├── scripts/        # 50+ Python scripts
├── rules/          # Agent behavior rules
└── workflows/      # SOPs
```

---

## 6. Central Registry Files

| File | Location | Purpose |
|------|----------|---------|
| INDEX.md | registry/ | Master list of all 22 skills |
| registry.md | skills_hub/ | Hub-level overview + add skill instructions |
| README.md | skills_hub/ | Usage guide |

---

## 7. Key Issues / Observations

1. **`skills_repository/` path does not exist.** Task referenced `/skills_repository/` but actual hub is at `skills_hub/`. Likely rename.

2. **`memory-setup` is listed in INDEX.md but has no directory.** Dead entry or missing skill.

3. **Historical: `os-database` had broken absolute symlinks.** Public-release cleanup replaced the remaining machine-specific documentation symlink with a repository-owned file; `rules` and `workflows` are now regular directories.

4. **`task-manager` contains SQLite WAL/SHM files** (siso_tasks.db-wal, siso_tasks.db-shm). These are runtime artifacts and shouldn't be in the skill directory.

5. **`in_progress/` is empty** — just a README placeholder. No skills currently being built.

6. **`backlog/requests.md` is an empty template** — no actual skill requests logged.

7. **No install mechanism.** Skills are copied manually (`cp -r`). No `requirements.txt` except for os-database. No `package.json`. No central install script.

8. **No versioning.** No version fields in SKILL.md frontmatter.

9. **SKILL.md format is inconsistent.** Some use `---` YAML frontmatter, some don't. No enforced schema.

---

## 8. Recommendations

1. Resolve `skills_repository` vs `skills_hub` naming confusion
2. Remove dead entry `memory-setup` from INDEX.md or create the directory
3. Fix broken symlinks in os-database
4. Add `.gitignore` to exclude `*.db-wal`, `*.db-shm`, `__pycache__/`
5. Standardize SKILL.md frontmatter schema (name, description, allowed-tools, version)
6. Implement actual install mechanism (pip install, npm link, or unified copy script)
7. Populate backlog/in_progress or remove them
