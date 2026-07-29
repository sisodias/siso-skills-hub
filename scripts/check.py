#!/usr/bin/env python3
"""Validate registry/source parity, entrypoints, index, and publication safety."""

import json
import os
from pathlib import Path
import py_compile
import re
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "skills_registry.json"
SKILLS = ROOT / "registry" / "skills"
IGNORED = {".git", "__pycache__", "node_modules"}


def run(command, **kwargs):
    subprocess.run(command, cwd=ROOT, check=True, **kwargs)


entries = json.loads(REGISTRY.read_text()).get("skills", [])
ids = [entry["skill_id"] for entry in entries]
assert entries and len(ids) == len(set(ids)), "registry skill IDs must be non-empty and unique"

for entry in entries:
    candidates = list(SKILLS.glob(f"*/{entry['skill_id']}"))
    assert len(candidates) == 1, f"expected one bundled source for {entry['skill_id']}, found {len(candidates)}"
    assert (candidates[0] / "SKILL.md").is_file(), f"missing SKILL.md for {entry['skill_id']}"
    if entry.get("remote_url"):
        assert re.fullmatch(r"[0-9a-f]{40}", entry.get("commit_hash") or ""), f"remote skill {entry['skill_id']} needs a full commit pin"

for path in ROOT.rglob("*.py"):
    if not IGNORED.intersection(path.parts):
        py_compile.compile(str(path), doraise=True)

for path in ROOT.rglob("*"):
    if not path.is_file() or IGNORED.intersection(path.parts):
        continue
    try:
        first = path.read_text().splitlines()[0]
    except (UnicodeDecodeError, IndexError):
        continue
    if "bash" in first or first.endswith("/sh"):
        run(["bash", "-n", str(path)])

with tempfile.TemporaryDirectory(prefix="siso-skills-hub-check-") as directory:
    env = dict(os.environ)
    env["SISO_SYSTEM_DB"] = str(Path(directory) / "system.sqlite")
    for skill_id in ids:
        run(["python3", "scripts/skills", "validate", skill_id], env=env, stdout=subprocess.DEVNULL)

run(["python3", "scripts/build_index.py", "--check"])

patterns = [
    re.compile("/" + "Users" + "/"),
    re.compile("BEGIN (?:RSA |OPENSSH |EC |DSA )?" + "PRIVATE KEY"),
    re.compile("(?:ghp|github_pat|sk)" + "-[A-Za-z0-9_-]{16,}"),
]
for path in ROOT.rglob("*"):
    if IGNORED.intersection(path.parts):
        continue
    if path.is_symlink():
        text = os.readlink(path)
    elif path.is_file():
        try:
            text = path.read_text()
        except UnicodeDecodeError:
            continue
    else:
        continue
    for pattern in patterns:
        if pattern.search(text):
            raise SystemExit(f"publication safety match {pattern.pattern!r} in {path.relative_to(ROOT)}")

assert not any(path.is_symlink() for path in ROOT.rglob("*") if ".git" not in path.parts), "public source must not contain unresolved symlinks"
print(f"SKILLS_HUB_CHECK_OK ({len(entries)} skills)")
