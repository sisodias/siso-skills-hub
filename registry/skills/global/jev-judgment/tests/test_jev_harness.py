#!/usr/bin/env python3
"""Offline behavioural invariants for the optional Jev harness skill."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT
sys.path.insert(0, str(SKILL))
import harness
import jev


def response(**scores):
    return {"answers": {k: {"type": "noul", "noul": v} for k, v in scores.items()},
            "usage": {"cost": 0.00001}, "_ms": 500, "model": "fixture"}


def complete_packet():
    return {"request": "Fix the calculation and verify it with a regression test.",
            "requirements": [{"id": "fix", "text": "The calculation returns the expected result.",
                              "evidence": [{"source": "test receipt", "text": "Regression input returned the expected result; test passed."}]}],
            "checks": [{"name": "regression", "passed": True}]}


def selection_packet():
    return {"request": "Read two files and return their differences.", "criteria": "A bounded read-only worker is sufficient.",
            "candidates": [{"id": "reader", "description": "Bounded read-only worker", "eligible": True},
                           {"id": "writer", "description": "Implementation worker", "eligible": True}]}


class HarnessChecks(unittest.TestCase):
    def test_explicit_override_never_calls_model(self):
        packet = selection_packet(); packet["override_id"] = "writer"
        call = Mock(side_effect=AssertionError("no inference"))
        result = harness.run("route", packet, ask=call)
        self.assertEqual(result["selected_id"], "writer")
        self.assertEqual(result["cost_usd"], 0)
        call.assert_not_called()

    def test_ineligible_override_is_not_silently_replaced(self):
        packet = selection_packet(); packet["override_id"] = "writer"
        packet["candidates"][1]["eligible"] = False
        result = harness.run("route", packet, ask=Mock(side_effect=AssertionError()))
        self.assertIsNone(result["selected_id"])
        self.assertEqual(result["reason"], "override_ineligible")

    def test_unknown_override_is_rejected(self):
        packet = selection_packet(); packet["override_id"] = "invented-model"
        with self.assertRaises(ValueError): harness.run("route", packet, dry_run=True)

    def test_ineligible_candidates_never_enter_request(self):
        packet = selection_packet(); packet["candidates"][1]["eligible"] = False
        call = Mock(return_value=response(c0=0.95))
        result = harness.run("select", packet, ask=call)
        self.assertEqual(result["selected_id"], "reader")
        self.assertEqual([c["id"] for c in call.call_args.args[0]["candidates"]], ["reader"])
        self.assertEqual(len(packet["candidates"]), 2)

    def test_tie_and_weak_fit_abstain(self):
        for values, verdict in [((0.95, 0.93), "uncertain"), ((0.25, 0.1), "no_match")]:
            result = harness.run("route", selection_packet(), ask=Mock(return_value=response(c0=values[0], c1=values[1])))
            self.assertIsNone(result["selected_id"])
            self.assertEqual(result["verdict"], verdict)

    def test_empty_eligible_pool_does_not_call_provider(self):
        packet = selection_packet()
        for candidate in packet["candidates"]: candidate["eligible"] = False
        result = harness.run("select", packet, ask=Mock(side_effect=AssertionError()))
        self.assertEqual(result["verdict"], "no_match")

    def test_duplicate_candidate_id_is_not_ambiguous(self):
        packet = selection_packet(); packet["candidates"][1]["id"] = "reader"
        with self.assertRaises(ValueError): harness.run("select", packet, dry_run=True)

    def test_missing_eligibility_must_be_established_by_caller(self):
        packet = selection_packet(); del packet["candidates"][0]["eligible"]
        with self.assertRaises(ValueError): harness.run("select", packet, dry_run=True)

    def test_known_failed_test_blocks_completion_without_inference(self):
        packet = complete_packet(); packet["checks"][0]["passed"] = False
        result = harness.run("complete", packet, ask=Mock(side_effect=AssertionError()))
        self.assertEqual(result["verdict"], "incomplete")
        self.assertEqual(result["failed_checks"], ["regression"])

    def test_open_work_and_missing_receipts_cannot_be_complete(self):
        packet = complete_packet(); packet["open_items"] = ["Run the requested check"]
        packet["requirements"][0]["evidence"] = []
        result = harness.run("complete", packet, ask=Mock(side_effect=AssertionError()))
        self.assertEqual(result["verdict"], "incomplete")
        self.assertEqual(result["missing_evidence"], ["fix"])
        self.assertEqual(result["open_item_count"], 1)

    def test_uncovered_user_request_prevents_all_clear(self):
        result = harness.run("complete", complete_packet(), ask=Mock(return_value=response(omission=0.8, r0_support=0.99, r0_contradiction=0.01)))
        self.assertEqual(result["verdict"], "incomplete")

    def test_contradictory_receipt_beats_positive_support(self):
        result = harness.run("complete", complete_packet(), ask=Mock(return_value=response(omission=0.05, r0_support=0.98, r0_contradiction=0.8)))
        self.assertEqual(result["verdict"], "incomplete")

    def test_completion_supported_is_only_advisory(self):
        result = harness.run("complete", complete_packet(), ask=Mock(return_value=response(omission=0.05, r0_support=0.95, r0_contradiction=0.01)))
        self.assertEqual(result["verdict"], "completion_supported")
        self.assertTrue(result["advisory"])
        self.assertNotIn("completed", result)

    def test_uncertain_evidence_does_not_complete(self):
        result = harness.run("complete", complete_packet(), ask=Mock(return_value=response(omission=0.1, r0_support=0.7, r0_contradiction=0.1)))
        self.assertEqual(result["verdict"], "uncertain")
        self.assertEqual(result["unresolved_ids"], ["fix"])

    def test_scope_violation_overrides_goal_alignment(self):
        packet = {"request": "Prepare a local preview", "plan": "Prepare and deploy publicly"}
        result = harness.run("intent", packet, ask=Mock(return_value=response(aligned=0.95, violation=0.9, omission=0.05)))
        self.assertEqual(result["verdict"], "mismatch")

    def test_new_evidence_is_progress_not_a_repeat(self):
        packet = {"request": "Diagnose a failing test", "attempts": [
            {"action": "Read failure", "observation": "Found missing fixture"},
            {"action": "Inspect fixture path", "observation": "Fixture uses a different filename"}]}
        result = harness.run("progress", packet, ask=Mock(return_value=response(progress=0.9, repeating=0.1, external_blocker=0.1)))
        self.assertEqual(result["verdict"], "progressing")

    def test_stuck_signal_does_not_dispatch_or_cancel(self):
        packet = {"request": "Fix a test", "attempts": [
            {"action": "Run unchanged test", "observation": "Same assertion failure"}]*3}
        result = harness.run("progress", packet, ask=Mock(return_value=response(progress=0.1, repeating=0.95, external_blocker=0.1)))
        self.assertEqual(result["verdict"], "stuck_signal")
        self.assertTrue(result["advisory"])

    def test_malformed_answers_fail_closed(self):
        bad = [None, [], {}, {"answers": {}}, response(c0=True, c1=0.1),
               response(c0=float("nan"), c1=0.1), response(c0=1.1, c1=0.1),
               response(c0=0.9, c1=0.1, invented=0.99)]
        for output in bad:
            with self.subTest(output=output):
                result = harness.run("select", selection_packet(), ask=Mock(return_value=output))
                self.assertEqual(result["status"], "unavailable")
                self.assertNotIn("selected_id", result)

    def test_network_failure_never_echoes_exception_text(self):
        result = harness.run("select", selection_packet(), ask=Mock(side_effect=OSError("private request content")))
        self.assertEqual(result["status"], "unavailable")
        self.assertNotIn("private request", json.dumps(result))

    def test_oversized_and_unknown_fields_rejected(self):
        packet = selection_packet(); packet["request"] = "x"*18001
        with self.assertRaises(ValueError): harness.run("route", packet, dry_run=True)
        packet = selection_packet(); packet["auto_execute"] = True
        with self.assertRaises(ValueError): harness.run("route", packet, dry_run=True)

    def test_common_credential_material_is_rejected(self):
        packet = selection_packet(); packet["request"] = "-----BEGIN " + "PRIVATE KEY-----"
        with self.assertRaises(ValueError): harness.run("route", packet, dry_run=True)

    def test_dry_run_works_from_installed_copy_without_credentials(self):
        import shutil
        with tempfile.TemporaryDirectory() as directory:
            installed = Path(directory)/"jev-judgment"
            shutil.copytree(SKILL, installed, ignore=shutil.ignore_patterns(".git", "__pycache__"))
            result = subprocess.run([sys.executable, str(installed/"harness.py"), "route", "--dry-run"],
                                    input=json.dumps(selection_packet()), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["api_calls"], 0)

    def test_cli_rejects_invalid_json_without_traceback(self):
        result = subprocess.run([sys.executable, str(SKILL/"harness.py"), "intent"], input="{bad", capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(json.loads(result.stdout)["status"], "invalid_input")
        self.assertEqual(result.stderr, "")

    def test_direct_typesafe_key_never_sent_to_openrouter(self):
        with patch.object(jev, "_load_env"), patch.dict(os.environ, {"TYPESAFE_API_KEY": "fixture"}, clear=True), patch.object(jev.urllib.request, "urlopen") as send:
            with self.assertRaises(RuntimeError): jev.ask({}, {})
            send.assert_not_called()

    def test_openrouter_key_is_not_sent_to_custom_host(self):
        with patch.object(jev, "_load_env"), patch.dict(os.environ, {"OPENROUTER_API_KEY": "fixture"}, clear=True), patch.object(jev.urllib.request, "urlopen") as send:
            with self.assertRaises(ValueError): jev.ask({}, {}, url="https://example.invalid/collect")
            send.assert_not_called()


if __name__ == "__main__":
    unittest.main()
