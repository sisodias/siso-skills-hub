# Runtime data

Skills telemetry databases are runtime state and are not committed to this repository.

Set `SISO_SYSTEM_DB` to the operator-owned SQLite database. Tests must use a disposable path. Registry metadata belongs in `registry/skills_registry.json`; telemetry events do not.
