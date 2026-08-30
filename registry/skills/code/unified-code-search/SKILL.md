---
name: unified-code-search
description: Navigate a local codebase through native Serena symbol, reference, outline, and call-hierarchy queries.
version: 1.0.0
tags: [code-navigation, serena, symbols, references]
---
# Unified code navigation

Serena is the default and authoritative route for code navigation. Use the native `query_project` wrapper with the repository's absolute root and a read-only Serena tool. Never activate a shared project endpoint.

## Choose the Serena operation

| Question | Operation |
| --- | --- |
| Where is a symbol defined? | `find_symbol` with `name_path_pattern` |
| What is the file structure? | `get_symbols_overview` |
| Who calls a symbol? | `find_referencing_symbols` with `name_path` and `relative_path` |
| What does a symbol call? | call hierarchy when the active language server exposes it |
| What is the type at a location? | hover/type information |
| What files are involved? | exact path reads or a narrow project query |

Use `serena-fast` only in a runtime without native MCP. Pass JSON tool parameters and keep `relative_path` as narrow as possible. Ask for `include_body: true` only for the one function or class that must be read.

## Fallback boundary

For a known non-code document/config file, read the exact path directly. If every configured Serena transport fails, use the smallest available local fallback and state that semantic navigation was unavailable. Do not prescribe a broad repository scan or a generic search command in a worker brief.

## Remote sources

This skill is local-only. For public repositories or ecosystem discovery, use the dedicated research/source-reference skills. For an exact known dependency, use `source-reference` and inspect its fetched source with the same Serena-first rule.

## Completion contract

Return the exact path, symbol, operation, and relevant evidence. Report negative results explicitly. Do not claim a caller or definition from text coincidence alone.
