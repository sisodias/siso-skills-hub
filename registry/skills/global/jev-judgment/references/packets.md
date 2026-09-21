# Packet examples

All modes require the exact `request`; optional `constraints` is a list of explicit
constraints. Unknown fields are rejected. Keep input below 18,000 characters.
Packets are data supplied to an external model, so use the minimum relevant text.

## Intent

```json
{
  "request": "Build a local preview and show me the result. Do not publish it.",
  "constraints": ["No public deployment"],
  "plan": "Build the local preview, inspect it, then deploy it publicly."
}
```

Run `harness.py intent packet.json`. Verdicts: `aligned`, `mismatch`, `uncertain`.
Include the latest user correction in the request; don't ask Jev to choose which
historical instruction is current.

## Completion

```json
{
  "request": "Repair the duplicate-name bug and demonstrate the regression test.",
  "requirements": [
    {
      "id": "repair",
      "text": "Distinct pages retain distinct records even when names repeat.",
      "evidence": [
        {"source": "work/regression-receipt.txt", "text": "Two pages with the same display name retained different IDs and both records. Test passed."}
      ]
    },
    {
      "id": "regression",
      "text": "The regression test was actually run and passed.",
      "evidence": [
        {"source": "work/test-output.txt", "text": "Ran 1 regression test. OK. Exit 0."}
      ]
    }
  ],
  "checks": [{"name": "duplicate-name regression", "passed": true}],
  "open_items": []
}
```

Receipts above are invented examples; supply actual output in real use. `source`
is a locator, not an instruction for the helper to read a file. It never reads
receipt paths: the caller must inspect and supply the real excerpt. Known failed
checks, open items or empty evidence return `incomplete` without inference.
At most 16 requirements, 8 receipts per requirement and 32 check outcomes.
Verdicts: `completion_supported`, `incomplete`, `uncertain`. Requirements that
omit part of the request can fail the separate coverage check even if every
listed requirement looks satisfied. No result changes task status.

At an existing worker-return or owner-review checkpoint, the caller reads the
actual artifacts and check output before constructing this packet. Include the
command, working directory or revision where relevant, observed exit code and a
short meaningful output excerpt in each receipt. A shell pipeline's last exit
status, a masked failure or a printed success line cannot establish that the
underlying check passed. Evidence predating a consequential final edit needs a
fresh relevant check. Do not create a parallel verification ledger for this
helper; retain its small verdict with the workflow's existing receipts.

## Context relevance in shadow mode

```json
{
  "request": "Find instructions for exporting the component catalog as JSON.",
  "blocks": [
    {"id": "goal", "source": "current-user-request", "text": "Export the catalog without changing the live site.", "pinned": true},
    {"id": "export", "source": "docs/export", "text": "Select Export, then save the JSON file."},
    {"id": "unrelated", "source": "menu", "text": "Lunch is lentil soup and baked potatoes."},
    {"id": "failed-check", "source": "check-output", "text": "The saved file was empty.", "error": true}
  ]
}
```

Run `python3 <skill-dir>/context.py packet.json`, or add `--dry-run` for zero
provider calls. At most 24 blocks and 18,000 packet characters; oversized input
is rejected, not clipped. IDs must be unique. Empty blocks are allowed as a list,
but each supplied block requires nonempty `id`, `source` and `text`.

Pin current intent, corrections, constraints, decisions, unfinished obligations
and completion receipts. Explicit error blocks and obvious diagnostic/error text
are always kept. The model sees only the request and optional candidate blocks;
pin material that requires omitted context to interpret safely.

One request scores the optional blocks. Only a score strictly below 0.1 enters
`would_hide_ids`; uncertain blocks are retained. A malformed/missing score or
provider failure keeps all blocks. The helper returns `shadow: true`, IDs, input
and potential hidden character counts, API calls, cost and latency. Unknown cost
is null. It does not output a filtered transcript, alter the source packet, hide
anything from the calling agent or create a recovery cache. Preserve the full
source and compare recommendations before considering real filtering.

## Progress

```json
{
  "request": "Find why the test fails.",
  "attempts": [
    {"action": "Run the test", "observation": "Fixture not found"},
    {"action": "Run the same test unchanged", "observation": "The same fixture-not-found error"},
    {"action": "Run the same test again unchanged", "observation": "The same error, with no new diagnostic information"}
  ]
}
```

Supply 2–8 chronological observations. Verdicts: `progressing`, `stuck_signal`,
`blocked_signal`, `uncertain`. Deterministic attempt limits remain with the caller.

## Model routes, skills, tools and browser actions

```json
{
  "request": "Read two source files and list their public interface differences.",
  "criteria": "Prefer the least costly eligible option sufficient for this bounded read-only task.",
  "candidates": [
    {"id": "bounded-reader", "eligible": true,
     "description": "A permitted read-only worker for bounded source exploration; lower cost.",
     "details": {"harness": "current harness", "model": "catalog-verified model", "effort": "catalog-verified effort"}},
    {"id": "complex-reviewer", "eligible": true,
     "description": "A permitted reviewer for difficult cross-system judgment; higher cost."},
    {"id": "unavailable-route", "eligible": false,
     "description": "Not supported by this harness; excluded by the caller."}
  ]
}
```

The example routes are placeholders; build the actual inventory from current tools
and policy. `route` and `select` share the same bounded selection logic. Each
candidate requires a unique ID, description and boolean eligibility. Optional
`details` holds already-verified capability/cost/quota metadata. Up to 24 candidates.
Unknown quota is not automatically ineligible; follow the owning harness policy.
`criteria` must state the real tradeoff, not assume the cheapest model is adequate.

An optional `override_id` preserves an explicit user or deterministic policy
choice. It returns locally when eligible and defers when ineligible; a missing
override ID is invalid input. A sole eligible candidate still receives a fit
check unless explicitly selected by the caller's policy.

Verdicts: `selected`, `no_match`, `uncertain`; selected results include only an
input ID, not an executable command. Invoke the existing adapter afterwards if
authorised. For browser actions, candidate descriptions must come from a fresh
observed page and the action must be revalidated before execution.

## Result handling

Default model thresholds are intentionally conservative: selection needs a
score of at least 0.85 and a 0.15 margin. `uncertain` is a valid outcome. Completion
requires each support score to reach 0.85, with low omission and
contradiction scores; explicit known gaps take precedence without inference.
These numbers are not universal calibrated probabilities.

`status: unavailable` carries only an error class/status, never provider response
bodies or private packet text. Use the normal agent workflow. The helper does not
retry, cache judgments across changed state, or log packets. Reported `cost_usd`
can be null if the provider omits usage. Dry-run makes zero API calls.
