---
name: gls
description: Register reviewed Work, Release, Source Inventory or research-question metadata in the Great Library through its schemas and verification gate. Use for adding Library records, not for publishing private payloads or editing accepted immutable history.
version: 1.0.0
---

# Register in the Great Library

The CLI belongs to the Library, not the Skills Hub. Reviewed source:
[bin/gls at 8f17a5e](https://github.com/sisodias/great-library-of-siso/blob/8f17a5e30322742e827251e55bc9980fe2b51eb8/bin/gls).

Resolve the intended Library checkout, read its `AGENTS.md`, current state and
`site/intelligence.json`, and use that checkout's `bin/gls`. From elsewhere pass
`--root` explicitly. If the CLI is absent, obtain the reviewed public source in
an isolated checkout; do not reset or overwrite an owner's dirty checkout.

Read the input and its source before asserting `--reviewed-public`. Prepare JSON
against the matching existing schema and preserve source identity, rights and
evidence. A question is a research-question Work; an Inventory is staging and
does not become a Work automatically. Check existing question labels as well as
stable UUIDs before allocating an ID. Never fill a known ID collision by silently
overwriting an accepted record.

From the Library root:

```bash
node bin/gls add work --file reviewed-work.json --reviewed-public --dry-run
node bin/gls add work --file reviewed-work.json --reviewed-public
```

Other kinds are `release`, `inventory`, and `question`. Repeat `--file` for a
same-kind batch; `--name` changes the output basename for a single file. Read
`docs/gls.md` for bounds, locking and recovery. Use the machine's existing RSS
guard when constrained. The command runs no dev server and does not push or deploy.

Dry-run success is schema/reference/publication preflight only. A real add runs
the full Library gate. On failure, inspect the reported paths; unexpected edits
are retained, and no accepted file is overwritten. Keep the prepared input until
the change is durably committed.

After success, record an Event and a new Snapshot when selection changes, verify,
commit, push and use `publish` for the generated `site/`. Registration is not an
accepted answer, an installation claim, or execution authority for another owner.
