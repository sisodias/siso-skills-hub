#!/usr/bin/env python3
"""
Skill self-analysis: error clustering, failure reports, auto-degradation.
"""
import sqlite3, os, json
from pathlib import Path
from collections import defaultdict
from datetime import datetime, timedelta

DB_PATH = Path(os.environ.get("SISO_SYSTEM_DB", str(Path.home() / ".SystemDB" / "sisostem.db")))
REGISTRY_FILE = Path(__file__).parent.parent / "registry" / "skills_registry.json"


def get_db():
    """Get database connection, creating tables if needed."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
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
    conn.execute("CREATE INDEX IF NOT EXISTS idx_skill_id ON skill_events(skill_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON skill_events(timestamp)")
    return conn


def get_error_profile(skill_id, days=30):
    """Get error breakdown for a skill."""
    conn = get_db()
    cutoff = datetime.now().timestamp() - (days * 86400)

    rows = conn.execute("""
        SELECT error_type, COUNT(*) as count
        FROM skill_events
        WHERE skill_id = ? AND timestamp > ? AND success = 0
        GROUP BY error_type
        ORDER BY count DESC
    """, (skill_id, cutoff)).fetchall()

    total = conn.execute("""
        SELECT COUNT(*) FROM skill_events
        WHERE skill_id = ? AND timestamp > ?
    """, (skill_id, cutoff)).fetchone()[0] or 1

    error_rows = conn.execute("""
        SELECT COUNT(*) FROM skill_events
        WHERE skill_id = ? AND timestamp > ? AND success = 0
    """, (skill_id, cutoff)).fetchone()[0]

    conn.close()

    error_rate = error_rows / total if total > 0 else 0

    return {
        "skill_id": skill_id,
        "total_invocations": total,
        "error_count": error_rows,
        "error_rate": round(error_rate, 3),
        "is_degraded": error_rate > 0.20,
        "top_errors": [{"type": r[0] or "unknown", "count": r[1]} for r in rows[:5]],
        "period_days": days
    }


def get_retry_stats(skill_id, days=30):
    """Get retry/repeat invocation stats."""
    conn = sqlite3.connect(DB_PATH)
    cutoff = datetime.now().timestamp() - (days * 86400)

    # Skills invoked multiple times by same agent in short window (potential retries)
    rows = conn.execute("""
        SELECT skill_id, agent_id, COUNT(*) as cnt
        FROM skill_events
        WHERE timestamp > ? AND skill_id = ?
        GROUP BY skill_id, agent_id
        HAVING cnt > 1
    """, (cutoff, skill_id)).fetchall()

    conn.close()
    return {"repeat_invocations": sum(r[2] for r in rows), "retrying_agents": len(rows)}


def generate_report(skill_id, days=30):
    """Generate a diagnosis report for a skill."""
    profile = get_error_profile(skill_id, days)
    retries = get_retry_stats(skill_id, days)

    report = f"""# Diagnosis Report: {skill_id}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Period:** Last {days} days
**Status:** {"DEGRADED" if profile['is_degraded'] else "HEALTHY"}

## Overview

| Metric | Value |
|--------|-------|
| Total invocations | {profile['total_invocations']} |
| Errors | {profile['error_count']} |
| Error rate | {profile['error_rate']*100:.1f}% |
| Repeat invocations | {retries['repeat_invocations']} |
| Retrying agents | {retries['retrying_agents']} |

## Top Failure Modes

"""

    if profile['top_errors']:
        for err in profile['top_errors']:
            report += f"- **{err['type']}**: {err['count']} occurrences\n"
    else:
        report += "_No errors recorded in this period._\n"

    report += """
## Recommendations

"""

    if profile['is_degraded']:
        report += f"""WARNING: **Error rate ({profile['error_rate']*100:.1f}%) exceeds 20% threshold.**

Suggested actions:
1. Check dependencies are installed: `brew install gh` for gitsearch
2. Check API keys are set for websearch/xsearch
3. Review error types above for patterns
4. Run: `skills validate {skill_id}` to check structure
"""
    elif profile['error_count'] > 0:
        report += f"""Error rate is acceptable ({profile['error_rate']*100:.1f}%).
Monitor for increases. Run `skills diagnose {skill_id}` weekly.
"""
    else:
        report += "_No issues detected. Skill is performing normally._\n"

    return report, profile


def auto_degrade(skill_id):
    """Set skill status to 'degraded' if error rate > 20%."""
    profile = get_error_profile(skill_id)

    if not profile['is_degraded']:
        return False

    with open(REGISTRY_FILE) as f:
        registry = json.load(f)

    for skill in registry['skills']:
        if skill['skill_id'] == skill_id:
            old_status = skill.get('metadata', {}).get('status', 'unknown')
            if old_status != 'degraded':
                skill.setdefault('metadata', {})['status'] = 'degraded'
                with open(REGISTRY_FILE, 'w') as f:
                    json.dump(registry, f, indent=2)
                return True
    return False
