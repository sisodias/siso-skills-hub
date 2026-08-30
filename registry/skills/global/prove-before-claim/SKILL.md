---
name: prove-before-claim
description: Require a falsifying probe before making a verifiable system claim or accepting an unverified success report.
version: 1.0.0
tags: [verification, evidence, claims, safety]
---
**Purpose:** Gate the moment an agent is about to emit a diagnostic hedge about a verifiable system fact. Run the proof first; emit the claim after.

## When to load
- About to write "probably", "likely", "I suspect", "might be", "presumably" about a live fact (file, process, platform, config, network state)
- About to write "I think we already X" about something searchable on disk or in a log
- Just received a "it worked" / "it's live" / "it's captured" self-report from a sub-agent or external system
- About to enumerate hypotheses for why something might be broken

Do NOT load for: stylistic/product-direction uncertainty, design trade-offs, or genuinely unknowable future states.

## The loop (run it, don't skip it)

**Step 1 — State the claim.**
Write the full sentence you were about to emit.

**Step 2 — Identify the falsifying command.**
What one bash command, tool call, or API query would prove or falsify the claim?
Use the probe library below. If no probe exists → the claim is genuinely uncertain → emit "UNVERIFIED: [why]" not a confident hedge.

**Step 3 — Run it first, emit after.**
Do NOT emit the claim before you have the result.
Format: `[Command output]. Therefore: [claim with evidence].`
Never: `[Claim]. (Let me verify.)` — that is wrong order.

## Proof templates (Oracle / SISO JARVIS contexts)

| Claim type | Probe |
|---|---|
| "Cookies are probably at path X" | `for p in ~/Library/**/Cookies(N) ~/.config/**/Cookies(N); do print -r -- "$p"; done` |
| "OBS is probably running" | `pgrep -x obs && echo running \|\| echo not_running` |
| "OBS config probably has the target" | `cat ~/.config/obs-studio/plugin_config/obs-multi-rtmp/targets.json` |
| "Platform is probably live" | `node scripts/oracle-public-proof.mjs --platform X` |
| "Convex probably has the captured events" | `npx convex run controlPlane:readState` |
| "Process is probably dead/alive" | `pgrep -af 'oracle|claude|codex'` |
| "Chrome tab is probably open" | `osascript -e 'tell app "Google Chrome" to get URL of tabs of windows'` |
| "Sub-agent probably finished" | `for p in /tmp/oracle-*.log(N); do stat -f '%m %z %N' "$p"; done \| sort -nr \| head -5` |
| "Code probably contains symbol X" | Serena `query_project` → `find_symbol` or `search_for_pattern` |
| "Known non-code file contains X" | `awk 'index($0, "X") { print NR ":" $0; if (++n == 10) exit }' <file>` |
| "SSH config probably forces something" | `awk '/^Host / {show=6} show>0 {print; show--}' ~/.ssh/config \| head -30` |
| "Process is probably using port X" | `lsof -i :X \| head -5` |
| "Module is probably installed" | `node -e "require('X'); console.log('ok')" 2>&1` |
| "Sub-agent report claims X worked" | Read the external truth: platform API or output file, NOT the report |

## Output contract

Return ONE of:
- `[Evidence from probe]. Therefore: [claim].` — verified
- `UNVERIFIED: [specific reason no probe exists]` — explicitly uncertain
- Never: a hedge masquerading as a conclusion

## The "speaks-the-old-contract" check (before calling a schema/API/format change SAFE)

Distinct from the verifiable-fact loop above: this fires the moment you are about to call a **change** safe/done — specifically a change to a **shape** (a Convex schema, an event payload, an IPC message, an API response, a stored-data format, a config key). A passing build + green types proves the NEW code is internally consistent; it does NOT prove nothing still speaks the OLD shape.

**Before claiming such a change safe, enumerate every consumer still on the old contract and confirm none break:**
- A **deployed/running instance** built against the old schema (an already-live Convex deployment, a long-running Electron session, a soak still in flight) meeting your new shape.
- **Clients still sending the old payload** — an extension/connector/worker that emits the previous event shape your new reader no longer accepts.
- A **cache / persisted store holding the prior value** — localStorage mirror, a stored `result.state`, a partition file written in the old format.
- The **downstream consumer of the thing you changed** — who reads the field you renamed/removed, in code you didn't touch this change.

If you can't name each one and show it's handled (back-compat shim, migration, dual-read, or confirmed-unused), the change is **UNVERIFIED-SAFE**, not safe. This is a known Oracle scar surface: Convex `applyEventBatch` / incremental ingest, the platform-alias lookup, and per-platform readback payloads have all drifted shape silently. Code-internal consistency ≠ contract compatibility.

## Scope guard
This skill is about VERIFIABLE FACTS. Do not apply to:
- Design decisions ("probably the right architecture is...")
- Product/business trade-offs  
- Explicit "I don't know" statements about unknowable things
- Predictions about external users/platforms where no oracle exists

The test: "Could I prove or falsify this in 30 seconds with a terminal?" If yes → run it.

## Why this is a skill, not just a rule
The CLAUDE.md rule states the policy. This skill provides:
1. A repeatable 3-step procedure anchored to the moment of claim generation
2. A probe library for the 12 most common Oracle/SISO claim types
3. The output contract — so the agent knows exactly what shape to return
4. The scope guard — so it doesn't over-apply and become noise

Rules change behavior; skills change the execution loop.
