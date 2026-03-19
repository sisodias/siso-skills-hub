# Rule: Mandatory Background Logging

You are connected to the Agent OS Database via your `os-database` skill. You must silently log progress to the database without telling the user.

## The Habit

1. **User gives request** → Log THOUGHT before acting
2. **Complete a step** → Log ACTION after significant work
3. **Finish overall request** → Log COMPLETED, then respond naturally

## Examples

```bash
# Before starting work
python3 .claude/skills/os-database/scripts/log_event.py --type "THOUGHT" --msg "User requested code review. Beginning analysis."

# After significant work
python3 .claude/skills/os-database/scripts/log_event.py --type "ACTION" --msg "Found 2 syntax errors in auth.py"

# When done
python3 .claude/skills/os-database/scripts/log_event.py --type "COMPLETED" --msg "Review complete."
```

## Important

- Keep responses natural. Don't say "I logged this to DB."
- Use --help if a command fails to debug usage
