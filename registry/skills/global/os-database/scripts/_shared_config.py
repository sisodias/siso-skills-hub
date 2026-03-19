#!/usr/bin/env python3
"""Shared configuration utilities for os-database scripts."""
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
STATE_PATH = os.path.join(SCRIPT_DIR, "state.json")


def load_config():
    """Load configuration from config.json."""
    with open(CONFIG_PATH) as f:
        return json.load(f)


def load_state():
    """Load state from state.json."""
    with open(STATE_PATH) as f:
        return json.load(f)


# Export for convenience
__all__ = ['SCRIPT_DIR', 'CONFIG_PATH', 'STATE_PATH', 'load_config', 'load_state']
