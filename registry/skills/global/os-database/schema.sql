-- SISO Agent OS Database Schema
-- Reference for agents - DO NOT EDIT

-- HIERARCHY
workspaces(id, name, root_path, created_at)
projects(id, workspace_id FK, name, status, created_at)
missions(id, project_id FK, name, description, target_completion_date, status, created_at)
goals(id, mission_id FK, name, success_criteria, status, created_at)

-- AGENTS
agents(id PK, role, department, root_path, status, token_budget_limit, tokens_used_lifetime, circuit_breaker_active, run_count, created_at, updated_at)

-- TASKS
tasks(id PK, goal_id FK, parent_task_id FK, blocked_by_task_id FK, assigned_agent_id FK, created_by_agent_id FK, title, description, status, workspace_path, executive_summary, tokens_burned, started_at, completed_at, created_at, updated_at)

-- TIMELINE (Twitter feed)
timeline_events(id PK, task_id FK, agent_id FK, event_type CHECK(BOOT,THOUGHT,ACTION,TOOL_CALL,ERROR,HANDOFF,COMPLETED), message, metadata, timestamp)

-- ARTIFACTS
artifacts(id PK, task_id FK, artifact_type, file_path, created_at)

-- SESSIONS
sessions(id PK, agent_id FK, task_id FK, run_number, status, start_time, end_time, tokens_used)

-- TOOLS
tools(id PK, name, description, parameters_schema, is_global)
agent_permissions(agent_id FK, tool_id FK)

-- MEMORIES
memories(id PK, task_id FK, agent_id FK, type, content, created_at)

-- KEY RELATIONSHIPS:
-- Task -> Goal -> Mission -> Project -> Workspace
-- Task -> blocked_by_task_id (dependency graph)
-- Task -> parent_task_id (subtasks)
-- Timeline -> Task -> Agent
-- Session -> Agent -> Task
