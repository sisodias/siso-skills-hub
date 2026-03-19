"""Tests for os-database scripts using --help flag."""
import subprocess
import os
import pytest

SCRIPTS_DIR = os.path.join(
    os.path.dirname(__file__), "..", "scripts"
)


def run_script_help(script_name):
    """Run a script with --help and return result."""
    script_path = os.path.join(SCRIPTS_DIR, script_name)
    return subprocess.run(
        ["python3", script_path, "--help"],
        capture_output=True,
        text=True,
        timeout=10
    )


# === Task CRUD ===
class TestTaskCRUD:
    """Tests for task creation, retrieval, update, delete scripts."""

    def test_create_task_help(self):
        result = run_script_help("create_task.py")
        assert result.returncode == 0

    def test_update_task_help(self):
        result = run_script_help("update_task.py")
        assert result.returncode == 0

    def test_archive_task_help(self):
        result = run_script_help("archive_task.py")
        assert result.returncode == 0

    def test_unarchive_task_help(self):
        result = run_script_help("unarchive_task.py")
        assert result.returncode == 0

    def test_search_tasks_help(self):
        result = run_script_help("search_tasks.py")
        assert result.returncode == 0

    def test_list_archived_help(self):
        result = run_script_help("list_archived.py")
        assert result.returncode == 0


# === Subtasks ===
class TestSubtasks:
    """Tests for subtask management scripts."""

    def test_add_subtask_help(self):
        result = run_script_help("add_subtask.py")
        assert result.returncode == 0

    def test_create_subtask_help(self):
        result = run_script_help("create_subtask.py")
        assert result.returncode == 0

    def test_delete_subtask_help(self):
        result = run_script_help("delete_subtask.py")
        assert result.returncode == 0

    def test_toggle_subtask_help(self):
        result = run_script_help("toggle_subtask.py")
        assert result.returncode == 0

    def test_list_subtasks_help(self):
        result = run_script_help("list_subtasks.py")
        assert result.returncode == 0

    def test_get_task_with_subtasks_help(self):
        result = run_script_help("get_task_with_subtasks.py")
        assert result.returncode == 0


# === Relationships & Blocking ===
class TestRelationships:
    """Tests for task relationship scripts."""

    def test_add_blocked_by_help(self):
        result = run_script_help("add_blocked_by.py")
        assert result.returncode == 0

    def test_relate_tasks_help(self):
        result = run_script_help("relate_tasks.py")
        assert result.returncode == 0

    def test_remove_relationship_help(self):
        result = run_script_help("remove_relationship.py")
        assert result.returncode == 0

    def test_list_relationships_help(self):
        result = run_script_help("list_relationships.py")
        assert result.returncode == 0

    def test_is_blocked_help(self):
        result = run_script_help("is_blocked.py")
        assert result.returncode == 0

    def test_find_blocked_chain_help(self):
        result = run_script_help("find_blocked_chain.py")
        assert result.returncode == 0

    def test_find_blocking_chain_help(self):
        result = run_script_help("find_blocking_chain.py")
        assert result.returncode == 0

    def test_list_blocking_tasks_help(self):
        result = run_script_help("list_blocking_tasks.py")
        assert result.returncode == 0

    def test_unblock_task_help(self):
        result = run_script_help("unblock_task.py")
        assert result.returncode == 0

    def test_propagate_unblock_help(self):
        result = run_script_help("propagate_unblock.py")
        assert result.returncode == 0


# === Tags & Fields ===
class TestTagsAndFields:
    """Tests for tag and field management scripts."""

    def test_add_tag_help(self):
        result = run_script_help("add_tag.py")
        assert result.returncode == 0

    def test_remove_tag_help(self):
        result = run_script_help("remove_tag.py")
        assert result.returncode == 0

    def test_list_tags_help(self):
        result = run_script_help("list_tags.py")
        assert result.returncode == 0

    def test_get_tasks_with_tags_help(self):
        result = run_script_help("get_tasks_with_tags.py")
        assert result.returncode == 0

    def test_add_field_help(self):
        result = run_script_help("add_field.py")
        assert result.returncode == 0

    def test_get_fields_help(self):
        result = run_script_help("get_fields.py")
        assert result.returncode == 0

    def test_set_field_help(self):
        result = run_script_help("set_field.py")
        assert result.returncode == 0

    def test_query_by_field_help(self):
        result = run_script_help("query_by_field.py")
        assert result.returncode == 0


# === Automations ===
class TestAutomations:
    """Tests for automation scripts."""

    def test_create_automation_help(self):
        result = run_script_help("create_automation.py")
        assert result.returncode == 0

    def test_toggle_automation_help(self):
        result = run_script_help("toggle_automation.py")
        assert result.returncode == 0

    def test_list_automations_help(self):
        result = run_script_help("list_automations.py")
        assert result.returncode == 0

    def test_run_automations_help(self):
        result = run_script_help("run_automations.py")
        assert result.returncode == 0


# === Templates ===
class TestTemplates:
    """Tests for template scripts."""

    def test_create_template_help(self):
        result = run_script_help("create_template.py")
        assert result.returncode == 0

    def test_list_templates_help(self):
        result = run_script_help("list_templates.py")
        assert result.returncode == 0

    def test_use_template_help(self):
        result = run_script_help("use_template.py")
        assert result.returncode == 0


# === Session & Agent ===
class TestSessionAndAgent:
    """Tests for session and agent management scripts."""

    def test_init_session_help(self):
        result = run_script_help("init_session.py")
        assert result.returncode == 0

    def test_get_my_tasks_help(self):
        result = run_script_help("get_my_tasks.py")
        assert result.returncode == 0


# === Time Tracking ===
class TestTimeTracking:
    """Tests for time tracking scripts."""

    def test_track_time_help(self):
        result = run_script_help("track_time.py")
        assert result.returncode == 0

    def test_time_report_help(self):
        result = run_script_help("time_report.py")
        assert result.returncode == 0

    def test_estimate_task_help(self):
        result = run_script_help("estimate_task.py")
        assert result.returncode == 0

    def test_compare_estimates_help(self):
        result = run_script_help("compare_estimates.py")
        assert result.returncode == 0

    def test_update_urgency_help(self):
        result = run_script_help("update_urgency.py")
        assert result.returncode == 0


# === Events & Logging ===
class TestEventsAndLogging:
    """Tests for event and logging scripts."""

    def test_log_event_help(self):
        result = run_script_help("log_event.py")
        assert result.returncode == 0

    def test_log_hook_help(self):
        result = run_script_help("log_hook.py")
        assert result.returncode == 0

    def test_recent_events_help(self):
        result = run_script_help("recent_events.py")
        assert result.returncode == 0


# === Task Notes ===
class TestTaskNotes:
    """Tests for task notes scripts."""

    def test_task_notes_help(self):
        result = run_script_help("task_notes.py")
        assert result.returncode == 0


# === Context & Cycle Detection ===
class TestContextAndCycles:
    """Tests for context and cycle detection scripts."""

    def test_query_context_help(self):
        result = run_script_help("query_context.py")
        assert result.returncode == 0

    def test_detect_cycle_help(self):
        result = run_script_help("detect_cycle.py")
        assert result.returncode == 0

    def test_ready_tasks_help(self):
        result = run_script_help("ready_tasks.py")
        assert result.returncode == 0


# === Bulk Operations ===
class TestBulkOperations:
    """Tests for bulk operation scripts."""

    def test_bulk_update_help(self):
        result = run_script_help("bulk_update.py")
        assert result.returncode == 0
