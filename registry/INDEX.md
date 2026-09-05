# Skill Registry

> Auto-generated from `skills_registry.json`. Do not edit manually.

## Categories

### code

| Skill | Description | Source |
|---|---|---|
| agent-builder | Create new agents from the SISO v3 agent template | bundled |
| agent-setup | Create new agent from V4 template with memory system pre-configured | bundled |
| analyze_task | Analyze a task and decompose into user stories | bundled |
| implement_story | Implement a single user story with tests | bundled |

### communication

| Skill | Description | Source |
|---|---|---|
| agent-commander | Create workspaces, start agents, and communicate with them via CMUX | bundled |
| cli-runner | Run SISO CLI commands and interact with agents | bundled |
| meta-commander | Communicate with META agents in the SISO ecosystem | bundled |

### data

| Skill | Description | Source |
|---|---|---|
| multisearch | Run web, GitHub, and X searches in parallel for comprehensive research | bundled |
| websearch | Search the web using Perplexity Sonar via OpenRouter | bundled |
| xsearch | Search X (Twitter) for discussions, opinions, and latest updates | bundled |

### devops

| Skill | Description | Source |
|---|---|---|
| cmux | Terminal multiplexer for Claude Code with socket API for workspace control and browser automation | bundled |
| cmux-browser | Control CMUX browser for automated testing and browser interactions | bundled |
| github | Complete GitHub workflow for SISO codebase - branch, commit, push, merge | bundled |
| gitsearch | Search GitHub for code, repos, issues, and PRs | bundled |
| publish | Publish a reviewed static directory or HTML file to an authorized public Cloudflare Pages project with exact readback and a caller handoff receipt. | bundled |
| vercel | Deploy SISO Internal Lab to Vercel | bundled |

### global

| Skill | Description | Source |
|---|---|---|
| os-database | Core Agent OS Database for telemetry, tasks, and timeline tracking | bundled |
| owner-handoff | Use the owning Playbook's preservation, cold-read and single-writer handoff gate. | bundled |
| owner-writeback | Persist owned material state and append an index pointer through the consuming project's existing adapter. | bundled |
| skill-author | Author, register, validate and safely install one reviewed skill from its owning source. | bundled |
| skills-hub-usage | Navigate, discover, install, and use skills from the SISO Skills Hub | bundled |
| subagents | Spawn and manage parallel subagents for concurrent task execution | bundled |
| writeback | Append one material owner line to a repository log and mirror it to the existing Agent Zero ledger, with safe retries. | bundled |

### pipeline

| Skill | Description | Source |
|---|---|---|
| check_status | Check the current status of a pipeline run by reading progress files | bundled |
| create_progress | Initialize or update progress.md for a pipeline run | bundled |
| pass_to_next | Pass context to the next agent in the pipeline by writing output files | bundled |
| read_job_ticket | Read and validate a JobTicket JSON file from inbox | bundled |

### system

| Skill | Description | Source |
|---|---|---|
| pm-tasks | Simple PM task manager - create, list, update tasks | bundled |
| task-commander | Log tasks and communicate with agents using the SISO task database | bundled |
| task-manager | Full task pipeline system with steps, artifacts, and execution logging | bundled |
| workspace | Understand and navigate the SISO workspace | bundled |

### testing

| Skill | Description | Source |
|---|---|---|
| playwright | Automated browser testing for SISO Internal Lab | bundled |
| verify_story | Verify a story implementation meets acceptance criteria | bundled |

---

**Total: 33 skills**

Use `python3 scripts/skills list`, `search <query>`, or `info <skill>` to explore.
