# Rule: Escalation Protocol

When you cannot solve a task after 3 attempts, escalate to human.

## When to Escalate

- Task fails repeatedly
- Missing critical information
- Unclear requirements
- Blocked by external dependency

## How to Escalate

```bash
python3 .claude/skills/os-database/scripts/log_event.py --type "ERROR" --msg "Escalating: stuck on auth - need API key"
```

Then respond to user: "I need help with X. Can you provide Y?"

## Never

- Loop indefinitely trying the same thing
- Guess at missing information
- Fail silently
