---
name: publish
description: Publish a reviewed static directory or self-contained HTML file to an explicitly authorized public Cloudflare Pages project and append an exact delivery receipt to the caller's handoff. Not for private client pages or server apps.
---

# Publish one static surface

Use the caller's requested project and public audience. Do not infer permission
to publish private/client content, create a new audience, or replace another site.
Private pages require a separately verified access-controlled workflow; stop here.

1. Read the caller's source and publication boundary. Run its build, tests and
   publication scan. Upload only the generated static directory, never the repo.
   Use a heap cap and, on constrained machines, an owned-process-group RSS guard.
2. Reuse the caller's pinned Wrangler. If absent, pin a reviewed version locally.
   Verify the existing Cloudflare project with `wrangler pages project list`.
   Create a project only when authorized; the helper does not create one for you.
3. For SISO reading pages, use the pinned `siso-shell` package at build time:
   render `rail(...)`, copy its assets as derived output, and load them once.
   Keep content and destinations with the consumer; never inject a guessed nav.
4. Run the helper with `--dry-run`, then without it:

```bash
node scripts/publish.mjs --input /absolute/public-output --project chosen-project \
  --branch main --handoff /absolute/private-handoff.md \
  --wrangler /absolute/project/node_modules/wrangler/bin/wrangler.js --public --dry-run
```

The helper stages an immutable upload copy, rejects symlinks, hidden/source files,
common secrets and local paths, and applies Pages size/count bounds. This is a
mechanical backstop, not a substitute for reading and rights/privacy review.
An HTML input must be self-contained; use a directory for local assets.

After deployment it requires HTTP 200 and an exact root-HTML hash match at the
returned deployment URL before appending the URL and artifact digest to the
handoff. A deployment may have succeeded even if readback/writeback fails: retain
the printed URL, inspect that deployment, and do not blindly deploy again.

Verify the caller's required deep links and interactions, then deliver that exact
URL. Do not claim the stable alias changed merely because a preview URL works.
Never echo credentials. Never weaken a failed safety gate to make publication pass.
