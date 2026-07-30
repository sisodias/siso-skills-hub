#!/usr/bin/env python3
"""Render the human promotion map from the machine assessment registry."""

from collections import Counter
from html import escape
import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "skills_registry.json"
ASSESSMENTS = ROOT / "registry" / "promotion-assessments.json"
OUTPUT = ROOT / "docs" / "skill-repository-map.html"

LABELS = {
    "stay_bundled": "Stay bundled",
    "move_to_playbook": "Move to Playbook",
    "reconcile_system_then_keep_adapter": "Reconcile system",
    "retire_or_replace": "Retire / replace",
    "candidate_after_evidence": "Candidate after evidence",
}


def render():
    registry = json.loads(REGISTRY.read_text())
    assessment_data = json.loads(ASSESSMENTS.read_text())
    skills = {entry["skill_id"]: entry for entry in registry["skills"]}
    assessments = assessment_data["assessments"]
    counts = Counter(item["recommendation"] for item in assessments)

    cards = "".join(
        f'<div><b>{counts.get(key, 0)}</b><span>{escape(label)}</span></div>'
        for key, label in LABELS.items()
    )
    rows = []
    for item in assessments:
        skill = skills[item["skill_id"]]
        source = f'../registry/skills/{skill["category"]}/{item["skill_id"]}/SKILL.md'
        blockers = "".join(f"<li>{escape(blocker)}</li>" for blocker in item["blockers"])
        rows.append(
            "<tr>"
            f'<td><a href="{escape(source)}"><b>{escape(item["skill_id"])}</b></a><small>{escape(skill["category"])} · {escape(item["capability_kind"].replace("_", " "))}</small></td>'
            f'<td><span class="tag {escape(item["recommendation"])}">{escape(LABELS[item["recommendation"]])}</span></td>'
            f'<td>{escape(item["target"])}</td>'
            f'<td>{escape(item["reason"])}<details><summary>Promotion blockers</summary><ul>{blockers}</ul></details></td>'
            "</tr>"
        )

    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>SISO Skills — Repository Promotion Map</title>
  <style>
    :root{{--ink:#182033;--muted:#5d6879;--paper:#f4f1e9;--panel:#fff;--line:#d9d5cb;--accent:#087b72;--navy:#13213d}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.58 ui-sans-serif,system-ui,sans-serif}}main{{max-width:92rem;margin:auto;padding:38px 24px}}header,section{{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:clamp(20px,4vw,44px);margin:16px 0}}header{{background:linear-gradient(135deg,#101d37,#19324a);color:#f8fbff}}.eyebrow{{color:#65e0cf;font:700 .74rem ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase}}h1{{font-size:clamp(2.5rem,7vw,5.6rem);line-height:.92;letter-spacing:-.05em;margin:.5rem 0 1.3rem;max-width:12ch}}h2{{line-height:1.1}}.lede{{max-width:73ch;font-size:1.18rem;color:#d7e2ef}}.numbers{{display:grid;grid-template-columns:repeat(5,1fr);gap:9px}}.numbers div{{background:#eef2f3;border-radius:12px;padding:15px}}.numbers b{{display:block;font-size:1.7rem}}.numbers span,small{{display:block;color:var(--muted)}}.flow{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}.node{{padding:9px 13px;border:1px solid var(--line);border-radius:999px;background:#f7f9fa}}.arrow{{color:var(--accent);font-weight:800}}.callout{{border-left:4px solid var(--accent);padding:12px 18px;background:#edf8f6}}table{{border-collapse:collapse;width:100%}}th,td{{padding:12px 10px;border-bottom:1px solid #e3e0d8;text-align:left;vertical-align:top}}th{{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--muted)}}td:nth-child(1){{min-width:170px}}td:nth-child(2){{min-width:175px}}.tag{{display:inline-block;border-radius:999px;padding:4px 8px;font:700 .7rem ui-monospace,monospace;text-transform:uppercase}}.stay_bundled{{background:#e5f2ff;color:#215b88}}.move_to_playbook{{background:#ece8ff;color:#59479a}}.reconcile_system_then_keep_adapter{{background:#fff1d6;color:#8b5500}}.retire_or_replace{{background:#ffe5e8;color:#973544}}.candidate_after_evidence{{background:#ddf8ed;color:#08705f}}details{{margin-top:7px}}summary{{cursor:pointer;color:var(--accent)}}ul{{margin:.4rem 0}}code{{overflow-wrap:anywhere}}footer{{padding:32px 4px;color:var(--muted)}}@media(max-width:72rem){{.numbers{{grid-template-columns:1fr 1fr}}table,tbody,tr,th,td{{display:block}}thead{{display:none}}tr{{padding:14px 0;border-bottom:1px solid var(--line)}}td{{border:0;padding:5px 0}}}}@media(max-width:34rem){{main{{padding:12px}}.numbers{{grid-template-columns:1fr}}}}
  </style>
</head>
<body><main>
  <header>
    <p class="eyebrow">Skills Hub · direct source review · 2026-07-30</p>
    <h1>Fork the right boundary.</h1>
    <p class="lede">The Hub can hold thousands of independently addressable skills without creating thousands of repositories by reflex. A repository is earned by independent adoption, ownership, release cadence, or a coherent executable surface—not by the existence of a folder.</p>
  </header>

  <section>
    <h2>The first assessment</h2>
    <div class="numbers">{cards}</div>
    <p class="callout"><b>Promote now: zero.</b> This is a useful result, not a failure. No current folder proves enough independent adoption and release evidence to justify a repository today. Web Search is the first plausible individual-skill candidate; the task/database family is a system reconciliation problem, not three skill repositories.</p>
  </section>

  <section>
    <h2>Decision flow</h2>
    <div class="flow"><span class="node">Skill folder</span><span class="arrow">→</span><span class="node">read outcome + dependencies + evidence</span><span class="arrow">→</span><span class="node">atomic skill</span><span class="node">playbook</span><span class="node">system adapter</span><span class="node">environment recipe</span><span class="arrow">→</span><span class="node">promote only when the gate is proven</span></div>
    <p>A promoted repository owns source, license, tests, releases, and contribution workflow. The Hub keeps stable skill identity and an immutable source receipt. Composed workflows move to Agent Playbook. Stateful systems join an existing system Work or become a new Work, while the Hub retains only their thin invocation adapter.</p>
  </section>

  <section>
    <h2>All 28 current entries</h2>
    <p>Every verdict below is provisional and evidence-linked, so the map can evolve without rewriting history. Open a row's blockers to see what must become true before its next boundary is accepted.</p>
    <table><thead><tr><th>Entry</th><th>Recommendation</th><th>Target boundary</th><th>Reason and blockers</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
  </section>

  <section>
    <h2>What happens next</h2>
    <ol>
      <li><b>Reconcile the task/state family with Agent Brain.</b> OS Database, Task Manager, and PM Tasks overlap one system outcome and currently lack isolated behavioral proof.</li>
      <li><b>Move compositions to Agent Playbook.</b> Multi-Search, Subagents, story phases, command flows, and pipeline steps should version with the scenarios they compose.</li>
      <li><b>Run Web Search through the promotion gate.</b> Add synthetic transport tests, provider-neutral configuration, citation/error contracts, and actual independent adoption evidence before creating its repository.</li>
    </ol>
    <p>The machine source is <code>registry/promotion-assessments.json</code>. The folder registry remains <code>registry/skills_registry.json</code>. Git submodules remain unnecessary.</p>
  </section>

  <footer>The Great Library of SISO — Built by the SISO Open Source Foundation · Funded by SISO Agency.</footer>
</main></body></html>
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contents = render()
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text() != contents:
            raise SystemExit(f"{OUTPUT.relative_to(ROOT)} is stale; run scripts/build_promotion_map.py")
        print("PROMOTION_MAP_CURRENT")
        return
    OUTPUT.write_text(contents)
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
