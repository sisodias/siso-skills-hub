# Phase 2 Progress — Skills Hub Dependency Graph

**Goal:** Build dependency resolution, diamond/cycle detection, and graph analysis for the skills hub.

---

## Checklist

### PH2-T9: Dependency Graph Module + `depsolve` Command
- [x] `scripts/skills_deps.py` with `SkillDeps` class
- [x] `get_install_order()` - topological sort, handles diamonds correctly
- [x] `detect_cycles()` - cycle detection across full graph
- [x] `detect_diamond_deps()` - diamond dependency detection
- [x] `resolve_all()` - unified resolution with install_order, cycles, diamonds
- [x] `skills depsolve` CLI command added to `scripts/skills`
- [x] `--json` flag for JSON output

**Status:** [DONE]
**Deliverable:** `scripts/skills_deps.py`, `skills depsolve` subcommand

**Test Results:**
```
$ python3 scripts/skills depsolve multisearch
Install order for 'multisearch':
  1. websearch
  2. cli-runner
  3. gitsearch
  4. xsearch
  5. multisearch

$ python3 scripts/skills depsolve analyze_task
Install order for 'analyze_task':
  1. analyze_task

$ python3 scripts/skills depsolve task-commander
Install order for 'task-commander':
  1. cmux
  2. pm-tasks
  3. task-commander
```

**Bug Fixed:** Original `get_install_order` had a bug where nodes with no dependencies were added to order but NOT marked as visited, causing duplicates when reached via multiple paths. Fixed by moving `visited.add(node)` before the graph check.

---

## Notes

- Dependency graph built from `registry/skills_registry.json`
- Skills with no dependencies (e.g., `websearch`, `analyze_task`) appear first in install order
- Diamond dependencies detected when same skill is reachable via multiple paths (e.g., `multisearch` -> `websearch` and `multisearch` -> `xsearch` -> `websearch`)
- Cycles would cause `ValueError` to be raised during `get_install_order`
