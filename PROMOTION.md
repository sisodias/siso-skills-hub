# Skill repository promotion

The Hub supports two useful fork sizes without making thousands of Git submodules part of normal operation.

## Before promotion: bundled skill

A new or tightly coupled skill lives at:

```text
registry/skills/<category>/<skill-id>/
```

It is versioned with the Hub and can be installed, linked, searched, validated, and composed into pipelines. This is the cheapest home while the capability is still changing with the catalog.

## Promotion gate

Promote a skill to its own repository when at least one is true:

- people need to fork or adopt it without the Hub;
- it needs releases, maintainers, permissions, or security response independent from the Hub;
- multiple playbooks or products consume it on their own schedules;
- its tests, fixtures, or dependencies have become a coherent product surface;
- its size or change rate makes bundled review materially worse.

A folder name alone is not a promotion reason.

## Current catalog assessment

The 2026-07-30 direct-source pass found no immediate repository promotions. That is deliberate: ten entries belong with Playbooks, three are adapters over one task/state system that must be reconciled with Agent Brain, ten are stale environment recipes that need replacement or retirement, four remain cheap bundled capabilities, and Web Search is the first individual-skill candidate after its missing tests, provider abstraction, and adoption evidence exist.

- Human map: [`docs/skill-repository-map.html`](docs/skill-repository-map.html)
- Machine decisions: [`registry/promotion-assessments.json`](registry/promotion-assessments.json)

All decisions are provisional. A new adoption receipt or independent maintainer can change the recommendation without changing the skill's identity.

## After promotion: independent source, pinned catalog entry

The skill repository owns its source, license, tests, releases, and contribution workflow. Its Hub entry records:

```json
{
  "repo_url": "https://github.com/Lordsisodia/<repo>",
  "remote_url": "https://github.com/Lordsisodia/<repo>.git",
  "commit_hash": "<reviewed-full-commit-sha>"
}
```

The Hub may carry a generated source snapshot for whole-catalog offline use. The snapshot is derived from the pinned commit and contains no nested `.git` directory. The CLI checks out the registry pin before materializing it.

## Fork behavior

- Fork the **individual repository** to change, release, or contribute to one promoted skill.
- Fork the **Skills Hub** to curate a whole catalog, dependency graph, pipelines, and a set of pinned skill snapshots.
- Fork the **Great Library** to curate the wider research and agent ecosystem without downloading every payload.

Git submodules are intentionally not the primary mechanism. They make recursive clones, branch updates, permissions, and thousands of independent pointers part of every contributor’s daily workflow. A plain registry of immutable source receipts scales further and remains usable by humans, CLIs, MCP servers, and agents.
