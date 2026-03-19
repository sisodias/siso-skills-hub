---
name: gitsearch
description: Search GitHub for code, repos, issues, and PRs. Use when looking for examples, libraries, or tracking down bugs.
version: 1.0.0
tags:
  - research
  - github
user-invocable: true
context: fork
agent: Explore
allowed-tools: Bash
---

# GitHub Search

You are running in a forked subagent context. Your task is to search GitHub.

## Search Query

$ARGUMENTS

## Your Task

1. Run one or more GitHub searches as appropriate:
```bash
# Search repositories
gh search repos "$ARGUMENTS" --limit 10 --sort stars

# Search code
gh search code "$ARGUMENTS" --limit 10

# Search issues
gh search issues "$ARGUMENTS" --limit 10

# Search PRs
gh search prs "$ARGUMENTS" --limit 10
```

2. Summarize the top results with:
   - Repository name and URL
   - Star count
   - Brief description
   - Relevance to the query

Return a concise summary of the GitHub search results.
