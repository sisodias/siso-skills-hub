#!/usr/bin/env python3
"""Shared configuration utilities for os-database scripts."""
import json
import os
import tempfile

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
STATE_PATH = os.path.expanduser(
    os.environ.get("SISO_AGENT_STATE", os.path.join(SCRIPT_DIR, ".runtime", "state.json"))
)


def _resolved(value, fallback=None):
    if isinstance(value, str) and value.startswith("env:"):
        environment_value = os.environ.get(value.removeprefix("env:"), "").strip()
        value = environment_value or fallback
    return os.path.expanduser(value) if isinstance(value, str) else value


def load_config():
    """Load public defaults and resolve explicit environment-backed values."""
    with open(CONFIG_PATH) as f:
        source = json.load(f)
    return {
        key: _resolved(value, source.get(f"{key}_fallback"))
        for key, value in source.items()
        if not key.endswith("_fallback")
    }


def load_state():
    """Load local runtime state, returning an empty state before first boot."""
    if not os.path.exists(STATE_PATH):
        return {}
    with open(STATE_PATH) as f:
        return json.load(f)


def save_state(state):
    """Atomically persist local state outside the public source files."""
    state_directory = os.path.dirname(STATE_PATH) or "."
    os.makedirs(state_directory, exist_ok=True)
    descriptor, temporary_path = tempfile.mkstemp(prefix="state-", suffix=".json", dir=state_directory)
    try:
        with os.fdopen(descriptor, "w") as handle:
            json.dump(state, handle, indent=2)
            handle.write("\n")
        os.chmod(temporary_path, 0o600)
        os.replace(temporary_path, STATE_PATH)
    finally:
        if os.path.exists(temporary_path):
            os.unlink(temporary_path)


# Export for convenience
__all__ = ['SCRIPT_DIR', 'CONFIG_PATH', 'STATE_PATH', 'load_config', 'load_state', 'save_state']
