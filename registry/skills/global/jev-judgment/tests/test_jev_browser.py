import importlib.util
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("jev_browser", ROOT / "browser.py")
browser = importlib.util.module_from_spec(spec)
spec.loader.exec_module(browser)

class FakeClient:
    def __init__(self, before, links, *, tabs=None, fresh=None, fresh_links=None, after=None, readback_error=None, post_error=None):
        self.before, self.links = before, links
        self.tabs = tabs if tabs is not None else [{"tabId": "tab1", "listItemId": "sess1"}]
        self.fresh, self.fresh_links, self.after = fresh, fresh_links, after
        self.readback_error, self.post_error = readback_error, post_error
        self.calls = []
    def call(self, method, path, **fields):
        self.calls.append((method, path, fields))
        if (method, path) == ("GET", "/tabs"): return {"tabs": self.tabs}
        if path.endswith("/snapshot"):
            snapshots = sum(c[1].endswith("/snapshot") for c in self.calls)
            if self.after is not None and any(c[0] == "POST" for c in self.calls):
                if self.readback_error: raise self.readback_error
                return self.after
            return self.fresh if self.fresh is not None and snapshots > 1 else self.before
        if path.endswith("/links"):
            snapshots = sum(c[1].endswith("/snapshot") for c in self.calls)
            return self.fresh_links if self.fresh_links is not None and snapshots > 1 else self.links
        if (method, path) == ("POST", "/tabs/tab1/navigate"):
            if self.post_error: raise self.post_error
            return {"ok": True}
        raise AssertionError((method, path, fields))

def ask_selected():
    def ask(state, questions, timeout=8):
        ask.calls += 1
        return {"answers": {k: {"type": "noul", "noul": 0.95 if k == "c0" else 0.05} for k in questions}, "usage": {"cost": 0.00001}}
    ask.calls = 0
    return ask

class BrowserAdapterTests(unittest.TestCase):
    def packet(self, prefixes=None):
        return {"request": "Read the next in-scope page", "user_id": "user1", "session_key": "sess1", "tab_id": "tab1", "allowed_prefixes": prefixes or ["https://example.test/docs"]}
    def page(self, url="https://example.test/docs/start", snapshot="start"):
        return {"url": url, "snapshot": snapshot, "totalChars": len(snapshot)}
    def links(self, urls, has_more=False):
        return {"links": [{"url": u, "text": u.rsplit("/", 1)[-1]} for u in urls], "pagination": {"hasMore": has_more}}

    def test_scope_and_boundary(self):
        got = browser.candidates(self.links(["https://example.test/docs/next", "https://example.test/docsity/no", "https://other.test/docs/no", "https://example.test/docs/next"]), "https://example.test/docs/start", self.packet()["allowed_prefixes"])
        self.assertEqual([c["details"]["url"] for c in got], ["https://example.test/docs/next"])

    def test_url_scope_rejects_credentials_scripts_traversal_and_host_confusion(self):
        prefix = ["https://example.test/docs"]
        for value in ("https://user:pass@example.test/docs/x", "javascript:alert(1)",
                      "https://example.test/docs/%2e%2e/admin", "https://example.test/docs.evil/x"):
            self.assertFalse(browser.in_scope(value, prefix), value)

    def test_stale_page_or_removed_target_aborts(self):
        before = self.page(snapshot="before")
        client = FakeClient(before, self.links(["https://example.test/docs/next"]), fresh=self.page(snapshot="changed"))
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())
        self.assertEqual(result["reason"], "page_changed_before_navigation")
        self.assertFalse(any(c[0] == "POST" for c in client.calls))
        client = FakeClient(before, self.links(["https://example.test/docs/next"]), fresh=before,
                            fresh_links=self.links(["https://example.test/docs/other"]))
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())
        self.assertEqual(result["reason"], "page_changed_before_navigation")
        self.assertFalse(any(c[0] == "POST" for c in client.calls))

    def test_uncertain_and_malformed_model_do_not_navigate(self):
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]))
        def uncertain(state, questions, timeout=8):
            uncertain.calls += 1
            return {"answers": {key: {"type": "noul", "noul": 0.5} for key in questions}}
        uncertain.calls = 0
        result = browser.run(self.packet(), navigate=True, client=client, ask=uncertain)
        self.assertNotEqual(result.get("verdict"), "navigated")
        self.assertFalse(any(c[0] == "POST" for c in client.calls))
        self.assertEqual(uncertain.calls, 1)
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]))
        result = browser.run(self.packet(), navigate=True, client=client, ask=lambda *a, **k: {"answers": {}})
        self.assertNotEqual(result.get("verdict"), "navigated")
        self.assertFalse(any(c[0] == "POST" for c in client.calls))

    def test_session_redirect_and_readback(self):
        client = FakeClient(self.page(), self.links([]), tabs=[{"tabId": "tab1", "listItemId": "other"}])
        with self.assertRaises(ValueError): browser.run(self.packet(), client=client, ask=ask_selected())
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]), after=self.page("https://evil.test/out", "redirect"))
        self.assertEqual(browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())["reason"], "redirect_outside_scope")
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]), after=self.page(), readback_error=OSError("gone"))
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())
        self.assertEqual((result["status"], result["reason"]), ("unavailable", "navigation_readback_failed"))

    def test_post_error_and_readback_state(self):
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]), post_error=OSError("post failed"))
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())
        self.assertIsNone(result["navigated"])
        self.assertEqual(result["reason"], "navigation_not_confirmed")
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]), after=self.page(), readback_error=OSError("gone"))
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask_selected())
        self.assertTrue(result["navigated"])

    def test_one_call_and_readback(self):
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]), after=self.page("https://example.test/docs/next", "next page"))
        ask = ask_selected()
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask)
        self.assertEqual(result["verdict"], "navigated")
        self.assertEqual(ask.calls, 1)
        self.assertEqual(sum(c[0] == "POST" for c in client.calls), 1)
        self.assertEqual(result["after_url"], "https://example.test/docs/next")

    def test_choose_only_and_empty_candidates_make_no_post_or_model_call(self):
        client = FakeClient(self.page(), self.links(["https://example.test/docs/next"]))
        ask = ask_selected()
        result = browser.run(self.packet(), navigate=False, client=client, ask=ask)
        self.assertFalse(result["navigated"])
        self.assertEqual(ask.calls, 1)
        self.assertFalse(any(c[0] == "POST" for c in client.calls))
        client = FakeClient(self.page(), self.links([])); ask = ask_selected()
        result = browser.run(self.packet(), navigate=True, client=client, ask=ask)
        self.assertEqual(result["verdict"], "no_match")
        self.assertEqual(ask.calls, 0)
        self.assertFalse(any(c[0] == "POST" for c in client.calls))

    def test_dry_run_and_bounds(self):
        client = FakeClient(self.page(), self.links([])); ask = ask_selected()
        result = browser.run(self.packet(), dry_run=True, client=client, ask=ask)
        self.assertEqual(result, {"status": "dry_run", "api_calls": 0, "browser_calls": 0})
        self.assertEqual(client.calls, [])
        self.assertEqual(ask.calls, 0)
        with self.assertRaises(ValueError): browser.candidates(self.links([f"https://example.test/docs/{i}" for i in range(25)]), "https://example.test/docs/start", self.packet()["allowed_prefixes"])
        with self.assertRaises(ValueError): browser.candidates(self.links(["https://example.test/docs/next"], has_more=True), "https://example.test/docs/start", self.packet()["allowed_prefixes"])
        bad = self.packet(); bad["request"] = "x" * 2001
        with self.assertRaises(ValueError): browser.validate(bad)

if __name__ == "__main__":
    unittest.main()
