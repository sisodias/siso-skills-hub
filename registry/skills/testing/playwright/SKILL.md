---
name: playwright
description: Automated browser testing for SISO Internal Lab using Playwright CLI
version: 1.0.0
tags:
  - testing
  - browser
  - automation
---

# Playwright CLI Skill

Automated browser testing for SISO Internal Lab.

## Installation

```bash
npm install -g @playwright/cli@latest
```

## Quick Start

```bash
# Open browser and navigate to URL
playwright-cli open https://siso-internal.vercel.app

# Capture page snapshot to see interactable elements
playwright-cli snapshot

# Take screenshot
playwright-cli screenshot /tmp/page.png
```

## Commands

### Browser Control

```bash
# Open browser (optionally with URL)
playwright-cli open <url>

# Close browser
playwright-cli close

# Navigate
playwright-cli goto <url>
playwright-cli go-back
playwright-cli go-forward
playwright-cli reload
```

### Interact with Elements

```bash
# Get list of clickable elements
playwright-cli snapshot

# Click element (use ref from snapshot)
playwright-cli click <ref>

# Type into input
playwright-cli fill <ref> <text>
playwright-cli type <ref> <text>

# Select dropdown
playwright-cli select <ref> <value>

# Check/uncheck
playwright-cli check <ref>
playwright-cli uncheck <ref>
```

### Screenshot & State

```bash
# Take screenshot
playwright-cli screenshot <filename>.png

# Save browser state (cookies, localStorage)
playwright-cli state-save <name>

# Load browser state
playwright-cli state-load <name>
```

### Console & Network

```bash
# View console logs
playwright-cli console

# View network requests
playwright-cli network
```

## Workflow for Testing

### 1. Open and Navigate
```bash
playwright-cli open https://siso-internal.vercel.app
```

### 2. Capture Page State
```bash
playwright-cli snapshot
```
This shows all interactable elements with refs like `ref=button-1`, `ref=input-2`

### 3. Interact
```bash
playwright-cli click button-1
playwright-cli fill input-2 "test text"
```

### 4. Take Screenshot
```bash
playwright-cli screenshot /tmp/test-result.png
```

### 5. Check Console Errors
```bash
playwright-cli console
```

### 6. Close
```bash
playwright-cli close
```

## Example: Test Login Flow

```bash
# Open app
playwright-cli open https://siso-internal.vercel.app

# Capture elements
playwright-cli snapshot

# Click sign in
playwright-cli click button-sign-in

# Wait and fill email
playwright-cli snapshot
playwright-cli fill input-email "test@example.com"
playwright-cli fill input-password "password123"

# Submit
playwright-cli click button-submit

# Verify
playwright-cli snapshot
playwright-cli screenshot /tmp/logged-in.png

# Check console
playwright-cli console

playwright-cli close
```

## Tips

- Always run `snapshot` after navigating to see available elements
- Use descriptive refs when clicking: `playwright-cli click "Add Task button"`
- Check console for JavaScript errors
- Save state to persist login sessions
- Run headed mode: `playwright-cli open <url> --headed`
