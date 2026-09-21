#!/usr/bin/env python3
import json
import sys
from pathlib import Path
import tempfile
import unittest

SKILL = Path(__file__).parents[1]
sys.path.insert(0, str(SKILL))
import context


def packet():
    return {"request": "fix the parser", "blocks": [
        {"id": "p", "source": "user", "text": "keep this decision", "pinned": True},
        {"id": "e", "source": "stderr", "text": "Error: bad token"},
        {"id": "a", "source": "tool", "text": "unrelated background"},
    ]}


class ContextTests(unittest.TestCase):
    def test_shadow_scores_and_preserves_evidence(self):
        calls = []
        def ask(state, questions, timeout):
            calls.append((state, questions, timeout))
            self.assertEqual(set(questions), {"c0"})
            self.assertIn("candidate block c0", questions["c0"]["instructions"])
            self.assertIn("'a'", questions["c0"]["instructions"])
            return {"answers": {"c0": {"type": "noul", "noul": 0.05}}, "usage": {"cost": 0.01}, "_ms": 12}
        result = context.evaluate(packet(), ask=ask)
        self.assertEqual(result["would_hide_ids"], ["a"])
        self.assertEqual(result["keep_ids"], ["p", "e"])
        self.assertEqual(result["potential_hidden_chars"], len("unrelated background"))
        self.assertEqual(len(calls), 1)
        self.assertTrue(result["shadow"])

    def test_malformed_response_keeps_all(self):
        result = context.evaluate(packet(), ask=lambda *a, **k: {"answers": {}})
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["would_hide_ids"], [])
        self.assertEqual(result["keep_ids"], ["p", "e", "a"])
        self.assertIsNone(result["cost"])

    def test_missing_usage_cost_remains_unknown(self):
        result = context.evaluate(packet(), ask=lambda *a, **k: {
            "answers": {"c0": {"type": "noul", "noul": 0.5}}, "_ms": 3})
        self.assertIsNone(result["cost"])

    def test_dry_run_no_provider(self):
        result = context.evaluate(packet(), dry_run=True, ask=lambda *a, **k: self.fail("called"))
        self.assertEqual(result["api_calls"], 0)
        self.assertEqual(result["keep_ids"], ["p", "e", "a"])

    def test_evaluation_does_not_mutate_input_file(self):
        payload = json.dumps(packet())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "packet.json"
            path.write_text(payload, encoding="utf-8")
            before = path.read_bytes()
            result = context.evaluate(json.loads(path.read_text(encoding="utf-8")), dry_run=True)
            self.assertEqual(result["status"], "dry_run")
            self.assertEqual(path.read_bytes(), before)

    def test_schema_bounds_and_credentials(self):
        with self.assertRaises(ValueError):
            context.validate({"request": "x", "blocks": [{"id": "a", "source": "s", "text": "x"}, {"id": "a", "source": "s", "text": "y"}]})
        with self.assertRaises(ValueError):
            fake_key = "sk" + "-or-v1-" + "abcdefghijklmnop"
            context.validate({"request": "x", "blocks": [{"id": "a", "source": "s", "text": fake_key}]})
        with self.assertRaises(ValueError):
            context.validate({"request": "x", "blocks": [{"id": "a", "source": "s", "text": "x", "pinned": "yes"}]})

    def test_missing_and_uncertain_scores_keep(self):
        for response in ({"answers": {"a": {"type": "noul"}}}, {"answers": {"a": {"type": "noul", "noul": 1.2}}}):
            result = context.evaluate(packet(), ask=lambda *a, response=response, **k: response)
            self.assertEqual(result["would_hide_ids"], [])

    def test_bounds(self):
        blocks = [{"id": str(i), "source": "s", "text": "x"} for i in range(25)]
        with self.assertRaises(ValueError):
            context.validate({"request": "x", "blocks": blocks})
        with self.assertRaises(ValueError):
            context.validate({"request": "x", "blocks": [{"id": "a", "source": "s", "text": "x" * 18_001}]})


if __name__ == "__main__":
    unittest.main()
