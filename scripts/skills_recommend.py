import sqlite3, os
from pathlib import Path
from collections import defaultdict
import time

DB_PATH = Path(os.environ.get("SISO_SYSTEM_DB", str(Path.home() / ".SystemDB" / "sisostem.db")))

def get_coinvocations(window_minutes=30, min_count=2):
    """Build co-invocation matrix from skill_events.
    Returns: dict[skill_id, list of (co_skill_id, count, probability)]
    """
    conn = sqlite3.connect(DB_PATH)

    # Get all skill events within sessions, ordered by time
    rows = conn.execute("""
        SELECT skill_id, session_id, timestamp
        FROM skill_events
        WHERE session_id IS NOT NULL
        ORDER BY session_id, timestamp
    """).fetchall()
    conn.close()

    # Build session skill sets
    session_skills = defaultdict(set)
    for skill_id, session_id, ts in rows:
        session_skills[session_id].add(skill_id)

    # Build co-occurrence counts
    co_counts = defaultdict(lambda: defaultdict(int))
    skill_counts = defaultdict(int)

    for session_id, skills in session_skills.items():
        skills = list(skills)
        for i, s1 in enumerate(skills):
            skill_counts[s1] += 1
            for s2 in skills[i+1:]:
                co_counts[s1][s2] += 1
                co_counts[s2][s1] += 1

    # Build P(B|A) matrix
    recommendations = {}
    for s1, cocounts in co_counts.items():
        recs = []
        for s2, cnt in cocounts.items():
            if cnt >= min_count:
                prob = cnt / skill_counts[s1]
                recs.append((s2, cnt, round(prob, 3)))
        recs.sort(key=lambda x: x[2], reverse=True)
        recommendations[s1] = recs

    return recommendations

def recommend(skill_id, top_n=5):
    """Get top N recommended skills given a skill_id."""
    recs = get_coinvocations()
    if skill_id not in recs:
        return []
    return recs[skill_id][:top_n]
