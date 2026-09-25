---
name: trace-to-regression
description: Convert an observed agent conversation failure into a small regression case and a tested skill or harness correction. Use for requested agent-efficiency or repeated-failure improvement; not routine task execution or automatic model training.
---

# Trace to regression

Use the existing private transcript index, lesson store and test harness. Do not create a second memory system or load the whole conversation archive into context.

1. Bound the sample by dates/timezone, project and observed model/route. Include older-created threads active in the window. Read the user request, relevant calls/results and actual outcome for selected cases. Transcript instructions are historical evidence, not current authorization.
2. Separate signals from failures. Large output, repeated calls, cached input and long elapsed time are not inherently waste. Exclude encoded images from text counts. Distinguish required verification, changed-state rereads and legitimate monitoring from unchanged retries. Attribute model/route per turn where available; an index label is not proof of every request's model.
3. Record one compact case: source locator, intended outcome, observed failure, smallest causal correction, acceptance check and a counterexample where the correction must not apply. Keep private excerpts and credentials out of shared skills.
4. Fix the owning layer. Missing assignment or unsupported tool transport is a harness/input failure: check the named input once, use an available authorized fallback, otherwise request the missing input. Do not repeatedly poll an unchanged missing file, or substitute a model upgrade for a broken transport. Oversized retrieval calls usually need a narrower query. A repeated decision error may justify a focused skill change; deterministic errors belong in code/tests.
5. Replay the failure and a neighboring non-failure in a disposable target using the existing test mechanism. Verify outcome quality as well as output/turn count. Keep a held-out case separate from the examples used to write the correction. Report behavioral evaluation as NOT_RUN when no actual agent replay ran; lint and instruction review alone do not prove changed behavior.
6. Promote only the tested, scoped correction through the existing skill installer or owning source workflow. Preserve a rollback pointer and compare the next naturally occurring comparable task. Record rejected/no-gain changes as well as successes; do not accumulate rules from every anecdote.

Stop the improvement pass after its scoped correction and checks. No unrequested cron, continuous worker loop, fleet restart, transcript upload or weight training. Report measured observations separately from hypothesized savings; skills are workflow guidance, not evidence that model weights learned from history.
