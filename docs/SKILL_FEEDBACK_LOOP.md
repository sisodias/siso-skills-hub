# Skills Feedback Loop Pipeline

> A self-improving skill ecosystem. Skills discover, analyze, integrate, monitor, and improve themselves.

---

## Concept

The Skills Hub becomes a living system, not a static registry. A pipeline continuously:
1. **Discovers** new skills from external sources
2. **Analyzes** them — purpose, patterns, quality, dependencies
3. **Places** them — identifies which agents/contexts need them
4. **Integrates** them — installs, adapts, reverse-engineers useful patterns
5. **Monitors** them — tracks usage, health, co-invocation patterns
6. **Improves** them — identifies gaps, generates scaffolds, evolves existing skills

```
Discover → Analyze → Place → Integrate → Monitor → Improve → (back to Discover)
                                        ↑                          |
                                        └────── feedback loop ────┘
```

---

## Pipeline Architecture

### Agents

| Agent | Role |
|-------|------|
| `skills_researcher` | Scans external sources for new skills |
| `skills_analyzer` | Reverse-engineers skill structure, patterns, quality |
| `skills_strategist` | Maps skills to agent needs, spots gaps |
| `skills_integrator` | Installs, adapts, and integrates skills |
| `skills_health_monitor` | Tracks usage, reports on health trends |
| `skills_improver` | Generates improvements, scaffolds, gap-fillers |

### Stage 1: Discover

**Input:** Discovery config (sources, frequency, filters)
**Output:** List of candidate skills

Sources to scan:
- GitHub: `awesome-sellm列表`, topic: `claude-agent-skill`, `siso-agent-skill`
- GitHub search: `SKILL.md`, skill patterns in code
- SISO internal: new directories added to agent workspaces
- User submissions: `skills_hub/backlog/requests.md`
- Telemetry orphans: skills invoked but not in registry

**Skills used:** `multisearch`, `gitsearch`

```bash
# Example discovery query
gh search repos "SKILL.md agent skill" --topic claude --limit 50
```

### Stage 2: Analyze

**Input:** Candidate skill (repo URL or local path)
**Output:** Skill analysis report

Analysis dimensions:
- **Purpose** — What does it do? Categorize.
- **Structure** — SKILL.md quality, script completeness, examples
- **Dependencies** — Required skills, system packages, external APIs
- **Patterns** — Invocation style, error handling, telemetry
- **Quality score** — Code quality, docs, test coverage
- **Compatibility** — Works with current hub architecture?

**Reverse-engineering:** Extract reusable patterns from successful external skills.

### Stage 3: Placement

**Input:** Skill analysis
**Output:** Agent targeting recommendations

Mapping logic:
- **By category need:** agents with missing skills in their domain
- **By telemetry gap:** skills invoked via subprocess but not tracked
- **By dependency:** if agent uses X, it probably needs Y
- **By workflow:** pipeline step skills should be near their co-invocators

```python
placement_score = (
    category_match * 0.3 +
    dependency_fit * 0.3 +
    telemetry_gap * 0.2 +
    workflow_proximity * 0.2
)
```

### Stage 4: Integrate

**Input:** Skill + target agent
**Output:** Skill installed and validated

Actions:
- Install to agent via `skills install --agent <name>`
- Validate structure
- Set up telemetry tracking
- Register in hub if new
- Create initial health baseline

### Stage 5: Monitor

**Input:** Live telemetry from the Skills-owned `telemetry.db` (`SISO_SKILLS_TELEMETRY_DB`)
**Output:** Health reports, usage patterns

Continuous monitoring:
- Health scores per skill (usage × success × latency × diversity)
- Co-invocation matrix — which skills cluster together
- **Orphan skills** — skills invoked but not in registry
- **Ghost skills** — registered skills never invoked
- **Degraded skills** — error rate > 20%
- **Stale skills** — not used in 30 days

### Stage 6: Improve

**Input:** Monitoring data
**Output:** Improvements, new scaffolds, gap fills

Improvement types:
- **Skill gaps** — identified by placement analysis, scaffold generated
- **Pattern extraction** — successful patterns reverse-engineered into templates
- **Dependency fixes** — broken deps updated
- **Health remediation** — degraded skills flagged for author review
- **Composition suggestions** — pipeline recommendations from co-invocation data

---

## Pipeline Implementation

### YAML Definition

```yaml
pipeline: skills-feedback-loop
description: Continuous discovery, analysis, integration, and improvement of skills
schedule: "0 */6 * * *"  # Every 6 hours via cron

steps:
  - skill: skills_researcher
    input: "{config.sources}"
    output_var: candidates

  - skill: skills_analyzer
    input: "{candidates}"
    output_var: analyses

  - skill: skills_strategist
    input: "{analyses}"
    output_var: placements

  - skill: skills_integrator
    input: "{placements}"
    output_var: integrations

  - skill: skills_health_monitor
    input: ""  # Reads the Skills telemetry store, never Agent Brain SQLite
    output_var: health_report

  - skill: skills_improver
    input: "{health_report}"
    output_var: improvements

error_mode: continue  # Don't stop on one failure
```

### Trigger Modes

1. **Scheduled (cron):** `"0 */6 * * *"` — every 6 hours
2. **On-demand:** `skills pipeline run skills-feedback-loop`
3. **Event-driven:** When a new agent is created, new skill is published, or health degrades

### Output Artifacts

| Artifact | Where |
|----------|-------|
| Discovery candidates | `skills_hub/backlog/candidates/<date>.json` |
| Analysis reports | `skills_hub/backlog/analyses/<skill_id>.md` |
| Placement maps | `skills_hub/backlog/placements/<date>.json` |
| Health reports | `skills_hub/backlog/health/<date>.md` |
| Improvement PRDs | `skills_hub/backlog/improvements/<skill_id>.md` |

---

## Existing Components to Leverage

| Component | How used |
|-----------|----------|
| `multisearch` | Stage 1 discovery |
| `gitsearch` | Stage 1 GitHub scanning |
| `xsearch` | Stage 1 social/trend discovery |
| `skills info` | Stage 2 structure analysis |
| `skills depsolve` | Stage 2 dependency mapping |
| `skills install --agent` | Stage 4 integration |
| `skills health` | Stage 5 monitoring |
| `skills diagnose` | Stage 5 error analysis |
| `skills recommend` | Stage 6 co-invocation patterns |

---

## New Skills to Build

### skills_researcher
Scans external sources for candidate skills.

**Inputs:** source config (GitHub topics, awesome lists, search queries)
**Outputs:** candidate list with URLs, descriptions, star counts

```bash
python3 $SISO_HUB/scripts/skills_researcher.py \
  --sources github,awesome,internal \
  --topic claude-agent-skill \
  --min-stars 10
```

### skills_analyzer
Reverse-engineers a skill and produces analysis report.

**Inputs:** skill repo URL or local path
**Outputs:** structured analysis (purpose, structure, quality, patterns, deps)

### skills_strategist
Maps skills to agent needs and identifies gaps.

**Inputs:** skill analyses + current agent inventory (from `skills agents`)
**Outputs:** placement recommendations ranked by score

### skills_integrator
Installs and validates skill into target agent.

**Inputs:** placement recommendations
**Outputs:** installation report, validation results

### skills_health_monitor
Reads telemetry and produces health report.

**Inputs:** Reads the Skills-owned telemetry store configured by `SISO_SKILLS_TELEMETRY_DB`
**Outputs:** orphan skills, ghost skills, degraded skills, usage trends

### skills_improver
Generates improvements from health data.

**Inputs:** health report
**Outputs:** scaffold suggestions, pattern improvements, gap-filler PRDs

---

## Immediate Next Steps

1. **Build `skills_researcher`** — simplest new skill, leverages existing tools
2. **Build `skills_health_monitor`** — reads existing telemetry, produces actionable report
3. **Wire up `skills agents` output → `skills_strategist`** — closes the placement loop
4. **Add cron trigger** — schedule the loop to run every 6 hours

---

## PH7 Opportunity: Testing Harness

Every new skill should have:
- `tests/test_skill.py` — basic invocation test
- `tests/examples_test.py` — example outputs match expected

Pipeline should run tests before marking skill "stable" in registry.
