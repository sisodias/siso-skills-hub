"""Tests for os-database schema verification."""
import sqlite3
import os
import pytest


def get_db_path():
    """Get the database path from environment or default."""
    db_path = os.path.expanduser("~/.SystemDB/siso_system.db")
    return db_path


def get_connection():
    """Get a database connection."""
    db_path = get_db_path()
    return sqlite3.connect(db_path)


class TestCoreTables:
    """Verify core tables exist in the database."""

    def test_tasks_table_exists(self):
        """Verify tasks table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "tasks table should exist"

    def test_agents_table_exists(self):
        """Verify agents table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='agents'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "agents table should exist"

    def test_projects_table_exists(self):
        """Verify projects table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='projects'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "projects table should exist"

    def test_timeline_events_table_exists(self):
        """Verify timeline_events table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='timeline_events'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "timeline_events table should exist"

    def test_sessions_table_exists(self):
        """Verify sessions table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='sessions'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "sessions table should exist"

    def test_workspaces_table_exists(self):
        """Verify workspaces table exists."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table' AND name='workspaces'
        """)
        result = cursor.fetchone()
        conn.close()
        assert result is not None, "workspaces table should exist"


class TestTableSchemas:
    """Verify core table schemas have expected columns."""

    def test_tasks_has_required_columns(self):
        """Verify tasks table has required columns."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns, "tasks should have id column"
        assert "title" in columns, "tasks should have title column"
        assert "status" in columns, "tasks should have status column"

    def test_agents_has_required_columns(self):
        """Verify agents table has required columns."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(agents)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns, "agents should have id column"
        assert "role" in columns, "agents should have role column"

    def test_timeline_events_has_required_columns(self):
        """Verify timeline_events table has required columns."""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(timeline_events)")
        columns = {row[1] for row in cursor.fetchall()}
        conn.close()
        assert "id" in columns, "timeline_events should have id column"
        assert "agent_id" in columns, "timeline_events should have agent_id column"
        assert "event_type" in columns, "timeline_events should have event_type column"
        assert "message" in columns, "timeline_events should have message column"
