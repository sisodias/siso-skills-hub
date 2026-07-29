# Security

Never place provider keys, tokens, cookies, credentials, private keys, or personal machine paths in a skill, fixture, registry entry, pipeline, or generated index.

Provider credentials are injected at runtime through named environment variables. Example files contain empty placeholders only.

If a credential is committed:

1. Revoke or rotate it at the provider immediately.
2. Remove it from current source.
3. Purge it from every reachable Git ref.
4. Force-publish the cleaned history with an exact lease.
5. Assume forks, caches, logs, and old clones may still contain it.
6. Record the incident without copying the secret into reports.
