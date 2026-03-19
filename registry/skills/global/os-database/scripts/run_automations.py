#!/usr/bin/env python3
"""Run automations for a given event and data."""
import sqlite3
import json
import os
import sys
import uuid
from datetime import datetime, timezone

_SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _SCRIPT_DIR)
from _shared_config import load_config


def evaluate_condition(condition: dict, data: dict) -> bool:
    field = condition.get("field")
    op = condition.get("op")
    value = condition.get("value")

    if not field or field not in data:
        return False

    data_value = data[field]

    if op == "eq":
        return data_value == value
    elif op == "ne":
        return data_value != value
    elif op == "gt":
        return data_value > value
    elif op == "lt":
        return data_value < value
    elif op == "contains":
        return value in str(data_value)
    elif op == "in":
        return data_value in value if isinstance(value, list) else False
    return False


def execute_action(action_type: str, action_config: dict, automation_id: int, data: dict, db_path: str) -> str:
    result = {"executed": True}

    if action_type == "log":
        event_type = action_config.get("event_type", "ACTION")
        msg = action_config.get("msg", "Automation triggered")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM agents LIMIT 1")
        row = cursor.fetchone()
        agent_id = row[0] if row else "SYSTEM"

        cursor.execute("""INSERT INTO timeline_events (id, agent_id, event_type, message, timestamp)
                          VALUES (?, ?, ?, ?, ?)""",
                       (f"EVT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}", agent_id, event_type, msg, datetime.now(timezone.utc).isoformat()))
        conn.commit()
        conn.close()
        result["logged"] = True
        result["message"] = msg

    elif action_type == "alert":
        result["alert"] = True
        result["message"] = action_config.get("msg", "Alert triggered")

    elif action_type == "escalate":
        result["escalated"] = True
        result["message"] = f"Escalation: {action_config.get('reason', 'Automation triggered')}"

    return json.dumps(result)


def run_automations(event: str, data_json: str):
    config = load_config()
    db_path = config.get("db_path")

    data = json.loads(data_json) if data_json else {}

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""SELECT id, name, trigger_condition, action_type, action_config
                      FROM automations WHERE trigger_event = ? AND enabled = 1""",
                   (event,))
    automations = cursor.fetchall()

    executed = []
    for auto in automations:
        automation_id, name, trigger_condition, action_type, action_config = auto

        try:
            condition = json.loads(trigger_condition)
            if evaluate_condition(condition, data):
                action_cfg = json.loads(action_config)
                result = execute_action(action_type, action_cfg, automation_id, data, db_path)

                cursor.execute("""INSERT INTO automation_logs (automation_id, trigger_data, action_result)
                                  VALUES (?, ?, ?)""",
                               (automation_id, data_json, result))

                executed.append({
                    "automation_id": automation_id,
                    "name": name,
                    "result": result
                })
        except json.JSONDecodeError as e:
            print(f"Error parsing condition for automation {automation_id}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error executing automation {automation_id}: {e}", file=sys.stderr)

    conn.commit()
    conn.close()

    print(json.dumps({"event": event, "executed": executed}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--event", required=True, help="Event that triggered this")
    parser.add_argument("--data", required=True, help="JSON data for the event")
    args = parser.parse_args()

    run_automations(args.event, args.data)
