---
name: bounded-tool-output
description: Keep diagnostic tool results small and recover precisely from truncated logs, broad searches, or oversized API responses. Use when inspecting large output or reducing context overhead; not to skip required source reads or verification.
---

# Bounded tool output

Choose the question and the fields or source window that answer it before fetching a large result.

- For ordinary shell diagnostics, start with `max_output_tokens: 1000`–`4000` when supported. This is a per-call budget, not a guarantee about nested calls or the combined response. Keep the combined tool batch similarly bounded; do not bundle ten full reads behind ten separate limits.
- Locate first, then read the matching window. Use available symbol navigation for symbols; scoped `rg -n`, exact file paths and bounded line ranges for text. Required instructions must still be read completely, paging when needed.
- Project structured results before printing: identifiers, status, counts, relevant fields and source locators. Do not print an entire tool response merely to obtain its status. Never serialize image/base64 payloads as text; use the image surface when visual inspection is required.
- Preserve lengthy test/build output in a task-local log. Return the actual command exit code, failure summary and log path; inspect the relevant failing section. A successful `tail` or `tee` is not proof that the test passed.
- If output is truncated, narrow the query or page the missing section. Do not repeat the same broad request with a higher limit unless the task genuinely needs the additional material. State exactly what remains unread.
- Reuse an already-read result while its source and decision context remain unchanged. Reread after a relevant edit, new checkpoint, or freshness-sensitive state change—not simply because another tool call occurred.

For an explicitly requested Codex configuration change, verify the supported `tool_output_token_limit` setting and inspect relevant overrides before editing. It is distinct from model response length and context-window settings. Do not change providers, reduce necessary model output, or restart live agents as a side effect. A file edit does not prove an existing session adopted it or discarded old context.

Completion evidence: the question answered, exact locator/exit status, and any unread remainder. A shorter response without the necessary evidence is not a successful optimization.
