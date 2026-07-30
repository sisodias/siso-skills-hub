# Agent guide

The Skills Hub owns atomic capability discovery, source receipts, installation, dependencies, telemetry adapters, templates, and pipeline references.

- Do not place whole-agent runtimes, Agent Zero, Herdr, Foundry, or composed operating playbooks here.
- Treat `registry/skills_registry.json` as the machine source of truth and regenerate `registry/INDEX.md`.
- A promoted remote skill must be pinned to a reviewed full commit SHA.
- Never commit runtime databases, credentials, personal absolute paths, nested `.git` directories, or broken symlinks.
- Preserve original ownership and licenses for externally sourced skills.
- Skills telemetry is a Skills-owned local data concern; it never writes Agent Brain SQLite directly.
- Legacy task adapters call the Agent Brain client; raw SQL and machine-specific task database paths are prohibited outside the preserved `os-database` source folder.
- Use the promotion gate in `PROMOTION.md`; do not create one repository per folder by reflex.

Run `npm test` before pushing.
