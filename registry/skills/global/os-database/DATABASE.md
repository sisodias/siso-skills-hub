# Database ownership

This skill operates on the database selected by `SISO_SYSTEM_DB`. No machine-specific database is linked into the skill source.

`schema.sql` is a compact human reference, while migrations and scripts hold executable behavior. Runtime databases, WAL files, agent-specific configuration, and state belong outside Git.
