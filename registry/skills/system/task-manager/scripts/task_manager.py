#!/usr/bin/env python3
"""Task Manager for PM Agent - SQLite based task management"""

import sqlite3
import json
import sys
import os
from datetime import datetime

DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/sisostem.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_task(task_id, title, description="", created_by="PM_Agent", assigned_to="PM_Agent", priority=5, parent_id=None):
    conn = get_db()
    cursor = conn.cursor()
    metadata = json.dumps({"source": "skill"})
    cursor.execute("""
        INSERT OR REPLACE INTO tasks (id, title, description, status, priority, created_by, assigned_to, parent_id, metadata)
        VALUES (?, ?, ?, 'pending', ?, ?, ?, ?, ?)
    """, (task_id, title, description, priority, created_by, assigned_to, parent_id, metadata))
    conn.commit()
    conn.close()
    print(f"✅ Created task: {task_id} - {title}")

def list_tasks(assigned_to=None, status=None, parent_id=None):
    conn = get_db()
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)
    if status:
        query += " AND status = ?"
        params.append(status)
    if parent_id:
        query += " AND parent_id = ?"
        params.append(parent_id)
    query += " ORDER BY priority DESC, created_at DESC"

    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("No tasks found")
        return

    for row in rows:
        print(f"[{row['id']}] {row['title']} | {row['status']} | priority: {row['priority']}")
        if row['description']:
            print(f"    {row['description'][:100]}...")
        if row['parent_id']:
            print(f"    parent: {row['parent_id']}")
        print()

def update_status(task_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
                  (status, datetime.now().isoformat(), task_id))
    conn.commit()
    conn.close()
    print(f"✅ Updated {task_id} → {status}")

def add_subtask(parent_id, subtask_id, title, description="", priority=5):
    create_task(subtask_id, title, description, assigned_to="PM_Agent", priority=priority, parent_id=parent_id)

def get_task(task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        print(f"Task: {row['id']}")
        print(f"Title: {row['title']}")
        print(f"Description: {row['description']}")
        print(f"Status: {row['status']}")
        print(f"Priority: {row['priority']}")
        print(f"Assigned to: {row['assigned_to']}")
        print(f"Parent: {row['parent_id']}")
        print(f"Created: {row['created_at']}")
        print(f"Updated: {row['updated_at']}")
    else:
        print(f"Task {task_id} not found")

def main():
    if len(sys.argv) < 2:
        print("Usage: task_manager.py <command> [args...]")
        print("Commands:")
        print("  create <id> <title> [--desc <description>] [--priority <n>] [--assigned <name>]")
        print("  list [--assigned <name>] [--status <status>]")
        print("  update <id> <status>")
        print("  subtask <parent_id> <subtask_id> <title> [--desc <description>]")
        print("  get <id>")
        return

    cmd = sys.argv[1]

    if cmd == "create" and len(sys.argv) >= 4:
        task_id = sys.argv[2]
        title = sys.argv[3]
        description = ""
        priority = 5
        assigned_to = "PM_Agent"
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == "--desc" and i + 1 < len(sys.argv):
                description = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            elif sys.argv[i] == "--assigned" and i + 1 < len(sys.argv):
                assigned_to = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        create_task(task_id, title, description, priority=priority, assigned_to=assigned_to)

    elif cmd == "list":
        assigned_to = None
        status = None
        i = 2
        while i < len(sys.argv):
            if sys.argv[i] == "--assigned" and i + 1 < len(sys.argv):
                assigned_to = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--status" and i + 1 < len(sys.argv):
                status = sys.argv[i + 1]
                i += 2
            else:
                i += 1
        list_tasks(assigned_to, status)

    elif cmd == "update" and len(sys.argv) >= 4:
        update_status(sys.argv[2], sys.argv[3])

    elif cmd == "subtask" and len(sys.argv) >= 5:
        parent_id = sys.argv[2]
        subtask_id = sys.argv[3]
        title = sys.argv[4]
        description = ""
        priority = 5
        i = 5
        while i < len(sys.argv):
            if sys.argv[i] == "--desc" and i + 1 < len(sys.argv):
                description = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == "--priority" and i + 1 < len(sys.argv):
                priority = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        add_subtask(parent_id, subtask_id, title, description, priority)

    elif cmd == "get" and len(sys.argv) >= 3:
        get_task(sys.argv[2])

    else:
        print("Unknown command or missing args")

if __name__ == "__main__":
    main()
