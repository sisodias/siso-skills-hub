# Provenance and publication cleanup

## Current public home

- Work: `gls:work:8acb11e9-026f-47e3-b620-bb1b969bcbcd`
- Repository: `Lordsisodia/siso-skills-hub`
- Review date: 2026-07-30

The existing Hub was reused because it already had a coherent registry, CLI, dependency graph, telemetry tools, pipeline DSL, templates, 28 bundled skills, and source history.

During the public-release audit, an embedded OpenRouter credential was found in the initial history. The current source was changed to require `OPENROUTER_API_KEY` from the environment, and all repository history was rewritten with the exposed value replaced before the cleaned `main` branch was force-published. The credential must still be revoked and rotated at the provider; Git history cleanup cannot invalidate a disclosed key or erase third-party caches and clones.

The same audit replaced personal absolute paths with environment-based workspace contracts, removed a broken absolute symlink and an empty path-artifact file, and removed an empty tracked telemetry database. Runtime data is now excluded from Git.

The SISO-owned Hub and bundled SISO skills carry the repository-root MIT license. A promoted or externally sourced skill keeps its own ownership and license receipt; the Hub license never overrides upstream rights.

The 2026-07-30 task-state reconciliation replaced Task Manager and PM Tasks database ownership with Agent Brain adapters, removed Task Commander raw-SQL and topology assumptions, and moved skill-health events to the Skills-owned `SISO_SKILLS_TELEMETRY_DB`. The mixed `os-database` folder remains preserved only as reviewed legacy import source; its consumer inventory is `registry/legacy-task-consumers.json`.
