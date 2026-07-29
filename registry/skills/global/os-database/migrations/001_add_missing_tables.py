#!/usr/bin/env python3
"""Migration 001: Add missing tables to os-database.

Tables added:
- automations
- automation_logs
- task_templates
- custom_fields
- custom_field_definitions (alias for custom_fields compatibility)
- custom_field_values
- task_relationships
"""
import sqlite3
import sys
import os

DB_PATH = os.environ.get("SISO_SYSTEM_DB", os.path.expanduser("~/.SystemDB/siso_system.db"))


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    tables_created = []

    # 1. automations table
    if not table_exists(cursor, "automations"):
        cursor.execute("""
            CREATE TABLE automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                trigger_event TEXT NOT NULL,
                trigger_condition TEXT NOT NULL,
                action_type TEXT NOT NULL,
                action_config TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        tables_created.append("automations")
        print("Created table: automations")

    # 2. automation_logs table
    if not table_exists(cursor, "automation_logs"):
        cursor.execute("""
            CREATE TABLE automation_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                automation_id INTEGER NOT NULL,
                trigger_data TEXT,
                action_result TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (automation_id) REFERENCES automations(id)
            )
        """)
        tables_created.append("automation_logs")
        print("Created table: automation_logs")

    # 3. task_templates table
    if not table_exists(cursor, "task_templates"):
        cursor.execute("""
            CREATE TABLE task_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                title_template TEXT NOT NULL,
                description_template TEXT,
                default_priority TEXT DEFAULT 'medium',
                default_tags TEXT,
                default_due_days INTEGER DEFAULT 7,
                subtasks_template TEXT,
                created_by_agent_id TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        tables_created.append("task_templates")
        print("Created table: task_templates")

    # 4. custom_fields table (used by query_by_field.py, set_field.py)
    if not table_exists(cursor, "custom_fields"):
        cursor.execute("""
            CREATE TABLE custom_fields (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                field_type TEXT NOT NULL,
                description TEXT,
                is_global INTEGER DEFAULT 0,
                project_id TEXT,
                options TEXT,
                is_required INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        tables_created.append("custom_fields")
        print("Created table: custom_fields")

    # 5. custom_field_definitions table (alias for compatibility with get_fields.py)
    if not table_exists(cursor, "custom_field_definitions"):
        cursor.execute("""
            CREATE TABLE custom_field_definitions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                field_key TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                field_type TEXT NOT NULL,
                description TEXT,
                is_global INTEGER DEFAULT 0,
                project_id TEXT,
                options TEXT,
                is_required INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        tables_created.append("custom_field_definitions")
        print("Created table: custom_field_definitions")

    # 6. custom_field_values table
    if not table_exists(cursor, "custom_field_values"):
        cursor.execute("""
            CREATE TABLE custom_field_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT NOT NULL,
                field_id INTEGER NOT NULL,
                value TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (field_id) REFERENCES custom_fields(id),
                FOREIGN KEY (field_id) REFERENCES custom_field_definitions(id),
                UNIQUE(task_id, field_id)
            )
        """)
        tables_created.append("custom_field_values")
        print("Created table: custom_field_values")

    # 7. task_relationships table
    if not table_exists(cursor, "task_relationships"):
        cursor.execute("""
            CREATE TABLE task_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_task_id TEXT NOT NULL,
                to_task_id TEXT NOT NULL,
                relationship_type TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        tables_created.append("task_relationships")
        print("Created table: task_relationships")

    conn.commit()
    conn.close()

    if tables_created:
        print(f"\nMigration complete. Created {len(tables_created)} table(s): {', '.join(tables_created)}")
    else:
        print("No tables needed to be created (all already exist).")

    return tables_created


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        sys.exit(1)
