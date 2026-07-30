---
name: Boot Sequence
description: Initialize your session and register with the OS. Run this FIRST when you boot.
---

# Procedure: Boot Sequence

You have just started. You MUST execute these steps in exact order.

## Step 1: Initialize Session
- **Action:** Run the init script
```bash
python3 .claude/skills/os-database/scripts/init_session.py
```
- **Result:** Creates a session and writes your SESSION_ID and run number to gitignored local runtime state. Set `SISO_AGENT_STATE` to choose a different explicit state path.

## Step 2: Log Your Boot
- **Action:** Log a BOOT event to timeline
```bash
python3 .claude/skills/os-database/scripts/log_event.py --type "BOOT" --msg "Agent booted. Session initialized."
```

## Step 3: Check for Work
- **Action:** Check if you have assigned tasks
```bash
python3 .claude/skills/os-database/scripts/get_my_tasks.py
```
- **Result:** Returns list of tasks assigned to you

## Step 4: Log Your First Thought
- **Action:** Log what you're about to do
```bash
python3 .claude/skills/os-database/scripts/log_event.py --type "THOUGHT" --msg "Found X tasks. Beginning work on first priority task."
```

---

**IMPORTANT:** Never skip Step 1. Without init_session.py, you won't be tracked in the OS.
