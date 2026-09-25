---
name: classify-by-reading
description: Classify files from their content before assigning consequential current/stale/dead/duplicate/archive verdicts.
version: 1.0.0
tags: [safety, classification, cleanup, evidence]
---
# Classify by reading, not by proxy

## When this fires
Any task where you will label files and then ACT on the label — archive, delete, supersede, dedup, "mark stale," "remove dead code," "consolidate docs." The moment a verdict drives a destructive or hard-to-reverse action, this skill applies.

## The failure this prevents (real, recurring)
A doc-canon consolidation marked `CONNECTOR-ARCHITECTURE.md` STALE because a grep found 5 incidental "BongaCams"/"CDP" mentions. On an actual read it was the **current** connector architecture spec (live normalized event union, the readback supervisor). It got orphaned. Earlier in the same task, archiving a stale *catalog* (DOCS-CANON) silently removed the only discovery path to ~10 current runbooks. Both failures share one root: **a verdict was assigned from a proxy (grep / filename / mtime / "nothing links it") instead of from the content.** The lesson recurred 3× in one session even though it was already written in a lessons file — which is why it's now a hard rule in global CLAUDE.md plus this skill.

## The rule
Before you write `current` / `stale` / `dead` / `duplicate` / `superseded` / `safe-to-archive` / `safe-to-delete` next to a file:

1. **Open it. Read enough to judge on content.** Not the filename, not the mtime, not a keyword count, not "nothing references it."
2. **Proxies are signals to investigate, never verdicts.** "Old mtime," "matches `bongacams`," "not in the active dir," "no inbound links" → all mean *go look*, not *it's dead*.
3. **Distrust your own grep.** Keyword counts contradict each other depending on the keyword set (the same file scored live:31 and live:2 on two different greps). If two proxies disagree, that's not noise to average — it's a signal to READ.
4. **A few incidental mentions of dead scope ≠ a dead doc.** Judge the doc's *primary subject and whether it describes how the system works NOW*, not whether a banned word appears.
5. **If you cannot read it, label it `UNVERIFIED` — never `dead`.** And don't take destructive action on an UNVERIFIED file.
6. **Preserve over destroy when unsure.** Archiving/moving (recoverable) beats deleting. But even archiving needs the read — archiving a current doc strands it.

## Sweep procedure (when classifying N files)
- Don't batch-verdict from a listing. For each file: read → judge → record `verdict + one-line evidence` (the evidence is a content fact, e.g. "describes live event union + supervisor," not "mtime 05-28").
- For LARGE sets, delegate the *reading* to a sub-agent (Haiku/Sonnet) one batch at a time with the instruction "judge by reading content, return verdict + content-evidence per file" — but the sub-agent must still read, not grep. Then spot-verify 2-3 of its CURRENT and 2-3 of its STALE calls yourself by reading.
- When you remove a *catalog/index/map* file, first check what it pointed AT — those pointers may be the only discovery path to live files. Rehome the still-valid ones.
- After the sweep, run an **independent adversarial re-check** (a fresh sub-agent, ideally a different model) tasked specifically with "find what the first pass mislabeled or stranded." The first pass's misclassifications are exactly what it's blind to.

## Done criterion
Every verdict traces to a content fact you (or a reader sub-agent) actually read, not to a proxy. Any file you couldn't read is `UNVERIFIED` and was not destroyed. An independent re-check found no stranded current file and no misclassification.
