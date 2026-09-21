# Camofox navigation and bounded loops with Jev

Use this for semantic link selection on a page your task already owns. The
adapter reads Camofox locally and gives the parent agent a short receipt. It
does not need the parent to paste a snapshot or construct each link candidate.

## Packet and invocation

Open a dedicated tab through the existing Camofox skill or REST API. Use a unique
task `userId` and `sessionKey` for public research; do not borrow another agent's
tab or authenticated session. With the current API, `POST /tabs` takes
`{"userId":"task-reader","sessionKey":"docs","url":"https://example.com/docs/"}`
and returns `tabId`. The caller closes the tab when its task is finished.

```json
{
  "request": "Open the guide explaining how to export the component catalog.",
  "user_id": "task-reader",
  "session_key": "docs",
  "tab_id": "replace-with-the-returned-tab-id",
  "allowed_prefixes": ["https://example.com/docs/"]
}
```

```sh
python3 <skill-dir>/browser.py packet.json --dry-run
python3 <skill-dir>/browser.py packet.json
python3 <skill-dir>/browser.py packet.json --navigate
```

These are alternative modes, not a three-call ritual. `--dry-run` validates with
zero browser/model calls. Default mode selects without navigating. `--navigate`
selects and follows one link in a single invocation; it does not repeat a prior
selection. Each non-dry run uses at most one Jev request. Packet `-` reads stdin.

Use narrow prefixes for pages reviewed as ordinary read-only navigation, such as
a documentation directory. Prefix comparison uses scheme, host, port and path
boundaries: `/docs` never permits `/docs-admin`. A prefix does not establish that
all URLs beneath it are harmless. Never include account actions, purchases,
logout, deletion, email/message sends or other state-changing GET endpoints.
If the next action is already determined by an exact URL or rule, use Camofox
directly and skip Jev.

## What it does

1. Verify the tab belongs to the supplied user and session group.
2. Fetch the current accessibility snapshot and up to 100 observed links.
3. Filter links against the supplied prefixes, deduplicate URLs, and exclude the
   current URL. More than 24 eligible links or incomplete link pagination defers
   to the caller; candidates are not silently dropped to make them fit.
4. Send the exact task, at most 3,000 characters of page context, and the eligible
   links to the existing Jev selector. Page context is a marked head/tail excerpt;
   request text and candidate records are not truncated to fit a request.
5. Require the existing selector's 0.85 score floor and 0.15 lead. These are
   conservative starting values, not calibrated correctness probabilities.
6. With `--navigate`, fetch the page and links again. If the page changed or the
   selected URL disappeared, stop. Otherwise navigate to that observed URL and
   return at most 2,500 characters of destination text with its actual URL.

`verdict: navigated` reports a browser operation and readback, not fulfillment of
the user's overall task. Check the returned content and gather any further
evidence with the normal browser workflow. An uncertain result, changed page,
large page/link inventory or unsupported UI action goes back to that workflow;
do not keep calling Jev until it agrees. There is no autonomous loop or retry.

The same tab must have one writer. Freshness checking reduces stale actions but
cannot make the separate HTTP requests atomic. A server redirect may leave the
permitted area before readback detects it; `redirect_outside_scope` stops the
adapter and withholds that page's content. This is not a browser network sandbox.
If a navigation request times out, `navigated: null` means inspect the tab before
retrying. A readback failure after a successful navigation keeps `navigated: true`.

## Existing service and credentials

The default Camofox origin is `http://127.0.0.1:9377`. `CAMOFOX_URL` can point to
another loopback origin. HTTP redirects and environment proxies are disabled for
the service API client. If the local service requires its global access key,
supply `CAMOFOX_ACCESS_KEY` in the process environment. Never put it in a packet.
The adapter does not import cookies, open accounts, launch a daemon or install a
browser. Jev uses the existing OpenRouter credential through `jev.py`.

`browser.py` supports navigation links. For permitted fields and buttons use the
separate bounded loop below. Visual/canvas interfaces, screenshots, logins and
other controls need the existing browser tools. The Chrome, CMUX and Codex browser tools have no automatic Jev
interception. Use Camofox for an appropriate task rather than replacing an
explicitly selected browser.

Page excerpts and link labels/URLs are sent to OpenRouter. Use only content
appropriate for that provider; omit credential pages and unrelated private
material. The existing common-key check is not a comprehensive secret detector.
The adapter writes no trace files; Camofox retains its own existing service logs.

## Evidence and limits

On 21 September 2026, the adapter navigated an actual Camofox tab on a disposable
local project-reference site. It chose the export guide from three permitted
links, excluded an account-action URL outside `/docs/`, and read back the expected
heading. The task tab was closed afterward.

- Source snapshot: 12,282 characters.
- Jev decision state: 4,049 characters, plus the selector's question instructions.
- Parent result: 598 characters (about 95% fewer characters than that snapshot).
- One API call: reported $0.000060732; 3,996 ms for Jev, 4,886 ms for the workflow.

This is a functional test on one synthetic site, not a production cost, token,
speed or reliability benchmark. The independent offline suite tests scope,
freshness, uncertainty, response failures and bounded behavior. Existing source:
[Camofox](https://github.com/jo-inc/camofox-browser); related public experiment:
[browser-use/jev-ultrafast](https://github.com/browser-use/jev-ultrafast).

## Bounded search/navigation loop (`browser_loop.py`, version 1.3)

This adapter keeps intermediate page reads and action selection inside a small
local loop. The parent supplies the goal, the text to fill, the exact buttons it
permits and a success condition. Jev chooses among observed actions; it cannot
invent field text, selectors, permissions or a completion verdict.

```json
{
  "request": "Search project docs for export, then open the component export guide.",
  "user_id": "task-reader",
  "session_key": "docs",
  "tab_id": "replace-with-the-returned-tab-id",
  "allowed_prefixes": ["https://example.com/docs/"],
  "max_steps": 4,
  "max_seconds": 90,
  "controls": [
    {"id": "query", "kind": "fill", "role": "textbox", "name": "Search docs", "text": "export", "url_prefix": "https://example.com/docs/"},
    {"id": "search", "kind": "click", "role": "button", "name": "Search", "after": ["query"], "url_prefix": "https://example.com/docs/"}
  ],
  "success": {"url_prefix": "https://example.com/docs/export", "snapshot_contains": ["Export the component catalog"]}
}
```

```sh
python3 <skill-dir>/browser_loop.py packet.json --dry-run
# When the packet's controls and URL scope match the authorised task:
python3 <skill-dir>/browser_loop.py packet.json
```

Default execution runs the loop; dry-run makes zero browser/model calls. The tab
must already exist under the supplied task user/session. The caller closes it.
Use the existing browser workflow to open it; a cold Camofox context can take
longer than an ordinary tab operation.

- Budget: default 4 actions/90 seconds; maxima 8/180. No new step or action begins
  after the elapsed-time check expires. This is a start budget, not a hard process
  deadline: an in-flight browser request has a 15-second timeout and inference an
  8-second timeout. Each step makes at most one inference request, with no retry.
- Controls: up to 12 explicitly permitted named textboxes/searchboxes and buttons,
  within a per-control URL prefix. `after` names earlier controls that must have
  run. Each control is used once; filling does not submit. Use these for approved
  search/filter flows, never as blanket authority to click every matching button.
  Comboboxes, file uploads, login/password entry and arbitrary selectors are not
  supported. Do not supply secret or unrelated private field text.
- Actions come from complete snapshots and observed links. Ambiguous names,
  disabled controls, oversized inventories and truncated snapshots defer. Fresh
  snapshot and target checks run immediately before each action. Keep one writer
  per tab; separate HTTP calls are not an atomic transaction.
- Stops include uncertainty, provider error, a changed page, no observed change,
  revisited link targets, exhausted budgets or departure from the URL scope. A
  timed-out action returns `action_confirmed: null`: inspect the tab before retrying.
  No retries or repeated actions are used to force a preferred model answer.
- Success requires the observed URL to match `success.url_prefix` and all supplied
  strings to appear in the snapshot. Choose specific result text, ideally a heading,
  not something repeated in navigation. `condition_observed` establishes those
  observations only; it does not certify content truth, saved files or the whole task.
- The receipt includes performed actions, final URL, up to 1,800 characters of
  readback and reported aggregate cost. Out-of-scope content is withheld. Unknown
  usage remains null; `known_cost_usd` is only the known subtotal.

The inherited URL-prefix restriction is not a network sandbox: a permitted
button or redirect can leave scope before readback detects it. Review the actual
site and controls first. The caller's existing browser takes over on uncertainty.

### Live observation, 21 September 2026

On a disposable local site, the loop filled `export`, clicked Search, chose the
export guide from three eligible results and verified its heading and URL. Three
Jev calls reported $0.000095886; the loop took 17,448 ms and returned 902 characters.
The test tab was closed. An initial generic-selector prompt returned uncertain;
the corrected prompt explicitly judges the next preparatory step rather than
single-action fulfillment of the whole request. Thresholds were unchanged.
The offline regression suite preserves no-action-on-uncertainty and budget checks.
This is a functional synthetic test, not evidence of production speed or token savings.
