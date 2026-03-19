#!/usr/bin/env python3
import sqlite3
import argparse
import json
import os
import sys
from datetime import datetime, timezone

DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH, isolation_level=None) # Auto-commit mode
    # Enable WAL mode for high concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(args):
    conn = get_db()
    cursor = conn.cursor()
    
    # Create Tasks table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        pipeline_type TEXT NOT NULL,
        title TEXT,
        category TEXT,
        created_by TEXT,
        assigned_to TEXT,
        description TEXT NOT NULL,
        metadata TEXT,
        status TEXT NOT NULL,
        priority INTEGER DEFAULT 1,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create Task Steps table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS task_steps (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        step_name TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_agent_role TEXT,
        step_order INTEGER NOT NULL,
        input_payload TEXT,
        output_payload TEXT,
        error_log TEXT,
        FOREIGN KEY(task_id) REFERENCES tasks(id)
    )
    """)
    
    # Create Artifacts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artifacts (
        id TEXT PRIMARY KEY,
        task_id TEXT NOT NULL,
        artifact_type TEXT NOT NULL,
        content TEXT NOT NULL,
        version INTEGER DEFAULT 1,
        created_by_step_id TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(id),
        FOREIGN KEY(created_by_step_id) REFERENCES task_steps(id)
    )
    """)
    
    # Create Sessions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        project_id TEXT NOT NULL,
        role TEXT NOT NULL,
        context_data TEXT,
        start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        end_time DATETIME
    )
    """)
    
    # Create Memories table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id TEXT PRIMARY KEY,
        task_id TEXT,
        session_id TEXT,
        type TEXT NOT NULL,
        content TEXT NOT NULL,
        embedding BLOB,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(id),
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)
    
    # Create Tools table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tools (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        parameters_schema TEXT,
        is_global INTEGER DEFAULT 0
    )
    """)
    
    # Create Agent Permissions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_permissions (
        role TEXT NOT NULL,
        tool_id TEXT NOT NULL,
        PRIMARY KEY (role, tool_id),
        FOREIGN KEY(tool_id) REFERENCES tools(id)
    )
    """)
    
    # Create Execution Logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS execution_logs (
        id TEXT PRIMARY KEY,
        step_id TEXT,
        session_id TEXT,
        action_type TEXT NOT NULL,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(step_id) REFERENCES task_steps(id),
        FOREIGN KEY(session_id) REFERENCES sessions(id)
    )
    """)
    
    print(f"Initialized database at {DB_PATH}")

def create_task(args):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    cursor.execute("""
    INSERT INTO tasks (id, project_id, pipeline_type, title, category, created_by, assigned_to, description, metadata, status, priority, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (args.id, args.project_id, args.pipeline_type, args.title, args.category, args.created_by, args.assigned_to, args.description, args.metadata, "pending", args.priority, now, now))
    
    print(json.dumps({"status": "success", "task_id": args.id}))

def add_step(args):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    INSERT INTO task_steps (id, task_id, step_name, status, assigned_agent_role, step_order, input_payload)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (args.id, args.task_id, args.step_name, "pending", args.role, args.order, args.input_payload))
    
    print(json.dumps({"status": "success", "step_id": args.id}))

def pull_step(args):
    conn = get_db()
    cursor = conn.cursor()
    
    # Find the earliest pending step for this role where the task isn't failed/paused
    # Also ensuring previous steps are 'done' (omitted for simple MVP, but order is enforced by step_order)
    # A true DAG would check if step_order-1 is 'done'.
    cursor.execute("""
    SELECT s.id, s.task_id, s.step_name, s.input_payload, t.project_id, t.description as task_description
    FROM task_steps s
    JOIN tasks t ON s.task_id = t.id
    WHERE s.assigned_agent_role = ? AND s.status IN ('pending', 'retry') AND t.status NOT IN ('failed', 'paused', 'completed')
    ORDER BY t.priority DESC, s.step_order ASC
    LIMIT 1
    """, (args.role,))
    
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "empty", "message": f"No pending steps found for role: {args.role}"}))
        return
    
    # Atomically mark as in_progress
    cursor.execute("UPDATE task_steps SET status = 'in_progress' WHERE id = ? AND status IN ('pending', 'retry')", (row['id'],))
    
    result = {
        "status": "success",
        "step_id": row['id'],
        "task_id": row['task_id'],
        "step_name": row['step_name'],
        "project_id": row['project_id'],
        "task_description": row['task_description'],
        "input_payload": json.loads(row['input_payload']) if row['input_payload'] else None
    }
    print(json.dumps(result, indent=2))

def view_inbox(args):
    """View all pending steps for a specific role/agent without pulling them"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT s.id, s.task_id, s.step_name, s.status, t.project_id, t.description as task_description, t.priority
    FROM task_steps s
    JOIN tasks t ON s.task_id = t.id
    WHERE s.assigned_agent_role = ? AND s.status IN ('pending', 'retry', 'in_progress') AND t.status NOT IN ('failed', 'paused', 'completed')
    ORDER BY t.priority DESC, s.step_order ASC
    """, (args.role,))
    
    rows = cursor.fetchall()
    
    inbox = []
    for row in rows:
        inbox.append({
            "step_id": row['id'],
            "task_id": row['task_id'],
            "project_id": row['project_id'],
            "task_description": row['task_description'],
            "step_name": row['step_name'],
            "status": row['status'],
            "priority": row['priority']
        })
        
    print(json.dumps({"status": "success", "role": args.role, "queue_length": len(inbox), "inbox": inbox}, indent=2))

def update_step(args):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    UPDATE task_steps 
    SET status = ?, output_payload = ?, error_log = ?
    WHERE id = ?
    """, (args.status, args.output_payload, args.error_log, args.id))
    
    # Check if task needs to be marked completed or failed
    if args.status == 'error':
        # Mark parent task as failed
        cursor.execute("SELECT task_id FROM task_steps WHERE id = ?", (args.id,))
        task_id = cursor.fetchone()['task_id']
        cursor.execute("UPDATE tasks SET status = 'failed', updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), task_id))
    elif args.status == 'done':
        # Check if all steps are done
        cursor.execute("SELECT task_id FROM task_steps WHERE id = ?", (args.id,))
        task_id = cursor.fetchone()['task_id']
        
        cursor.execute("SELECT count(*) as pending_count FROM task_steps WHERE task_id = ? AND status != 'done'", (task_id,))
        if cursor.fetchone()['pending_count'] == 0:
            cursor.execute("UPDATE tasks SET status = 'completed', updated_at = ? WHERE id = ?", (datetime.now(timezone.utc).isoformat(), task_id))

    print(json.dumps({"status": "success", "step_id": args.id, "new_status": args.status}))

def update_artifact(args):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    import uuid
    artifact_id = str(uuid.uuid4())
    
    # Get current version
    cursor.execute("SELECT coalesce(max(version), 0) + 1 as next_version FROM artifacts WHERE task_id = ? AND artifact_type = ?", (args.task_id, args.type))
    next_version = cursor.fetchone()['next_version']
    
    cursor.execute("""
    INSERT INTO artifacts (id, task_id, artifact_type, content, version, created_by_step_id, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (artifact_id, args.task_id, args.type, args.content, next_version, args.step_id, now))
    
    print(json.dumps({"status": "success", "artifact_id": artifact_id, "version": next_version}))

def get_artifact(args):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT content, version, created_at 
    FROM artifacts 
    WHERE task_id = ? AND artifact_type = ? 
    ORDER BY version DESC LIMIT 1
    """, (args.task_id, args.type))
    
    row = cursor.fetchone()
    if not row:
        print(json.dumps({"status": "not_found"}))
        return
        
    print(row['content'])

def log_execution(args):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    import uuid
    log_id = str(uuid.uuid4())
    
    cursor.execute("""
    INSERT INTO execution_logs (id, step_id, session_id, action_type, details, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (log_id, args.step_id, args.session_id, args.action_type, args.details, now))
    
    print(json.dumps({"status": "success", "log_id": log_id}))

def add_memory(args):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    
    import uuid
    memory_id = str(uuid.uuid4())
    
    cursor.execute("""
    INSERT INTO memories (id, task_id, session_id, type, content, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (memory_id, args.task_id, args.session_id, args.type, args.content, now))
    
    print(json.dumps({"status": "success", "memory_id": memory_id}))

def query_db(args):
    """Execute a raw SELECT query returning JSON. Highly useful for introspection."""
    if not args.sql.strip().upper().startswith("SELECT"):
        print(json.dumps({"status": "error", "message": "Only SELECT queries are allowed for safety."}))
        return
        
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute(args.sql)
        rows = cursor.fetchall()
        
        # Convert sqlite3.Row objects to standard dicts
        results = [dict(row) for row in rows]
        print(json.dumps({"status": "success", "results": results}, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}))

def main():
    parser = argparse.ArgumentParser(description="SISO Tasks CLI - Native DB orchestrator for Agent Skills")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # init
    parser_init = subparsers.add_parser("init", help="Initialize the SQLite database")
    
    # create-task
    parser_create = subparsers.add_parser("create-task", help="Create a new global task")
    parser_create.add_argument("--id", required=True, help="Unique task ID (e.g. TASK-0001)")
    parser_create.add_argument("--project-id", required=True, help="Project name (e.g. lumelle)")
    parser_create.add_argument("--pipeline-type", required=True, help="Pipeline executing this (e.g. execution)")
    parser_create.add_argument("--title", help="Short descriptive title")
    parser_create.add_argument("--category", help="Task category (e.g. feature, bugfix)")
    parser_create.add_argument("--created-by", help="Creator name or human")
    parser_create.add_argument("--assigned-to", help="Assigned agent module")
    parser_create.add_argument("--description", required=True, help="Raw task description")
    parser_create.add_argument("--metadata", help="JSON string for specs, dependencies, beads")
    parser_create.add_argument("--priority", type=int, default=1, help="Integer priority (higher is more urgent)")
    
    # add-step
    parser_add_step = subparsers.add_parser("add-step", help="Add a step to a task DAG")
    parser_add_step.add_argument("--id", required=True, help="Unique step ID")
    parser_add_step.add_argument("--task-id", required=True, help="Parent task ID")
    parser_add_step.add_argument("--step-name", required=True, help="Name of step (e.g. plan)")
    parser_add_step.add_argument("--role", required=True, help="Agent role that picks this up")
    parser_add_step.add_argument("--order", type=int, required=True, help="Sequential order (1, 2, 3...)")
    parser_add_step.add_argument("--input-payload", help="JSON string of inputs")
    
    # pull
    parser_pull = subparsers.add_parser("pull", help="Pull the next available step for a given role")
    parser_pull.add_argument("--role", required=True, help="The agent role (e.g. developer)")
    
    # view-inbox
    parser_inbox = subparsers.add_parser("view-inbox", help="View the entire pending queue for a given role")
    parser_inbox.add_argument("--role", required=True, help="The agent role (e.g. developer)")
    
    # update-step
    parser_update_step = subparsers.add_parser("update-step", help="Update the status and payload of a step")
    parser_update_step.add_argument("--id", required=True, help="Step ID")
    parser_update_step.add_argument("--status", required=True, choices=["done", "retry", "error", "in_progress"], help="New status")
    parser_update_step.add_argument("--output-payload", help="JSON string of outputs")
    parser_update_step.add_argument("--error-log", help="Error notes if status is retry/error")
    
    # update-artifact
    parser_update_art = subparsers.add_parser("update-artifact", help="Push a new version of an artifact")
    parser_update_art.add_argument("--task-id", required=True, help="Parent task ID")
    parser_update_art.add_argument("--step-id", help="Step ID of agent making the edit")
    parser_update_art.add_argument("--type", required=True, help="Type of artifact (e.g. progress_log)")
    parser_update_art.add_argument("--content", required=True, help="The full updated content string")
    
    # get-artifact
    parser_get_art = subparsers.add_parser("get-artifact", help="Get the latest version of an artifact")
    parser_get_art.add_argument("--task-id", required=True, help="Parent task ID")
    parser_get_art.add_argument("--type", required=True, help="Type of artifact (e.g. progress_log)")
    
    # log-execution
    parser_log = subparsers.add_parser("log-execution", help="Log an agent's thought or action loop")
    parser_log.add_argument("--step-id", help="Step ID this execution occurs under")
    parser_log.add_argument("--session-id", help="Session ID (if applicable)")
    parser_log.add_argument("--action-type", required=True, help="Type of action (e.g., thought, execute, tool_call)")
    parser_log.add_argument("--details", required=True, help="JSON string representing the action input/output")

    # add-memory
    parser_memory = subparsers.add_parser("add-memory", help="Save a persistent fact or context")
    parser_memory.add_argument("--task-id", help="Task ID this memory is relevant to")
    parser_memory.add_argument("--session-id", help="Session ID")
    parser_memory.add_argument("--type", required=True, help="Memory category (e.g., fact, observation, learning)")
    parser_memory.add_argument("--content", required=True, help="The detailed memory content")

    # query
    parser_query = subparsers.add_parser("query", help="Run a raw read-only SELECT query against the database")
    parser_query.add_argument("--sql", required=True, help="The SELECT SQL string to execute")

    args = parser.parse_args()
    
    if args.command == "init":
        init_db(args)
    elif args.command == "create-task":
        create_task(args)
    elif args.command == "add-step":
        add_step(args)
    elif args.command == "pull":
        pull_step(args)
    elif args.command == "view-inbox":
        view_inbox(args)
    elif args.command == "update-step":
        update_step(args)
    elif args.command == "update-artifact":
        update_artifact(args)
    elif args.command == "get-artifact":
        get_artifact(args)
    elif args.command == "log-execution":
        log_execution(args)
    elif args.command == "add-memory":
        add_memory(args)
    elif args.command == "query":
        query_db(args)

if __name__ == "__main__":
    main()
