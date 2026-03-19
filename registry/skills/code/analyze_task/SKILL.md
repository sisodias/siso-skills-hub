---
name: analyze-task
description: Analyze a task and decompose into user stories
version: 1.0.0
tags:
  - task-management
  - planning
user-invocable: true
---

# Analyze Task Skill

Decompose a task description into ordered user stories.

## Usage

```
/analyze-task <task_description> <repo_path>
```

## Steps

1. Explore the codebase to understand:
   - Tech stack
   - File structure
   - Conventions
   - Existing patterns

2. Break task into stories (max 20)

3. Order by dependency:
   - Schema/DB first
   - Backend logic
   - Frontend
   - Integration

4. For each story, define:
   - ID (US-001, US-002, etc.)
   - Title
   - Description (As a... I need... So that...)
   - Acceptance criteria (mechanically verifiable)
   - Test requirements

5. Output to `stories.json`

## Output Format

```json
{
  "stories": [
    {
      "id": "US-001",
      "title": "Add database column",
      "description": "As a user, I need... ",
      "acceptanceCriteria": [
        "Column added to schema",
        "Migration runs",
        "Tests pass"
      ]
    }
  ]
}
```
