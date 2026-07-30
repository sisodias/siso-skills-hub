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
ASSESSMENTS = ROOT / "registry" / "promotion-assessments.json"
SKILLS = ROOT / "registry" / "skills"
IGNORED = {".git", "__pycache__", "node_modules"}


def run(command, **kwargs):
    subprocess.run(command, cwd=ROOT, check=True, **kwargs)


entries = json.loads(REGISTRY.read_text()).get("skills", [])
ids = [entry["skill_id"] for entry in entries]
assert entries and len(ids) == len(set(ids)), "registry skill IDs must be non-empty and unique"

assessment_entries = json.loads(ASSESSMENTS.read_text()).get("assessments", [])
assessment_ids = [entry["skill_id"] for entry in assessment_entries]
assert len(assessment_ids) == len(set(assessment_ids)), "promotion assessment IDs must be unique"
assert set(assessment_ids) == set(ids), "promotion assessments must cover exactly the registered skills"
known_kinds = {"atomic_skill", "tool_adapter", "playbook_step", "orchestration_playbook", "system_adapter", "environment_recipe", "catalog_meta_skill", "deprecated_adapter", "mixed_legacy_system"}
known_recommendations = {"stay_bundled", "move_to_playbook", "reconcile_system_then_keep_adapter", "retire_or_replace", "candidate_after_evidence", "keep_thin_adapter", "retire_after_adapter", "decompose_then_retire"}
for entry in assessment_entries:
    assert entry["capability_kind"] in known_kinds, f"unknown capability kind for {entry['skill_id']}"
    assert entry["recommendation"] in known_recommendations, f"unknown recommendation for {entry['skill_id']}"
    assert entry["decision_status"] in {"provisional", "accepted"}, f"unknown decision status for {entry['skill_id']}"
    assert entry.get("reason") and entry.get("target") and entry.get("evidence"), f"assessment evidence incomplete for {entry['skill_id']}"

for entry in entries:
    candidates = list(SKILLS.glob(f"*/{entry['skill_id']}"))
    assert len(candidates) == 1, f"expected one bundled source for {entry['skill_id']}, found {len(candidates)}"
    assert (candidates[0] / "SKILL.md").is_file(), f"missing SKILL.md for {entry['skill_id']}"
    if entry.get("remote_url"):
        assert re.fullmatch(r"[0-9a-f]{40}", entry.get("commit_hash") or ""), f"remote skill {entry['skill_id']} needs a full commit pin"

runtime_artifact_names = {"state.json"}
runtime_artifact_suffixes = (".db", ".db-wal", ".db-shm", ".sqlite", ".sqlite-wal", ".sqlite-shm")
for path in SKILLS.rglob("*"):
    if path.is_file():
        assert path.name not in runtime_artifact_names and not path.name.endswith(runtime_artifact_suffixes), f"runtime artifact committed under skills: {path.relative_to(ROOT)}"

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
    target = Path(directory) / "installed"
    run(["python3", "scripts/skills", "install", "gitsearch", "--target", str(target)], env=env, stdout=subprocess.DEVNULL)
    assert (target / "gitsearch" / "SKILL.md").is_file(), "disposable skill installation did not materialize source"
    state_path = Path(directory) / "agent-state.json"
    env.update({
        "SISO_AGENT_STATE": str(state_path),
        "SISO_AGENT_ID": "agent-test",
        "SISO_AGENT_ROLE": "tester",
        "SISO_AGENT_DEPARTMENT": "verification",
        "SISO_AGENT_ROOT": directory,
    })
    probe = """
import importlib.util, json, pathlib, sys
module_path = pathlib.Path(sys.argv[1])
spec = importlib.util.spec_from_file_location('shared_config_probe', module_path)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
config = module.load_config()
assert config['db_path'] == sys.argv[2]
assert config['agent_id'] == 'agent-test'
module.save_state({'session': 'synthetic'})
assert module.load_state() == {'session': 'synthetic'}
"""
    run(["python3", "-c", probe, str(SKILLS / "global" / "os-database" / "scripts" / "_shared_config.py"), env["SISO_SYSTEM_DB"]], env=env, stdout=subprocess.DEVNULL)

    fake_brain = Path(directory) / "fake_brain.py"
    capture = Path(directory) / "brain-command.json"
    fake_brain.write_text(
        "import json, os, sys\n"
        "open(os.environ['SISO_BRAIN_CAPTURE'], 'w').write(json.dumps(sys.argv[1:]))\n"
        "print('{\"ok\":true}')\n"
    )
    adapter_env = dict(env)
    adapter_env.update({"SISO_BRAIN_CLI": f"python3 {fake_brain}", "SISO_BRAIN_CAPTURE": str(capture)})
    task_adapter = SKILLS / "system" / "task-manager" / "siso-tasks.py"
    pm_adapter = SKILLS / "system" / "pm-tasks" / "scripts" / "pm_tasks.py"
    run(["python3", str(task_adapter), "create-task", "--id", "TASK-CHECK", "--project-id", "library",
         "--pipeline-type", "execution", "--description", "adapter receipt", "--assigned-to", "builder",
         "--priority", "8"], env=adapter_env, stdout=subprocess.DEVNULL)
    routed = json.loads(capture.read_text())
    assert routed[:3] == ["task-create", "--id", "TASK-CHECK"] and "--urgency" in routed and "80" in routed
    run(["python3", str(pm_adapter), "update", "TASK-CHECK", "completed"], env=adapter_env, stdout=subprocess.DEVNULL)
    assert json.loads(capture.read_text()) == ["task-update", "--id", "TASK-CHECK", "--status", "completed"]
    refused = subprocess.run(["python3", str(task_adapter), "query", "--sql", "SELECT * FROM tasks"],
                             cwd=ROOT, env=adapter_env, text=True, capture_output=True)
    assert refused.returncode == 2 and "raw SQL is retired" in refused.stderr

run(["python3", "scripts/build_index.py", "--check"])
run(["python3", "scripts/build_promotion_map.py", "--check"])

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
