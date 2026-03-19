# Skills Hub Strategic Roadmap

> Think 10x. Build the telemetry foundation first. Everything else compounds from data.

---

## Big Bang: Unified Telemetry Pipeline

**The single initiative that compounds all others.**

Every skill invocation logged to a central event stream: skill_id, agent_id, timestamp, duration, success/failure, context_hash, input_size, output_size. This is the nervous system of the entire ecosystem.

Without this, you cannot:
- Know which skills actually work
- Improve anything based on evidence
- Detect skill rot when dependencies change
- Recommend skills intelligently
- Score skill health objectively

**With telemetry, every other initiative becomes data-driven.**

---

## Top 10 Improvements (ranked by impact/effort)

### 1. Skill Invocation Telemetry

- **What**: Every skill invocation logged to `skill_events` table: `event_id, skill_id, agent_id, session_id, timestamp, duration_ms, success, error_type, context_hash, input_summary, output_summary`
- **Why**: You cannot improve what you cannot measure. Currently zero visibility into skill usage patterns.
- **How**: Lightweight async logger. Skill wrapper script intercepts invocations. Schema:
  ```sql
  CREATE TABLE skill_events (
    event_id TEXT PRIMARY KEY,
    skill_id TEXT NOT NULL,
    agent_id TEXT,
    session_id TEXT,
    timestamp REAL,
    duration_ms INTEGER,
    success INTEGER,
    error_type TEXT,
    context_hash TEXT,
    input_size INTEGER,
    output_size INTEGER
  );
  ```
  Telemetry SDK: `from skills_telemetry import track; track("websearch", success=True)`
- **Effort**: Low
- **Impact**: 10x — unlocks all other initiatives

---

### 2. Skill Health Scores

- **What**: Composite score per skill: `health = usage_freq_score * success_rate * latency_score * context_diversity`
- **Why**: Surfaced from telemetry. Identifies skills that need attention. Gives authors concrete metrics to improve.
- **How**:
  - `usage_freq_score`: log(scale, percentile rank over 30 days)
  - `success_rate`: % invocations with `success=1`
  - `latency_score`: 1 - min(avg_duration_ms / p95_threshold, 1.0)
  - `context_diversity`: entropy of context_hash distribution (high entropy = skill used in many contexts)
  - Expose via `skills hub health [--skill <id>]`
- **Effort**: Low
- **Impact**: High — turns raw telemetry into actionable signals

---

### 3. Skill Dependency Graph with Conflict Detection

- **What**: Build DAG from `dependencies.skills` in registry. Detect cycles, version conflicts, diamond dependencies. Provide `skills hub depsolve <skill_id>` to install with all transitive deps.
- **Why**: The current flat dep list is insufficient. `multisearch` depends on `websearch, gitsearch, xsearch` but if `xsearch` depends on `websearch`, installing `multisearch` without transitive deps breaks. No visibility into this today.
- **How**:
  - Parse all `dependencies.skills` fields, build directed graph
  - Topological sort for install order
  - Cycle detection via DFS (error if cycle found)
  - Conflict detection: if skill A requires `skill X >= 2.0` and skill B requires `skill X < 2.0`, surface conflict
  - `skills hub depsolve websearch` outputs install order and any conflicts
- **Effort**: Medium
- **Impact**: High — unblocks composition and prevents installation failures

---

### 4. Context-Aware Skill Recommendations

- **What**: "Given what you're working on, you might also need X" — co-invocation-based recommendation engine.
- **Why**: Discovery is manual. Agents/Users must know to search for a skill. Co-invocation patterns reveal implicit relationships (e.g., `verify_story` is always used after `implement_story`).
- **How**:
  - On each telemetry event, log co-invocations (skills used in same session within 30 min)
  - Build co-invocation matrix: `P(B|A) = count(A,B) / count(A)`
  - When agent invokes skill A, surface skills with high `P(B|A)` that aren't yet installed
  - Expose via `skills hub recommend <skill_id>` and as a nudge during skill invocation
- **Effort**: Low
- **Impact**: High — turns implicit knowledge into explicit suggestions

---

### 5. Skill Pipeline DSL

- **What**: Chain skills together: `skill_a | skill_b | skill_c` with data passing and error handling.
- **Why**: Real tasks are multi-step. Agents currently hand-roll skill sequences manually. A pipeline abstraction standardizes composition and makes workflows reusable.
- **How**:
  - Pipeline format (YAML):
    ```yaml
    pipeline: analyze-and-implement
    steps:
      - skill: analyze_task
        input: "{task_description}"
      - skill: implement_story
        input: "{steps[0].output}"
      - skill: verify_story
        input: "{steps[1].output}"
    error_mode: continue|stop
    ```
  - `skills pipeline run analyze-and-implement --input "build auth"`
  - Pipeline runner handles: invoke skill, capture output, pass to next skill, handle errors
  - Each step's output is stored in `steps[N].output` for interpolation
- **Effort**: Medium
- **Impact**: High — transforms skills from isolated tools into composable workflows

---

### 6. Git-Based Skill Distribution

- **What**: Each skill is a git submodule. Registry is a manifest. `skills hub install` pulls from remote.
- **Why**: Currently skills live in the hub repo. No versioning, no remote install, no contribution flow. For a distributed agent ecosystem, skills must be independently versioned and distributable.
- **How**:
  - Each skill becomes its own git repo under `skills_hub/skills/<skill_id>/.git`
  - Registry gains `version`, `commit_hash`, `remote_url` fields
  - `skills hub install websearch` clones from remote
  - `skills hub publish` pushes local skill to remote and updates registry
  - `skills hub versions websearch` lists all tags
- **Effort**: Medium
- **Impact**: High — enables ecosystem growth beyond single-hub deployment

---

### 7. Automated Skill Testing Harness

- **What**: Standard `tests/` structure per skill. Hub runs tests before marking skill "stable."
- **Why**: Skills rot. Dependencies change. Without tests, there's no way to validate a skill still works after hub updates.
- **How**:
  - Template adds `tests/test_skill.py` with standard hooks:
    ```python
    def test_invocation():
        result = invoke_skill("skill_id", sample_input)
        assert result.success
        assert "expected_output" in result.output
    ```
  - `skills hub test <skill_id>` runs the test suite
  - CI/CD: on registry update, run tests for changed skills
  - `metadata.status` must pass tests to transition from `beta` to `stable`
- **Effort**: Medium
- **Impact**: Medium — prevents regressions and raises baseline quality

---

### 8. Skill Self-Analysis

- **What**: Skills log their own failure modes. Periodic analysis surfaces patterns and improvement suggestions.
- **Why**: Instead of requiring human review of telemetry, skills that detect their own failure patterns can flag issues proactively.
- **How**:
  - Skills call `skills_telemetry.log_fidelity(skill_id, success, error_type, retry_count)` after each invocation
  - Weekly analysis job: cluster errors by `error_type`, identify top failure patterns per skill
  - Generate `skill_id.failure_report.md` with: top 5 failure modes, retry rates, suggested fixes
  - If a skill's error rate exceeds threshold (e.g., 20%), auto-mark as `degraded` in registry
  - Expose via `skills hub diagnose <skill_id>`
- **Effort**: Medium
- **Impact**: Medium — closes the feedback loop without manual review

---

### 9. AI-Assisted Skill Scaffold Generation

- **What**: Given a natural language description, generate a working skill scaffold with SKILL.md, scripts, and tests.
- **Why**: Authoring skills is manual. A generator lowers the barrier to contribute new skills and can bootstrap from existing successful patterns.
- **How**:
  - `skills hub generate "search GitHub for code patterns and return relevant files"`
  - Uses existing skill templates as few-shot examples
  - Generates: `SKILL.md` with prompt engineering, `scripts/` with boilerplate, `tests/test_skill.py`
  - Human reviews and edits the scaffold
  - Based on telemetry, identifies which existing skills are most similar to generate from
- **Effort**: High
- **Impact**: Medium — accelerates skill authoring but requires AI infrastructure

---

### 10. Formal Skill Verification (Signatures & Drift Detection)

- **What**: Skill manifests include output signatures. Hub detects when skill output drifts from expected schema.
- **Why**: Skills can silently change behavior (output format, error codes). Without signatures, there's no way to detect this until agents fail.
- **How**:
  - `skills hub register websearch --output-schema '{"type": "object", "properties": {"results": {"type": "array"}}}`
  - Periodic sampling: run skill with known input, compare output against schema
  - If drift detected: flag skill, notify author, optionally auto-deprecate
  - Schema stored in `skill.manifest.json` alongside SKILL.md
- **Effort**: High
- **Impact**: Medium — prevents silent breakage but complex to implement reliably

---

## Summary Matrix

| Rank | Initiative | Effort | Impact | Status |
|------|-----------|--------|--------|--------|
| 1 | Telemetry Pipeline | Low | 10x | ✅ DONE |
| 2 | Health Scores | Low | High | ✅ DONE |
| 3 | Dependency Graph | Medium | High | ✅ DONE |
| 4 | Recommendations | Low | High | ✅ DONE |
| 5 | Pipeline DSL | Medium | High | ✅ DONE |
| 6 | Git Distribution | Medium | High | ✅ DONE |
| 7 | Testing Harness | Medium | Medium | ⏳ Not started |
| 8 | Self-Analysis | Medium | Medium | ✅ DONE |
| 9 | Scaffold Generation | High | Medium | ⏳ Not started |
| 10 | Output Signatures | High | Medium | ⏳ Not started |

## Recommended Build Order

```
Phase 1 (Week 1-2):   #1 Telemetry + #2 Health Scores
                      -> You now have data. Everything else is downstream.

Phase 2 (Week 3-4):   #4 Recommendations + #3 Dependency Graph
                      -> Improve discovery and prevent install failures.

Phase 3 (Week 5-6):   #5 Pipeline DSL + #7 Testing Harness
                      -> Composition and quality enforcement.

Phase 4 (Week 7-8):   #6 Git Distribution + #8 Self-Analysis
                      -> Distribution and automated maintenance.

Phase 5 (Ongoing):    #9 Scaffold Generation + #10 Output Signatures
                      -> Advanced authoring and drift detection.
```

## The Compounding Effect

Every initiative amplifies the others:
- Telemetry enables health scores, which enable self-analysis
- Health scores enable recommendations, which enable scaffold generation
- Dependency graph enables pipelines, which enable composition
- Git distribution enables the ecosystem to grow beyond the hub

**Build telemetry first. The rest becomes obvious.**

---

## Phase 1 Integration Decisions (Completed)

### Telemetry Schema Location: Consolidated into sisosystem.db

**Decision (2026-03-19):** Skill telemetry (`skill_events` table) now lives in `~/.SystemDB/sisostem.db`, NOT in a separate file.

**History:**
- Original: Separate `skills_hub/data/skill_events.db` for domain separation
- Consolidated: Merged into `sisosystem.db` for cross-domain query capability

**Rationale:**
- `skill_events.session_id` can JOIN to `sisosystem.sessions` and `sisosystem.tasks`
- Enables: "Show me all skill invocations for task X" queries
- Single operational burden: one backup, one path, one connection
- Both task tracking and skill telemetry are equally critical to observability
- `resource-registry.db` remains SEPARATE (read-heavy catalog, not event log)

### Agent Skill Invocation: Subprocess Scripts

**Decision:** Agents invoke skills almost exclusively via subprocess Python scripts, NOT via import or SKILL.md loading.

**Invocation form:**
```bash
python3 .claude/skills/<skill-id>/scripts/<script>.py <args>
```

**Top skills by invocation frequency:**
1. os-database scripts (get_my_tasks, create_task, update_task, log_event) — multiple calls per session
2. pm-tasks scripts — task management
3. websearch/perplexity_search.py — research skills
4. gitsearch, xsearch, multisearch — discovery skills

**SKILL.md with `${CLAUDE_SKILL_DIR}`** is used for subagent execution contexts (websearch, xsearch, gitsearch, multisearch) where the agent runs as a forked process. These still ultimately invoke Python scripts.

### No Structural Changes Required

Phase 1 telemetry does not require any changes to the agent ecosystem structure:
- Existing subprocess invocation pattern is compatible with telemetry insertion
- A thin wrapper script (`scripts/agent_skill_tracker.py`) is sufficient for auto-tracking
- No changes to SKILL.md format, agent templates, or hook infrastructure needed
- Skills remain self-contained with no mandatory telemetry dependency

### Phase 1 Status

| Task | Status | Notes |
|------|--------|-------|
| PH1-T1: Telemetry Pipeline | ✅ DONE | SDK + CLI + DB schema → consolidated into sisosystem.db |
| PH1-T2: Health Scores | ✅ DONE | `skills hub health` command |
| PH1-T3: Agent Runtime Integration | ✅ DONE | Wrapper script + invocation patterns documented |
| PH1-T4: Integration Review | ✅ DONE | DB consolidation decision made and implemented |

### Phase 2 Status

| Task | Status | Notes |
|------|--------|-------|
| PH2-T9: Dependency Graph | ✅ DONE | `skills hub depsolve` + cycle/diamond detection |
| PH2-T10: Recommendations | ✅ DONE | `skills hub recommend` + P(B\|A) co-invocation engine |

### Phase 3 Status

| Task | Status | Notes |
|------|--------|-------|
| PH3-T11: Pipeline DSL | ✅ DONE | `skills pipeline run/list` + 2 example pipelines |

### Phase 4 Status (In Progress)

| Task | Status | Notes |
|------|--------|-------|
| PH4-T12: Git Distribution | ✅ DONE | publish, versions |
| PH4-T13: Self-Analysis | ✅ DONE | diagnose, auto-degrade, failure reports |
