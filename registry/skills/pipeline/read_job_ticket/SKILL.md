---
name: read-job-ticket
description: Read and validate a JobTicket from inbox
user-invocable: true
---

# Read JobTicket Skill

Read a JobTicket JSON file from the inbox and validate its structure.

## Usage

```
/read-job-ticket <ticket_file.json>
```

Or call from skill:

## Steps

1. Find the latest `inbox/*.json` file
2. Read the JSON file
3. Validate required fields:
   - `id` (TASK-XXXX format)
   - `task_description`
   - `target_workspace`
   - `priority`
   - `status`
4. Extract and return key fields

## Output

Return a summary:
```
TICKET_ID: TASK-0001
DESCRIPTION: Add dark mode
REPO: /path/to/repo
PRIORITY: medium
STATUS: pending
```
