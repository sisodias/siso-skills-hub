#!/usr/bin/env python3
"""Manage task notes."""
import sqlite3
import json
import os
import sys
from datetime import datetime, timezone

# Import shared config from scripts directory
_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def ensure_notes_table(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS task_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_note(task_id: str, content: str):
    config = load_config()
    db_path = config.get("db_path")

    init_table(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()

    cursor.execute("""
        INSERT INTO task_notes (task_id, content, created_at)
        VALUES (?, ?, ?)
    """, (task_id, content, now))

    note_id = cursor.lastrowid
    conn.commit()
    conn.close()

    print(json.dumps({
        "status": "success",
        "note_id": note_id,
        "task_id": task_id,
        "message": f"Note added to {task_id}"
    }))


def list_notes(task_id: str):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, task_id, content, created_at
        FROM task_notes
        WHERE task_id = ?
        ORDER BY created_at DESC
    """, (task_id,))

    rows = cursor.fetchall()
    conn.close()

    notes = []
    for row in rows:
        notes.append({
            "id": row[0],
            "task_id": row[1],
            "content": row[2],
            "created_at": row[3]
        })

    print(json.dumps({
        "status": "success",
        "task_id": task_id,
        "count": len(notes),
        "notes": notes
    }))


def delete_note(note_id: int):
    config = load_config()
    db_path = config.get("db_path")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM task_notes WHERE id = ?", (note_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()

    if deleted > 0:
        print(json.dumps({
            "status": "success",
            "note_id": note_id,
            "message": f"Note {note_id} deleted"
        }))
    else:
        print(json.dumps({
            "status": "error",
            "note_id": note_id,
            "message": f"Note {note_id} not found"
        }))
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    # add subcommand
    add_parser = subparsers.add_parser("add", help="Add a note to a task")
    add_parser.add_argument("--task-id", required=True, help="Task ID")
    add_parser.add_argument("--content", required=True, help="Note content")

    # list subcommand
    list_parser = subparsers.add_parser("list", help="List notes for a task")
    list_parser.add_argument("--task-id", required=True, help="Task ID")

    # delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a note")
    delete_parser.add_argument("--note-id", type=int, required=True, help="Note ID to delete")

    args = parser.parse_args()

    if args.action == "add":
        add_note(args.task_id, args.content)
    elif args.action == "list":
        list_notes(args.task_id)
    elif args.action == "delete":
        delete_note(args.note_id)
