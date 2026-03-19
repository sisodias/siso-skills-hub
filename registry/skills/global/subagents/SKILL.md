---
name: subagents
description: Spawn and manage subagents for parallel work
version: 1.0.0
tags:
  - agent-management
  - parallel-execution
user-invocable: true
---

# Subagents

Spawn subagents to keep your context clean and run work in parallel.

## When to Use Subagents

- Research tasks (search multiple sources)
- Parallel file operations
- Complex problems (throw more compute at it)
- Any task that can be broken down

## Available Subagent Types

| Type | Use For |
|------|---------|
| `general-purpose` | Default, any task |
| `Explore` | Codebase research, searching, finding patterns |
| `test-runner` | Running tests, verifying fixes |
| `file-creator` | Creating multiple files, batch operations |

## Syntax

```
Use the Agent tool with:
{
  "description": "what the subagent does",
  "prompt": "detailed instructions for the subagent",
  "subagent_type": "Explore",
  "run_in_background": true  // parallel
}
```

## Examples

### Research in Parallel

```
Spawn 3 parallel agents for research:

1. Agent: "web-researcher"
   subagent_type: "Explore"
   prompt: "Search the web for X"

2. Agent: "github-researcher"
   subagent_type: "Explore"
   prompt: "Search GitHub for X"

3. Agent: "x-researcher"
   subagent_type: "Explore"
   prompt: "Search X/Twitter for X"

Use run_in_background: true for all 3
```

### File Operations

```
For batch file creation:
subagent_type: "file-creator"
prompt: "Create 5 test files with these contents..."
```

### Testing

```
For running tests:
subagent_type: "test-runner"
prompt: "Run the test suite and report results"
```

## Templates

See `templates/` folder for prompt templates:

- `research.md` — Research task template
- `testing.md` — Test runner template
- `file-ops.md` — File operation template
- `parallel-spawn.md` — Spawn multiple subagents

## Best Practices

1. **Always use subagents** to keep context clean
2. **Spawn in parallel** with `run_in_background: true`
3. **One task per subagent** for focused execution
4. **Provide detailed prompts** — don't be vague
5. **Wait for results** before synthesizing
