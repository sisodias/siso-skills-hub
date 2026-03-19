---
name: verify-story
description: Verify a story implementation meets acceptance criteria
version: 1.0.0
tags:
  - testing
  - verification
user-invocable: true
---

# Verify Story Skill

Verify that a story was implemented correctly.

## Usage

```
/verify-story <story_id> <repo_path> <branch>
```

## Steps

1. Inspect the git diff:
   ```
   git diff main..<branch>
   ```

2. Security checks FIRST:
   - Verify .gitignore exists
   - Check for sensitive files in diff
   - Scan for hardcoded credentials

3. Verify acceptance criteria:
   - Read the story from stories.json
   - Check each criterion against actual code

4. Run tests:
   ```
   npm test
   npm run typecheck
   ```

5. Visual verification (if UI):
   - Open local server
   - Take screenshot
   - Check layout/styling

## Output

```
STATUS: done
VERIFIED:
- Criterion 1: PASS
- Criterion 2: PASS

Or:

STATUS: retry
ISSUES:
- Issue 1: what failed
```
