# Parallel Spawn Template

Use this to spawn multiple subagents in parallel.

## Pattern

```
Use the Agent tool multiple times with run_in_background: true:

Agent 1:
{
  "description": "[task 1]",
  "prompt": "[detailed prompt 1]",
  "subagent_type": "[type]",
  "run_in_background": true
}

Agent 2:
{
  "description": "[task 2]",
  "prompt": "[detailed prompt 2]",
  "subagent_type": "[type]",
  "run_in_background": true
}

Agent 3:
{
  "description": "[task 3]",
  "prompt": "[detailed prompt 3]",
  "subagent_type": "[type]",
  "run_in_background": true
}
```

## Example: Multi-Source Research

```
// Agent 1: Web Search
{
  "description": "Web research on API authentication",
  "prompt": "Search the web for best practices for API authentication in 2025. Focus on OAuth2 patterns.",
  "subagent_type": "Explore",
  "run_in_background": true
}

// Agent 2: GitHub Search
{
  "description": "GitHub research on auth patterns",
  "prompt": "Search GitHub for popular authentication libraries and their patterns. Look at stars and recent commits.",
  "subagent_type": "Explore",
  "run_in_background": true
}

// Agent 3: X/Twitter Search
{
  "description": "Twitter research on auth",
  "prompt": "Search X/Twitter for discussions about API authentication best practices in 2025.",
  "subagent_type": "Explore",
  "run_in_background": true
}
```

## Key Points

1. **Always use `run_in_background: true`** for parallel execution
2. **Wait for all to complete** before synthesizing
3. **Aggregate results** into a unified summary
