---
name: cmux-browser
description: Control CMUX browser for automated testing. This skill lets you open, navigate, and interact with browsers in Claude Code workspaces.
version: 1.0.0
tags:
  - testing
  - browser
  - automation
---

# CMUX Browser Skill

Control CMUX browser for automated testing. This skill lets you open, navigate, and interact with browsers in Claude Code workspaces.

## Requirements

CMUX must be installed at: `/Applications/cmux.app/Contents/Resources/bin/cmux`

Make sure cmux is in your PATH:
```bash
export PATH="/Applications/cmux.app/Contents/Resources/bin:$PATH"
```

---

## Current Setup

- **Testing Agent workspace:** `workspace:24`
- **Browser surface:** `surface:50` (already open)

---

## List Workspaces & Panes

```bash
# List all workspaces
cmux list-workspaces

# List panes in a workspace
cmux list-panes --workspace workspace:24

# List surfaces in a pane
cmux list-pane-surfaces --workspace workspace:24 --pane pane:47
```

---

## Open Browser

```bash
# Open browser in a new split (creates new pane)
cmux browser open-split --workspace workspace:24 https://siso-internal.vercel.app

# Open browser in current workspace
cmux browser open https://siso-internal.vercel.app
```

---

## Navigate

```bash
# Navigate to URL
cmux browser --surface surface:50 goto https://siso-internal.vercel.app

# Navigate (alternative)
cmux browser --surface surface:50 navigate https://siso-internal.vercel.app

# Go back/forward
cmux browser --surface surface:50 back
cmux browser --surface surface:50 forward

# Reload
cmux browser --surface surface:50 reload
```

---

## Get Page Info

```bash
# Get current URL
cmux browser --surface surface:50 get url

# Get page title
cmux browser --surface surface:50 get title

# Get page text
cmux browser --surface surface:50 get text
```

---

## Interact with Elements

```bash
# Click element (by role, text, label, etc.)
cmux browser --surface surface:50 click "button:Login"
cmux browser --surface surface:50 click "text:Submit"
cmux browser --surface surface:50 click "role:heading"

# Type text
cmux browser --surface surface:50 type "input:email" "test@example.com"

# Fill input
cmux browser --surface surface:50 fill "input:name" "John Doe"

# Press key
cmux browser --surface surface:50 press "Enter"
cmux browser --surface surface:50 press "Control+c"

# Hover
cmux browser --surface surface:50 hover "button:Menu"
```

---

## Snapshots (DOM)

```bash
# Get DOM snapshot
cmux browser --surface surface:50 snapshot

# Interactive snapshot (with refs)
cmux browser --surface surface:50 snapshot --interactive

# Compact snapshot (smaller output)
cmux browser --surface surface:50 snapshot --compact

# Limit depth
cmux browser --surface surface:50 snapshot --compact --max-depth 3
```

---

## Screenshots (Image)

```bash
# Take screenshot
cmux browser --surface surface:50 screenshot /tmp/test.png

# Screenshot paths are relative to /tmp on the system
```

---

## Find Elements

```bash
# Find elements by strategy
cmux browser --surface surface:50 find role "button"
cmux browser --surface surface:50 find text "Login"
cmux browser --surface surface:50 find label "Email"
cmux browser --surface surface:50 find placeholder "Enter email"

# Find specific element
cmux browser --surface surface:50 find first "button"
cmux browser --surface surface:50 find nth "link:2"
```

---

## Wait for Conditions

```wait
# Wait for element
cmux browser --surface surface:50 wait --selector "button:Submit"

# Wait for text
cmux browser --surface surface:50 wait --text "Welcome"

# Wait for URL
cmux browser --surface surface:50 wait --url-contains "admin"

# Wait with timeout
cmux browser --surface surface:50 wait --selector "div:loading" --timeout-ms 5000
```

---

## Console Errors

```bash
# List console errors
cmux browser errors list

# Get browser surface ID
cmux browser identify
```

---

## Example Workflow

```bash
# 1. Open browser to app
cmux browser --surface surface:50 goto "https://siso-internal.vercel.app"

# 2. Wait for page load
cmux browser --surface surface:50 wait --selector "body"

# 3. Take screenshot
cmux browser --surface surface:50 screenshot /tmp/homepage.png

# 4. Get DOM snapshot
cmux browser --surface surface:50 snapshot --compact

# 5. Click navigation
cmux browser --surface surface:50 click "button:Tasks"

# 6. Check console errors
cmux browser errors list
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Open URL | `cmux browser --surface surface:X goto <url>` |
| Click | `cmux browser --surface surface:X click "button:Label"` |
| Type | `cmux browser --surface surface:X type "input:sel" "text"` |
| Get URL | `cmux browser --surface surface:X get url` |
| Snapshot | `cmux browser --surface surface:X snapshot` |
| Screenshot | `cmux browser --surface surface:X screenshot /tmp/name.png` |
| Errors | `cmux browser errors list` |

**Remember:** Replace `surface:50` with your actual surface ID from `list-pane-surfaces`.
