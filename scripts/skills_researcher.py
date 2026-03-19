#!/usr/bin/env python3
"""
Skills Researcher — discovers skills from various sources (github, internal, external).
Run: python3 skills_researcher.py --sources github,internal [--query "search term"]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

HUB_ROOT = Path(__file__).parent.parent
REGISTRY_FILE = HUB_ROOT / "registry/skills_registry.json"
WORKSPACE_ROOT = HUB_ROOT.parent.parent


def load_registry():
    """Load the skills registry."""
    if not REGISTRY_FILE.exists():
        return {"skills": []}
    with open(REGISTRY_FILE) as f:
        return json.load(f)


def get_registered_skill_ids():
    """Get set of already registered skill IDs."""
    registry = load_registry()
    return {s["skill_id"] for s in registry.get("skills", [])}


def search_internal_skills(query=None):
    """Search internal codebase for skill-like patterns."""
    findings = []

    # Search for SKILL.md files
    skill_md_patterns = [
        WORKSPACE_ROOT / "**/SKILL.md",
        WORKSPACE_ROOT / "**/.claude/**/SKILL.md",
        WORKSPACE_ROOT / "agents/**/skills/**/SKILL.md",
    ]

    for pattern in skill_md_patterns:
        for skill_file in WORKSPACE_ROOT.glob(str(pattern).replace(str(WORKSPACE_ROOT) + "/", "")):
            # Skip if already in registry
            skill_id = skill_file.parent.name
            if skill_id in get_registered_skill_ids():
                continue

            # Get relative path
            try:
                rel_path = skill_file.relative_to(WORKSPACE_ROOT)
            except ValueError:
                rel_path = skill_file

            # Read description from SKILL.md
            description = ""
            try:
                content = skill_file.read_text()
                # Extract first paragraph as description
                lines = content.strip().split("\n")
                for line in lines[1:]:  # Skip title line
                    if line.strip():
                        description = line.strip()[:100]
                        break
            except Exception:
                pass

            findings.append({
                "source": "internal",
                "skill_id": skill_id,
                "path": str(rel_path),
                "description": description or f"Found SKILL.md at {rel_path.parent}",
                "type": "full_skill",
            })

    # Search for .skill directories or skill-like scripts
    skill_script_patterns = ["**/skills/**/*.py", "**/.skills/**"]

    # Look for common skill script names
    common_skills = ["gitsearch", "websearch", "xsearch", "cli-runner", "github",
                     "playwright", "vercel", "workspace", "task-commander"]

    for skill_name in common_skills:
        # Check if it's already registered
        if skill_name in get_registered_skill_ids():
            continue

        # Search for matching directories/files
        for pattern in skill_script_patterns:
            matches = list(WORKSPACE_ROOT.glob(f"**/{skill_name}/{pattern.split('/')[-1]}"))
            for match in matches:
                if match.exists():
                    try:
                        rel_path = match.relative_to(WORKSPACE_ROOT)
                    except ValueError:
                        rel_path = match

                    # Check if this looks like a valid skill
                    if any(x in str(match) for x in ["/skills/", "/.claude/skills/", "/skill."]):
                        findings.append({
                            "source": "internal",
                            "skill_id": skill_name,
                            "path": str(rel_path.parent),
                            "description": f"Potential skill found at {rel_path.parent}",
                            "type": "discovered",
                        })
                    break

    # Filter by query if provided
    if query:
        query_lower = query.lower()
        findings = [f for f in findings
                   if query_lower in f.get("skill_id", "").lower()
                   or query_lower in f.get("description", "").lower()]

    return findings


def search_github_skills(query=None):
    """Search GitHub for skill-like repositories or patterns."""
    findings = []

    # Check if gh CLI is available
    try:
        subprocess.run(["gh", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [{"source": "github", "error": "GitHub CLI (gh) not installed"}]

    # Search for relevant repos in the user's GitHub
    search_queries = [
        "claude-code-skill",
        "claude skill",
        "agent skill",
    ]

    for sq in search_queries:
        try:
            result = subprocess.run(
                ["gh", "search", "repos", sq, "--owner", "@me", "--limit", "5", "--json", "name,description,url"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                repos = json.loads(result.stdout)
                for repo in repos:
                    # Try to infer skill_id from repo name
                    skill_id = repo["name"].lower().replace("-", "_").replace("_skill", "").replace("skill_", "")

                    if skill_id not in get_registered_skill_ids():
                        findings.append({
                            "source": "github",
                            "skill_id": skill_id,
                            "name": repo["name"],
                            "description": repo.get("description", ""),
                            "url": repo.get("url", ""),
                            "type": "repo",
                        })
        except Exception as e:
            findings.append({"source": "github", "error": str(e)})

    # Filter by query if provided
    if query:
        query_lower = query.lower()
        findings = [f for f in findings
                   if "error" not in f
                   and (query_lower in f.get("skill_id", "").lower()
                        or query_lower in f.get("description", "").lower())]

    return findings


def search_external_skills(query=None):
    """Search external sources (npm, pypi, etc.) for skill-like packages."""
    findings = []

    # Check for npm packages
    try:
        if query:
            result = subprocess.run(
                ["npm", "search", query, "--json"],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                try:
                    packages = json.loads(result.stdout)
                    for pkg in packages[:5]:
                        findings.append({
                            "source": "npm",
                            "skill_id": pkg.get("name", "").replace("-", "_"),
                            "description": pkg.get("description", ""),
                            "version": pkg.get("version", ""),
                            "type": "package",
                        })
                except json.JSONDecodeError:
                    pass
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Check for PyPI packages
    try:
        if query:
            result = subprocess.run(
                ["pip", "index", "versions", query],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0 and result.stdout:
                findings.append({
                    "source": "pypi",
                    "skill_id": query.lower().replace("-", "_"),
                    "description": result.stdout.strip()[:200],
                    "type": "package",
                })
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return findings


def generate_research_report(sources, query=None):
    """Generate a research report from all sources."""
    report = {
        "generated_at": datetime.now().isoformat(),
        "query": query,
        "sources": sources,
        "findings": {},
        "summary": {},
    }

    all_findings = []

    if "internal" in sources:
        internal = search_internal_skills(query)
        report["findings"]["internal"] = internal
        all_findings.extend(internal)

    if "github" in sources:
        github = search_github_skills(query)
        report["findings"]["github"] = github
        all_findings.extend(github)

    if "external" in sources or "npm" in sources or "pypi" in sources:
        external = search_external_skills(query)
        report["findings"]["external"] = external
        all_findings.extend(external)

    # Summary
    report["summary"] = {
        "total_findings": len(all_findings),
        "by_source": {},
        "already_registered": len(get_registered_skill_ids()),
    }

    for finding in all_findings:
        source = finding.get("source", "unknown")
        report["summary"]["by_source"][source] = report["summary"]["by_source"].get(source, 0) + 1

    return report


def main():
    parser = argparse.ArgumentParser(description="Skills Researcher - Discover skills from various sources")
    parser.add_argument("--sources", default="internal", help="Comma-separated sources: github,internal,external (default: internal)")
    parser.add_argument("--query", "-q", help="Search query")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--limit", type=int, default=20, help="Limit results per source")
    args = parser.parse_args()

    sources = [s.strip() for s in args.sources.split(",")]

    # Validate sources
    valid_sources = {"github", "internal", "external", "npm", "pypi"}
    invalid = [s for s in sources if s not in valid_sources]
    if invalid:
        print(f"Error: Invalid sources: {', '.join(invalid)}")
        print(f"Valid sources: {', '.join(sorted(valid_sources))}")
        return 1

    report = generate_research_report(sources, args.query)

    # Extract all findings for recommendations
    all_findings = []
    for source, findings in report["findings"].items():
        all_findings.extend(findings)

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    # Human-readable output
    print(f"# Skills Research Report")
    print(f"Generated: {report['generated_at']}")
    print(f"Sources: {', '.join(sources)}")
    if args.query:
        print(f"Query: {args.query}")
    print()

    # Summary
    print(f"## Summary")
    print(f"- Total findings: {report['summary']['total_findings']}")
    print(f"- Already registered: {report['summary']['already_registered']}")
    print(f"- By source:")
    for source, count in report["summary"]["by_source"].items():
        print(f"  - {source}: {count}")
    print()

    # Findings by source
    for source in sources:
        findings = report["findings"].get(source, [])
        if not findings:
            continue

        print(f"## {source.upper()} ({len(findings)} findings)")

        for f in findings[:args.limit]:
            if "error" in f:
                print(f"  - Error: {f['error']}")
                continue

            skill_id = f.get("skill_id", "unknown")
            desc = f.get("description", "No description")
            path = f.get("path", f.get("url", ""))

            print(f"  - `{skill_id}`: {desc[:60]}")
            if path:
                print(f"    -> {path}")

        if len(findings) > args.limit:
            print(f"  ... and {len(findings) - args.limit} more")
        print()

    # Recommendations
    new_skills = [f for f in all_findings
                 if f.get("skill_id") not in get_registered_skill_ids()]

    if new_skills:
        print("## Recommendations")
        print(f"Found {len(new_skills)} potential new skills not in registry:")
        for f in new_skills[:10]:
            print(f"  - {f.get('skill_id')} ({f.get('source')})")
        if len(new_skills) > 10:
            print(f"  ... and {len(new_skills) - 10} more")
    else:
        print("## Recommendations")
        print("No new skills found. Consider creating new skills or checking different sources.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
