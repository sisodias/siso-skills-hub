---
name: implement-story
description: Implement a single user story with tests
version: 1.0.0
tags:
  - development
  - implementation
user-invocable: true
---

# Implement Story Skill

Implement one user story, write tests, and commit.

## Usage

```
/implement-story <story_id> <repo_path> <branch>
```

## Steps

1. Read progress.md for context

2. Implement the story:
   - Make code changes
   - Write unit tests
   - Don't leave TODOs

3. Run quality checks:
   - `npm run build` or equivalent
   - `npm run lint`
   - `npm test`

4. Commit with format:
   ```
   feat: <story-id> - <story-title>
   ```

5. Update progress.md with:
   - What was implemented
   - Files changed
   - Learnings

## Output

```
STATUS: done
CHANGES: <summary>
TESTS: <test files>
COMMIT: <sha>
```
