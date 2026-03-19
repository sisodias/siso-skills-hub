#!/usr/bin/env python3
"""
Skills Strategist — scores skill candidates against agents to determine best fit.
Run: python3 skills_strategist.py [--json]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

HUB_ROOT = Path(__file__).parent.parent
REGISTRY_FILE = HUB_ROOT / "registry" / "skills_registry.json"
CANDIDATES_DIR = HUB_ROOT / "backlog" / "candidates"
PLACEMENTS_DIR = HUB_ROOT / "backlog" / "placements"


def load_registry():
    """Load skill registry."""
    if not REGISTRY_FILE.exists():
        return {"skills": []}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def load_candidates():
    """Load all candidate JSON files from backlog/candidates/."""
    candidates = []
    if not CANDIDATES_DIR.exists():
        return candidates

    for f in sorted(CANDIDATES_DIR.iterdir()):
        if f.suffix == '.json' and f.name != 'README.md':
            try:
                with open(f) as fp:
                    data = json.load(fp)
                    data['_source_file'] = f.name
                    candidates.append(data)
            except json.JSONDecodeError as e:
                print(f"Warning: Invalid JSON in {f.name}: {e}", file=sys.stderr)
    return candidates


def get_agents():
    """Get agent inventory from skills agents --json."""
    try:
        result = subprocess.run(
            [sys.executable, str(HUB_ROOT / "scripts" / "skills"), "agents", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Warning: agents command failed: {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Warning: Could not get agents: {e}", file=sys.stderr)
        return []


def parse_agent_skills(agents_data):
    """Parse agent skill inventory into a structured format."""
    agents = {}
    for agent in agents_data:
        name = agent.get('name', 'unknown')
        full_skills = []
        bare_skills = []

        for s in agent.get('full_skills', []):
            skill_id = s.split(' [')[0]
            full_skills.append(skill_id)

        for s in agent.get('bare_skills', []):
            skill_id = s.split(' [')[0]
            bare_skills.append(skill_id)

        all_skills = set(full_skills + bare_skills)
        agents[name] = {
            'full_skills': full_skills,
            'bare_skills': bare_skills,
            'all_skills': all_skills,
        }
    return agents


def get_category_tags(registry):
    """Build mapping of skill categories and tags."""
    skill_info = {}
    for skill in registry.get('skills', []):
        sid = skill.get('skill_id')
        if sid:
            skill_info[sid] = {
                'category': skill.get('category', 'unknown'),
                'tags': set(skill.get('tags', [])),
            }
    return skill_info


def score_candidate(candidate, agents, skill_info, registry_skills):
    """Score a candidate against all agents. Returns dict of agent -> score."""
    # Extract candidate attributes
    name = candidate.get('name', candidate.get('skill_id', 'unknown'))
    description = candidate.get('description', '').lower()
    use_case = candidate.get('use_case', '').lower()
    category = candidate.get('category', '').lower()
    tags = set(candidate.get('tags', []))
    target_agent = candidate.get('target_agent', '')

    # Build registry skill set
    registry_skill_ids = set(registry_skills.keys())

    scores = {}
    for agent_name, agent_data in agents.items():
        score = 0
        reasons = []

        # 1. Target agent match (highest priority)
        if target_agent and agent_name.lower() == target_agent.lower():
            score += 100
            reasons.append(f"target_agent match")

        # 2. Explicit skill match in target_agent field
        elif target_agent and target_agent.lower() in [s.lower() for s in agent_data['all_skills']]:
            score += 50
            reasons.append(f"target_agent has requested skill")

        # 3. Category alignment - agent already has skills in same category
        if category:
            agent_skill_ids = agent_data['all_skills']
            matching_category = 0
            for sid in agent_skill_ids:
                if sid in skill_info and skill_info[sid].get('category', '').lower() == category.lower():
                    matching_category += 1
            if matching_category > 0:
                score += matching_category * 10
                reasons.append(f"{matching_category} skills in same category '{category}'")

        # 4. Tag overlap with existing skills
        if tags:
            agent_skill_ids = agent_data['all_skills']
            matching_tags = 0
            for sid in agent_skill_ids:
                if sid in skill_info:
                    overlap = len(tags & skill_info[sid].get('tags', set()))
                    matching_tags += overlap
            if matching_tags > 0:
                score += matching_tags * 5
                reasons.append(f"{matching_tags} tag matches")

        # 5. Skill gap analysis - agent needs this skill
        # Check if agent is missing a commonly needed skill
        # This is a simple heuristic: skills used by many agents are "core"
        if name in registry_skill_ids:
            # Check how many other agents have this
            agent_count = sum(1 for a in agents.values() if name in a['all_skills'])
            total_agents = len(agents)
            penetration = agent_count / total_agents if total_agents > 0 else 0

            # Low penetration = high value for agent that doesn't have it
            if name not in agent_data['all_skills']:
                if penetration < 0.3:
                    score += 25
                    reasons.append(f"rare skill ({agent_count}/{total_agents} agents)")
                elif penetration < 0.6:
                    score += 15
                    reasons.append(f"moderate skill ({agent_count}/{total_agents} agents)")

        # 6. Description keyword matching
        keywords_map = {
            'git': ['git', 'github', 'repo', 'commit'],
            'search': ['search', 'find', 'lookup', 'query'],
            'web': ['web', 'http', 'fetch', 'url'],
            'database': ['database', 'db', 'sql', 'storage'],
            'pm': ['task', 'project', 'manage', 'plan'],
            'code': ['code', 'build', 'compile', 'implement'],
            'test': ['test', 'verify', 'qa', 'validate'],
        }

        for skill_key, keywords in keywords_map.items():
            if any(kw in description or kw in use_case for kw in keywords):
                if skill_key in agent_data['all_skills']:
                    score += 8
                    reasons.append(f"has related skill '{skill_key}'")

        # 7. Bonus for empty agents (new agents need skills too)
        if len(agent_data['all_skills']) == 0:
            score += 5
            reasons.append("agent has no skills yet")

        # 8. Penalty for agents that already have this exact skill
        if name in agent_data['all_skills']:
            score -= 50
            reasons.append("agent already has this skill")

        scores[agent_name] = {
            'score': score,
            'reasons': reasons,
        }

    return scores


def rank_candidates(candidates, agents, skill_info, registry_skills):
    """Rank all candidates against all agents."""
    results = []

    for candidate in candidates:
        name = candidate.get('name', candidate.get('skill_id', 'unknown'))
        source = candidate.get('_source_file', 'unknown')

        scores = score_candidate(candidate, agents, skill_info, registry_skills)

        # Get top agents
        ranked = sorted(scores.items(), key=lambda x: -x[1]['score'])
        top_agents = [
            {
                'agent': agent,
                'score': data['score'],
                'reasons': data['reasons'][:3],
            }
            for agent, data in ranked[:3] if data['score'] > 0
        ]

        results.append({
            'candidate': name,
            'source': source,
            'description': candidate.get('description', ''),
            'category': candidate.get('category', 'unknown'),
            'priority': candidate.get('priority', 'medium'),
            'recommended_agents': top_agents,
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Skills Strategist - Score candidates for agents")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--candidate", type=str, help="Specific candidate file to analyze")
    args = parser.parse_args()

    # Load data
    registry = load_registry()
    candidates = load_candidates()

    if args.candidate:
        # Filter to specific candidate
        candidates = [c for c in candidates if c.get('_source_file') == args.candidate]
        if not candidates:
            print(f"Candidate {args.candidate} not found")
            return 1

    agents_data = get_agents()
    if not agents_data:
        print("Warning: No agents data found", file=sys.stderr)
        return 1

    agents = parse_agent_skills(agents_data)
    skill_info = get_category_tags(registry)
    registry_skills = {s['skill_id']: s for s in registry.get('skills', [])}

    # Rank candidates
    results = rank_candidates(candidates, agents, skill_info, registry_skills)

    # Always write placements to backlog/placements/ for the integrator
    # Flatten to integrator's expected format: {skill_id, agent, score, category}
    if results:
        PLACEMENTS_DIR.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        flat_placements = []
        for r in results:
            for ra in r.get("recommended_agents", []):
                flat_placements.append({
                    "skill_id": r["candidate"].lower().replace(" ", "_"),
                    "agent": ra["agent"],
                    "score": ra["score"],
                    "category": r.get("category", "unknown"),
                    "priority": r.get("priority", "medium"),
                })
        out_file = PLACEMENTS_DIR / f"placements_{ts}.json"
        with open(out_file, 'w') as f:
            json.dump(flat_placements, f, indent=2)

    if args.json:
        print(json.dumps({
            'candidates_count': len(candidates),
            'agents_count': len(agents),
            'results': results,
        }, indent=2))
        return 0

    # Human-readable output
    print(f"# Skills Strategist Report")
    print(f"Candidates: {len(candidates)} | Agents: {len(agents)}")
    print()

    if not results:
        print("No candidates found in backlog/candidates/")
        print("Add JSON files with skill requests to enable scoring.")
        return 0

    for r in results:
        print(f"## {r['candidate']}")
        print(f"   Category: {r['category']} | Priority: {r['priority']}")
        print(f"   Description: {r['description'][:80]}..." if len(r['description']) > 80 else f"   Description: {r['description']}")
        print()

        if r['recommended_agents']:
            print("   Top agents:")
            for i, rec in enumerate(r['recommended_agents'], 1):
                reasons_str = ", ".join(rec['reasons']) if rec['reasons'] else "no specific reasons"
                print(f"   {i}. {rec['agent']} (score: {rec['score']}) - {reasons_str}")
        else:
            print("   No strong agent matches found")
        print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
