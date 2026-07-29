# Agent guide

The Skills Hub owns atomic capability discovery, source receipts, installation, dependencies, telemetry adapters, templates, and pipeline references.

- Do not place whole-agent runtimes, Agent Zero, Herdr, Foundry, or composed operating playbooks here.
- Treat `registry/skills_registry.json` as the machine source of truth and regenerate `registry/INDEX.md`.
- A promoted remote skill must be pinned to a reviewed full commit SHA.
- Never commit runtime databases, credentials, personal absolute paths, nested `.git` directories, or broken symlinks.
- Preserve original ownership and licenses for externally sourced skills.
- Use the promotion gate in `PROMOTION.md`; do not create one repository per folder by reflex.

Run `npm test` before pushing.
