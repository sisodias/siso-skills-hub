# Research and validation

Reviewed 2026-09-21. Jev is a text decision model: supply bounded state and typed
questions; keep execution with ordinary code and the current harness. The pack
uses parallel Noul questions and explicit fallback outcomes. It adds no hook,
provider daemon, scheduler, model inventory or new task/memory store.

## Sources and what was adopted

- [Ricker's Jev Engineering article](https://x.com/0xRicker/status/2101292455391809670)
  argues for bounded state, explicit candidate lists, independent questions in
  one request and code-owned execution. Those patterns informed this pack.
- [Kun Chen's Firstmate dispatch report](https://x.com/kunchenguid/status/2100468943853085061)
  describes matching 25 routing decisions and lower dispatch cost/time. It is an
  author's small evaluation, not evidence that SISO's different routes match.
- [Morty's summary](https://x.com/0xMortyx/status/2101308432305254889) describes
  routing/scoring outside generative reasoning. The headline ratios are not
  expected savings for this installation.
- [Grok's use-case list](https://x.com/grok/status/2101071508567150743) includes
  theoretical speedups and a zero-hallucination assertion. Typed output constrains
  structure, not truth; this pack does not treat a score as action authorisation.
- [TypeSafe System One](https://docs.typesafe.ai/concepts/system-one),
  [citation checking](https://docs.typesafe.ai/cookbooks/citation_check), and
  [skill suggestion](https://docs.typesafe.ai/cookbooks/skill_suggestion)
  supply the primary technical patterns. Missing evidence still needs retrieval
  or inspection; a decision model cannot create it.
- [OpenRouter Jev model page](https://openrouter.ai/typesafe/jev-1.13) listed
  $0.042 per million input tokens and no output-token charge at review time.
  Read actual returned usage; latency, price and model aliases can change.

Original X post/article text was read through a syndication proxy when direct X
access was unavailable. The article's broad compaction and safety claims were
not reproduced. Context relevance remains optional ranking of unpinned excerpts;
automatic memory deletion and tool-approval hooks were not adopted.

## Evidence available before this expansion

The original skill recorded a seven-case failure/control replay with six expected
judgments and one uncertain result. It was a historical report, not rerun here.
A separate 2026-09-21 synthetic FAQ probe using the existing helper produced
10/12 expected results versus 5/12 for a keyword baseline; its two misses were
deferrals. Twelve calls cost $0.000546798, with median latency 562.5 ms. That toy
test does not measure this harness pack or the current generative assistant.

## Verify this pack

From the Skills Hub root, run `python3 scripts/test_jev_harness.py`. It covers
explicit overrides, eligibility, ties, evidence gaps, omitted requirements,
contradictory receipts, invalid API output, unavailable providers, secret-safe
errors and execution from a disposable installed copy. API responses are mocked
in those tests; they establish code behaviour, not model accuracy.

For semantic evaluation, keep task-specific labelled fixtures and at least one
held-out case. Include correct controls as well as drift, partial completion,
unchanged retries and malicious candidate text. Fix demonstrated failures rather
than increasing scope or lowering thresholds until a preferred answer appears.
Record cost and fallbacks alongside accuracy. Use only synthetic or authorised,
minimised content, and cap paid calls before starting.

Live evaluation results and installation receipts are recorded in the consuming
task's handoff; current sessions do not automatically reload skill catalogs.

## 2026-09-21 implementation observations

Twenty-five offline tests passed. The first 12 live synthetic cases matched eight
predeclared verdicts and returned uncertain on four; median API time was 513.5 ms.
An independent four-case agent pass matched two expectations and deferred two.
One of those expectations labelled new diagnostic evidence as a stuck loop, so
that annotation itself was questionable; the recorded expectation was preserved.

A completion prompt correction scoped each question to one requirement's own
receipts and separated missing-request coverage from evidence support. Eight
bounded repeat calls tested that correction, then two fresh independent cases
checked the final version. It withheld completion on a missing deployment and on
a missing human review; clear positive examples still sometimes deferred. This
pack is therefore useful as an advisory discrepancy detector, not an automatic
completion certificate. Thresholds were not lowered to force positive verdicts.

These are 26 harness API calls across synthetic scenarios and prompt revisions,
not a production reliability score. Legacy verify/rank compatibility was also
smoke-tested. End-to-end token, labour and cost savings remain unmeasured.

## Camofox integration, 21 September 2026

The installed pack now has an optional one-step Camofox navigation adapter. Read
[browser packets, measured receipt and limits](browser.md). This uses the
existing local browser service; Chrome/CMUX/Codex browser tools are not intercepted.
The first real-browser fixture passed at $0.000060732 and 3,996 ms for Jev, so
sub-second social-media claims are not reproduced by this run.

## Repository patterns integrated in version 1.3

The repository list in [Pluvio's post](https://x.com/Pluvio9yte/status/2101831273224311035)
was reviewed before choosing these small additions. This pack adapts ideas in its
existing standard-library/OpenRouter implementation; it does not install the
upstream runtimes or imply their direct TypeSafe credentials are interchangeable.

- [jev-ultrafast action loop, reviewed commit](https://github.com/browser-use/jev-ultrafast/blob/1231850a0bf1a0c0341fe408ef1668dbbfdfac46/jev_ultrafast/agent.py):
  bounded action choice, compact state and execution in code informed
  `browser_loop.py`. Caller-supplied fill text replaces a generative typing step;
  observed URL/text checks replace a model's claim to be done.
- [Winnow policy, reviewed commit](https://github.com/GhalebDweikat/winnow/blob/51d80b945c74c8384bc47fa817179f668289afd8/sidecar/src/winnow/policy.py):
  shadow evaluation, conservative retention and error preservation informed
  `context.py`. No resident sidecar, recovery cache, hook or actual deletion was
  needed for this first evaluation surface.
- [Canny verification checks, reviewed commit](https://github.com/qkal/Canny/blob/d927d2606b07ce990fa4bef8908a27d8d32db1e1/src/checks.ts):
  actual verification evidence before completion informed the consuming
  Firstmate returned-work checkpoint. It reuses `harness.py complete`; this pack
  does not copy Canny's hook system or ledger. Evidence gathering remains with
  the existing harness, and a favourable model score never repairs a failed test.

The added offline suites are `scripts/test_jev_browser_loop.py` and
`scripts/test_jev_context.py`. The live search fixture's three actions and readback
passed; its costs and the initial uncertain case are documented in `browser.md`.
A synthetic context call proposed hiding only an unrelated menu (49 of 200 text
characters), kept the export instructions and pinned/error evidence, and left
the original packet unchanged. It reported $0.000020076 and 562 ms. This is a
functional check, not a measured compression or agent-quality improvement.
