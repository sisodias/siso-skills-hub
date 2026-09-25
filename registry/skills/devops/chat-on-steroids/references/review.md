# Reviewed upstream and integration boundary

- Source: https://github.com/totec448-spec/chat-on-steroids
- Reviewed commit: `62608f266c92a4ff64f093af3721ecb20cd47c57`
- Release inspected: `v2.0.5` (2026-09-06 inspection)
- Release tag commit: `f9d0e26db02fdd0b68cf1188a4998baa979eebf5`.
  The reviewed main commit is nine commits ahead; the configuration file is
  identical at both refs, but later native-helper/renderer changes are not proof
  of behavior in the released binary.
- License: MIT. This skill/client is SISO-authored integration guidance, not an
  upstream skill or an assertion of upstream endorsement.
- Apple Silicon ZIP SHA-256:
  `dafaac6310e6093ab0706efea755a93755174fd7b75e3626d4eecfc5047bcdf9`

Primary reviewed sources: upstream `README.md`, `SECURITY.md`,
`extension/manifest.json`, `src/main/config.ts`, `src/main/connection.ts`,
`src/main/mcp/server.ts`, `src/preload/index.ts`, and `src/shared/types.ts`.

Upstream is a separate local MCP app, not a drop-in connection to an already
running browser. It has `observe`/`computer` Desktop tools on Windows and macOS;
the desktop group is off by default on macOS and needs OS consent. The companion
extension is documented for Chrome and handles recording, attribution and worker
tabs. The extension is not a general-purpose remote-browser control API.

Fresh upstream defaults enable recording, auto-compaction and multi-agent features.
Do not start a fresh profile blindly when the user only requested browser setup.
Our setup profile uses manual/local-only transport, no approved filesystem roots,
no Core file/shell permissions, no clipboard access, and disables recording,
compaction, workers and Goal/Loop. Native screen/input remains subject to macOS.

Release binaries are unsigned/unnotarized; a checksum establishes artifact
integrity, not publisher trust. The repository's `SECURITY.md` has an outdated
sentence about macOS availability; the current README, native backend and config
code explicitly include macOS. Do not generalize platform support from that stale
sentence.

The helper accepts only an operator-supplied local Desktop MCP URL. It does not
discover secret paths, read cookies or browser storage, modify the upstream app,
expose another public tunnel, or replace SISO Workspace's stable fleet URLs.
Native UI behavior remains unverified until the owner approves macOS permissions
and the live Desktop MCP endpoint is configured and tested.
