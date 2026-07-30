# Skills Feedback Loop — Implementation Plan

## Research Findings

### How Claude Agents Work

**Teams + Messaging:**
- Spawned via `Agent` tool with `team_name` param
- Communicate via `SendMessage` — text output is NOT visible to teammates
- Idle ≠ done — idle agents wake on message
- `broadcast` for critical issues only (expensive, N deliveries)
- Team config at `~/.claude/teams/{team}/config.json`

**Subagent Types:**

| Type | Tools | Use For |
|------|-------|---------|
| `general-purpose` | All | Default, any task |
| `Explore` | Read, Glob, Grep, Bash | Codebase research |
| `test-runner` | Bash, Read, Grep, Glob | Running tests |
| `file-creator` | Write, Bash, Read | Batch file creation |
| `Plan` | Read-only | Planning, breaking down tasks |

**Agent Bootstrapping:**
- Agents are **document-driven** — `CLAUDE.md` at root is the entry point
- No `run.sh` for agents — pure file-based bootstrap
- Identity assembled from: `identity.yaml` → `SOUL.md` → `AGENTS.md` → `CLAUDE.md`
- Memory: `memory/brain.md` (long-term) + `memory/journal.md` (session log)

**Key Gotchas:**
- Context NOT inherited on spawn — must pass all context explicitly in prompt
- Subagent `cwd` set at spawn time via team config
- `planModeRequired: true` blocks execution awaiting approval
- Separate contracts: Agent Brain owns task truth; the selected host delivers messages; Skills Hub owns local capability telemetry

---

## Implementation Options

### Option A: Pipeline Chain (Simplest)

Each stage is a **skill script**. A pipeline YAML orchestrates them:

```yaml
pipeline: skills-feedback-loop
steps:
  - skill: skills_researcher
  - skill: skills_analyzer
  - skill: skills_strategist
  - skill: skills_integrator
  - skill: skills_health_monitor
  - skill: skills_improver
```

**Pros:** Leverages existing pipeline DSL. Already built.
**Cons:** Skills run sequentially in one agent context. No parallelism. No persistence between runs.

---

### Option B: Team of Agents (Recommended)

An **orchestrator agent** spawns 6 specialist sub-agents in parallel, collects results, writes state, loops.

```
┌─────────────────────────────────────────────────────┐
│  skills-loop-orchestrator (team lead)              │
│                                                     │
│  Spawns in parallel:                               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │researcher│ │analyzer │ │strategist│          │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘          │
│       │             │             │                  │
│       └─────────────┼─────────────┘                  │
│                     ▼                                │
│              ┌──────────┐                            │
│              │integrator│                            │
│              └────┬─────┘                            │
│                   │                                 │
│       ┌───────────┴───────────┐                    │
│       ▼                       ▼                      │
│  ┌──────────┐          ┌──────────┐                │
│  │ monitor  │          │ improver │                │
│  └────┬─────┘          └────┬─────┘                │
│       │                     │                        │
│       └──────────┬──────────┘                        │
│                  ▼                                   │
│           Loop decision                              │
│       (if new candidates → restart)                  │
└─────────────────────────────────────────────────────┘
```

**Pros:** Parallel execution, stateful across iterations, real feedback loop
**Cons:** More complex, needs state management

---

### Option C: Hybrid — Pipeline Stages, Team Per Stage

Each pipeline stage spins up a team for that stage's work, then tears down. More complex but allows stage-specific parallelism.

**Cons:** Over-engineered. Option B is sufficient.

---

## Recommended: Option B

### Architecture

```
skills-feedback-loop/
├── orchestrator/
│   ├── CLAUDE.md              # Team lead entry point
│   ├── identity.yaml
│   ├── SOUL.md
│   ├── AGENTS.md
│   ├── memory/
│   │   ├── brain.md          # Stores loop state, iteration count
│   │   └── loop_state.json   # Current stage, candidates, results
│   └── workspace/
│       ├── candidates/        # Discovered skills
│       ├── analyses/          # Analysis reports
│       ├── placements/        # Placement decisions
│       └── health/           # Health reports
└── skills/                    # The 6 skill scripts
    ├── skills_researcher.py
    ├── skills_analyzer.py
    ├── skills_strategist.py
    ├── skills_integrator.py
    ├── skills_health_monitor.py
    └── skills_improver.py
```

### Team Setup

```python
TeamCreate("skills-feedback-loop", "Continuous skill discovery and improvement loop")

# Spawn all 6 in parallel
Agent(subagent_type="general-purpose", team_name="skills-feedback-loop",
      prompt=f"""You are skills_researcher. Run discovery scan...
      Save results to {workspace}/candidates/{timestamp}.json""")

Agent(subagent_type="general-purpose", team_name="skills-feedback-loop",
      prompt=f"""You are skills_analyzer. Read candidates from {workspace}/candidates/...
      Write analyses to {workspace}/analyses/...""")

# ... etc
```

### State Machine (in loop_state.json)

```json
{
  "iteration": 3,
  "stage": "improve",
  "candidates": ["skill-A", "skill-B"],
  "analyses": {"skill-A": {...}, "skill-B": {...}},
  "placements": [{"skill": "skill-A", "agent": "PM_Agent", "score": 0.87}],
  "integrations": [{"skill": "skill-A", "agent": "PM_Agent", "status": "installed"}],
  "health_report": {...},
  "improvements": ["Generate scaffold for skill-gap-X"],
  "next_action": "restart" | "stop"
}
```

### Trigger Modes

1. **Cron** — every 6 hours via `CronCreate`
2. **On-demand** — `skills pipeline run skills-feedback-loop`
3. **Event** — triggered by health degradation or new agent creation

---

## Building the Orchestrator Agent

### Step 1: Create the agent directory

From `module_templates/agents/versions/v3/` or v5 template.

### Step 2: Implement the 6 skill scripts

Each is a Python script that:
- Reads input from CLI args or workspace files
- Produces output to workspace
- Returns exit code (0 = success)

### Step 3: Implement orchestrator CLAUDE.md

The orchestrator:
1. Reads current `loop_state.json` (or initializes)
2. Spawns stage sub-agents in parallel
3. Waits for results
4. Updates state
5. Makes loop decision
6. Either restarts or sleeps

### Step 4: Wire to `skills pipeline`

Add `skills_hub/pipelines/skills-feedback-loop.yml` that calls the orchestrator.

---

## Immediate Implementation Steps

1. **Build `skills_health_monitor`** — reads telemetry, outputs orphan/ghost/degraded lists. ~50 lines.
2. **Build `skills_researcher`** — scans GitHub topics, awesome lists. Uses `multisearch`.
3. **Create `skills-feedback-loop` agent** from template
4. **Wire pipeline** — add to `skills_hub/pipelines/`
5. **Add cron trigger** — schedule every 6 hours

---

## How to Run

```bash
# On-demand
python3 skills_hub/scripts/skills pipeline run \
  skills_hub/pipelines/skills-feedback-loop.yml

# Or trigger the agent directly
python3 skills_hub/scripts/skills agents --health-loop
```

---

## Scaling Path

Once working, extend to:
- `skills_analyzer`: Add LLM-based code analysis
- `skills_improver`: Generate actual skill scaffolds from gap analysis
- `skills_strategist`: Use co-invocation data to score placements
- **Git-based distribution**: Each skill becomes a git repo, updates propagate via `git pull`
