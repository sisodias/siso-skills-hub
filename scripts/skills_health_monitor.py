#!/usr/bin/env python3
"""
Skills Health Monitor — reads telemetry, outputs orphan/ghost/degraded/hot/stale skills.
Run: python3 skills_health_monitor.py [--days 30] [--json]
"""
import argparse
import json
import os
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(os.environ.get("SISO_SKILLS_TELEMETRY_DB", str(Path.home() / ".local" / "share" / "siso-skills-hub" / "telemetry.db")))
REGISTRY_FILE = Path(__file__).parent.parent / "registry" / "skills_registry.json"

# Skills that are actually hub CLI commands, not real skills
CLI_COMMANDS = {"list", "search", "info", "install", "validate", "health",
                "depsolve", "recommend", "diagnose", "pipeline", "publish",
                "versions", "update", "agents"}


def get_db():
    """Get DB connection."""
    if not DB_PATH.exists():
        return None
    conn = sqlite3.connect(DB_PATH)
    # Ensure table exists
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skill_events (
            event_id TEXT PRIMARY KEY,
            skill_id TEXT NOT NULL,
            agent_id TEXT,
            session_id TEXT,
            timestamp REAL NOT NULL,
            duration_ms INTEGER,
            success INTEGER NOT NULL DEFAULT 1,
            error_type TEXT,
            context_hash TEXT,
            input_size INTEGER,
            output_size INTEGER
        )
    """)
    return conn


def load_registry():
    """Load skill registry."""
    if not REGISTRY_FILE.exists():
        return {"skills": []}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def get_invoked_skills(conn, days):
    """Get all skills that were actually invoked (excluding CLI commands)."""
    if conn is None:
        return {}
    cutoff = datetime.now().timestamp() - (days * 86400)
    rows = conn.execute("""
        SELECT skill_id, COUNT(*) as cnt,
               SUM(success) as successes,
               COUNT(DISTINCT agent_id) as agents,
               AVG(duration_ms) as avg_ms
        FROM skill_events
        WHERE timestamp > ? AND skill_id NOT IN ({})
        GROUP BY skill_id
    """.format(",".join("?" for _ in CLI_COMMANDS)),
    [cutoff] + list(CLI_COMMANDS)).fetchall()

    invoked = {}
    for row in rows:
        skill_id, count, successes, agents, avg_ms = row
        error_count = count - (successes or 0)
        error_rate = error_count / count if count > 0 else 0
        invoked[skill_id] = {
            "count": count,
            "successes": successes or 0,
            "error_count": error_count,
            "error_rate": round(error_rate, 3),
            "unique_agents": agents or 0,
            "avg_ms": round(avg_ms, 1) if avg_ms else 0,
            "is_degraded": error_rate > 0.20,
            "is_stale": False,
        }
    return invoked


def get_orphan_skills(invoked_skills, registered_skills):
    """Skills invoked but not in registry."""
    orphans = []
    for sid in invoked_skills:
        if sid not in registered_skills:
            info = invoked_skills[sid]
            orphans.append({
                "skill_id": sid,
                "count": info["count"],
                "error_rate": info["error_rate"],
                "unique_agents": info["unique_agents"],
            })
    return sorted(orphans, key=lambda x: -x["count"])


def get_ghost_skills(registered_skills, invoked_skills):
    """Skills registered but never invoked."""
    ghosts = []
    for sid in registered_skills:
        if sid not in invoked_skills:
            ghosts.append({
                "skill_id": sid,
                "category": registered_skills[sid].get("category", "unknown"),
                "status": registered_skills[sid].get("metadata", {}).get("status", "unknown"),
            })
    return sorted(ghosts, key=lambda x: x["skill_id"])


def get_degraded_skills(invoked_skills):
    """Skills with error rate > 20%."""
    degraded = []
    for sid, info in invoked_skills.items():
        if info["is_degraded"]:
            degraded.append({
                "skill_id": sid,
                "error_rate": info["error_rate"],
                "error_count": info["error_count"],
                "count": info["count"],
            })
    return sorted(degraded, key=lambda x: -x["error_rate"])


def get_hot_skills(invoked_skills, top_n=10):
    """Most invoked skills."""
    return sorted(invoked_skills.items(), key=lambda x: -x[1]["count"])[:top_n]


def get_coinvocation_matrix(conn, days):
    """Build co-invocation matrix from session data."""
    if conn is None:
        return {}
    cutoff = datetime.now().timestamp() - (days * 86400)

    # Group by session_id, filter out CLI commands
    rows = conn.execute("""
        SELECT session_id, skill_id FROM skill_events
        WHERE timestamp > ? AND skill_id NOT IN ({})
        ORDER BY session_id, timestamp
    """.format(",".join("?" for _ in CLI_COMMANDS)),
    [cutoff] + list(CLI_COMMANDS)).fetchall()

    session_skills = defaultdict(set)
    for session_id, skill_id in rows:
        session_skills[session_id].add(skill_id)

    # Build co-occurrence matrix
    cooc = defaultdict(lambda: defaultdict(int))
    for skills in session_skills.values():
        skills = list(skills)
        for i, a in enumerate(skills):
            for b in skills[i+1:]:
                cooc[a][b] += 1
                cooc[b][a] += 1

    # Convert to probability P(B|A)
    result = {}
    for a, others in cooc.items():
        total = sum(others.values())
        if total > 0:
            result[a] = {b: round(count/total, 3) for b, count in sorted(others.items(), key=lambda x: -x[1])[:5]}
    return result


def main():
    parser = argparse.ArgumentParser(description="Skills Health Monitor")
    parser.add_argument("--days", type=int, default=30, help="Analysis period (default: 30)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--report", action="store_true", help="Full markdown report")
    args = parser.parse_args()

    days = args.days
    conn = get_db()
    registry = load_registry()

    # Index registered skills
    registered = {s["skill_id"]: s for s in registry.get("skills", [])}

    # Analyze
    invoked = get_invoked_skills(conn, days)
    orphans = get_orphan_skills(invoked, registered)
    ghosts = get_ghost_skills(registered, invoked)
    degraded = get_degraded_skills(invoked)
    hot = get_hot_skills(invoked)
    cooc = get_coinvocation_matrix(conn, days) if conn else {}

    total_events = conn.execute("SELECT COUNT(*) FROM skill_events").fetchone()[0] if conn else 0
    total_sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM skill_events WHERE session_id IS NOT NULL").fetchone()[0] if conn else 0

    if args.json:
        print(json.dumps({
            "period_days": days,
            "total_events": total_events,
            "total_sessions": total_sessions,
            "invoked_skills_count": len(invoked),
            "registered_skills_count": len(registered),
            "orphans": orphans,
            "ghosts": ghosts,
            "degraded": degraded,
            "hot_skills": [{"skill_id": k, **v} for k, v in hot],
            "coinvocation": cooc,
        }, indent=2))
        return 0

    # Markdown report
    print(f"# Skills Health Report — Last {days} days")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Total skill invocations: {total_events} | Sessions: {total_sessions}")
    print(f"Registered skills: {len(registered)} | Actively invoked: {len(invoked)}")
    print()

    # Orphans
    print("## 🔴 Orphans — Invoked but not in registry")
    if orphans:
        print(f"| Skill | Invocations | Error Rate | Agents |")
        print(f"|-------|-------------|------------|--------|")
        for o in orphans:
            print(f"| `{o['skill_id']}` | {o['count']} | {o['error_rate']*100:.0f}% | {o['unique_agents']} |")
    else:
        print("_No orphan skills found._")
    print()

    # Ghosts
    print("## 🟡 Ghosts — Registered but never invoked")
    if ghosts:
        print(f"| Skill | Category | Status |")
        print(f"|-------|----------|--------|")
        for g in ghosts[:20]:
            print(f"| `{g['skill_id']}` | {g['category']} | {g['status']} |")
        if len(ghosts) > 20:
            print(f"_...and {len(ghosts) - 20} more (run with --json for full list)_")
    else:
        print("_No ghost skills found — all registered skills have been invoked!_")
    print()

    # Degraded
    print("## 🔴 Degraded — Error rate > 20%")
    if degraded:
        print(f"| Skill | Error Rate | Errors | Total |")
        print(f"|-------|-------------|--------|-------|")
        for d in degraded:
            print(f"| `{d['skill_id']}` | {d['error_rate']*100:.0f}% | {d['error_count']} | {d['count']} |")
    else:
        print("_No degraded skills found._")
    print()

    # Hot
    print(f"## 🟢 Hot Skills — Top {min(len(hot), 10)} by usage")
    if hot:
        print(f"| Skill | Invocations | Success | Avg MS | Agents |")
        print(f"|-------|-------------|---------|--------|--------|")
        for skill_id, info in hot:
            print(f"| `{skill_id}` | {info['count']} | {info['successes']} | {info['avg_ms']:.0f}ms | {info['unique_agents']} |")
    else:
        print("_No skill invocations recorded yet._")
    print()

    # Co-invocation
    if cooc:
        print("## 🔵 Co-invocations — Skills used together")
        for skill_id, related in sorted(cooc.items())[:10]:
            if related:
                top = ", ".join(f"`{b}` ({p*100:.0f}%)" for b, p in list(related.items())[:3])
                print(f"- `{skill_id}` → {top}")
        print()

    # Recommendations
    print("## 💡 Recommendations")
    recs = []
    if ghosts:
        recs.append(f"**Stage for removal:** {len(ghosts)} skills never used — consider deprecating or promoting.")
    if orphans:
        recs.append(f"**Add to registry:** {len(orphans)} skills invoked but unregistered: {', '.join(o['skill_id'] for o in orphans[:5])}.")
    if degraded:
        recs.append(f"**Fix errors:** {len(degraded)} skills degraded — check dependencies and API keys.")
    if not recs:
        recs.append("System looks healthy. Keep monitoring!")
    for r in recs:
        print(f"- {r}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
