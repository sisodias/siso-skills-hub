---
name: timeline
description: Track your thought process, actions, and decisions in a persistent timeline
user-invocable: true
---

# Timeline Skill

Track your thought process, actions, and decisions in a persistent timeline that persists across sessions.

## Usage

```
/timeline add <entry_type> <content>
/timeline recent [count]
/timeline search <query>
```

## Entry Types

- **thought**: Observations, hypotheses, reasoning
- **action**: Things you did (files changed, commands run)
- **decision**: Choices you made and why
- **milestone**: Significant achievements or completions
- **tool_use**: External tool/API calls and results

## Database Schema

The timeline entries are stored in `agent_os/.SystemDB/sisosystem.db`:

```sql
CREATE TABLE agent_timeline_entries (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    session_id TEXT,
    entry_type TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Commands

### Add Entry

```bash
# Add a thought
sqlite3 $SYSTEM_DB "INSERT INTO agent_timeline_entries (id, agent_id, entry_type, content) VALUES (
  'tl_' || lower(hex(randomblob(4))),
  '$AGENT_ID',
  'thought',
  'User wants to add timeline tracking to all agents'
);"

# Add an action
sqlite3 $SYSTEM_DB "INSERT INTO agent_timeline_entries (id, agent_id, entry_type, content) VALUES (
  'tl_' || lower(hex(randomblob(4))),
  '$AGENT_ID',
  'action',
  'Created timeline skill at skills_hub/timeline/SKILL.md'
);"

# Add a decision
sqlite3 $SYSTEM_DB "INSERT INTO agent_timeline_entries (id, agent_id, entry_type, content, metadata) VALUES (
  'tl_' || lower(hex(randomblob(4))),
  '$AGENT_ID',
  'decision',
  'Using SQLite for timeline storage to match existing task DB',
  '{\"reason\": \"simplicity, no new dependencies\"}'
);"
```

### View Recent

```bash
sqlite3 $SYSTEM_DB "SELECT entry_type, content, created_at FROM agent_timeline_entries
  WHERE agent_id = '$AGENT_ID'
  ORDER BY created_at DESC
  LIMIT 10;"
```

### Search

```bash
sqlite3 $SYSTEM_DB "SELECT entry_type, content, created_at FROM agent_timeline_entries
  WHERE agent_id = '$AGENT_ID' AND content LIKE '%query%'
  ORDER BY created_at DESC;"
```

## Best Practices

1. **Log early, log often** — Add entries at key moments, not just at the end
2. **Be specific** — "Fixed auth bug in login.js" not "worked on stuff"
3. **Link context** — Use metadata to link to task IDs, file paths
4. **Review before major decisions** — Check your recent timeline for context

## Example Workflow

```
/timeline add thought User wants each agent to have their own timeline
/timeline add action Researched existing database schema - found tasks, steps, sessions tables
/timeline add decision Using existing sisosystem.db instead of creating new DB
/timeline add milestone Designed timeline schema with agent_id, entry_type, content, metadata
/timeline add tool_use Read existing skill files to understand SKILL.md format
/timeline recent 5
/timeline search "database"
```

## Environment Variables

- `AGENT_ID` — Set this to uniquely identify your agent (e.g., "pm-agent", "researcher-01")
- `SYSTEM_DB` — Path to the tasks database (default: `agent_os/.SystemDB/sisosystem.db`)
