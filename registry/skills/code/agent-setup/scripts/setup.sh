#!/bin/bash
# Setup a new agent from V4 template with memory system
# Usage: ./setup.sh <agent_dir> <agent_name>
#
# NOTE: Uses CENTRAL claude-mem-lite source - no local copy needed!
# Each agent gets its own memory DB at .claude/memory/

set -e

AGENT_DIR="$1"
AGENT_NAME="$2"

if [ -z "$AGENT_DIR" ] || [ -z "$AGENT_NAME" ]; then
    echo "Usage: $0 <agent_dir> <agent_name>"
    echo "Example: $0 /path/to/Developer_Agent Developer_Agent"
    exit 1
fi

TEMPLATE_DIR="/Users/shaansisodia/SISO_Workspace/agent_os/module_templates/agents/live/v4"
MEMORY_SOURCE="/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite"

echo "Setting up agent: $AGENT_NAME"
echo "Location: $AGENT_DIR"

# 1. Copy V4 template
echo "📋 Copying V4 template..."
mkdir -p "$AGENT_DIR"
rsync -a --exclude='.claude/memory/*' --exclude='node_modules' --exclude='*.db' \
    "$TEMPLATE_DIR/" "$AGENT_DIR/"

# 2. Create .claude folder structure
mkdir -p "$AGENT_DIR/.claude/memory"
mkdir -p "$AGENT_DIR/.claude/hooks"

# 3. Create hooks.json pointing to CENTRAL source
echo "⚙️ Creating hooks (central source)..."
cat > "$AGENT_DIR/.claude/hooks/hooks.json" << EOF
{
  "description": "claude-mem-lite memory system hooks for $AGENT_NAME",
  "env": {
    "CLAUDE_MEM_DIR": "${AGENT_DIR}/.claude/memory",
    "CLAUDE_MEM_AGENT_ID": "$AGENT_NAME"
  },
  "hooks": {
    "SessionStart": [{"matcher": "startup|clear|compact", "hooks": [{"type": "command", "command": "node \"/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs\" session-start", "timeout": 15}]}],
    "PreToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "node \"/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs\" pre-tool-use", "timeout": 2}]}],
    "PostToolUse": [{"matcher": "*", "hooks": [{"type": "command", "command": "node \"/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs\" post-tool-use", "timeout": 5}]}],
    "Stop": [{"matcher": "*", "hooks": [{"type": "command", "command": "node \"/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs\" stop", "timeout": 5}]}],
    "UserPromptSubmit": [{"matcher": "*", "hooks": [{"type": "command", "command": "node \"/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs\" user-prompt", "timeout": 5}]}]
  }
}
EOF

# 4. Create .mcp.json pointing to CENTRAL source
cat > "$AGENT_DIR/.mcp.json" << EOF
{
  "mcpServers": {
    "mem": {
      "command": "node",
      "args": ["/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/server.mjs"],
      "env": {
        "CLAUDE_MEM_DIR": "$AGENT_DIR/.claude/memory",
        "CLAUDE_MEM_AGENT_ID": "$AGENT_NAME"
      }
    }
  }
}
EOF

# 5. Initialize memory (creates DB in agent's memory folder)
echo "💾 Initializing memory database..."
CLAUDE_MEM_DIR="$AGENT_DIR/.claude/memory" \
CLAUDE_MEM_AGENT_ID="$AGENT_NAME" \
    node "/Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite/hook.mjs" session-start 2>/dev/null || true

echo ""
echo "✅ Agent '$AGENT_NAME' ready!"
echo ""
echo "Created structure:"
echo "  $AGENT_DIR/"
echo "  ├── .claude/"
echo "  │   ├── hooks/hooks.json   # Hooks (central source)"
echo "  │   └── memory/            # Agent's OWN memory DB"
echo "  ├── .mcp.json             # MCP (central source)"
echo "  ├── identity.yaml         # Edit this!"
echo "  ├── inbox/                # Task inbox"
echo "  ├── outbox/               # Task outbox"
echo "  └── workspace/             # Working dir"
echo ""
echo "Note: Uses central claude-mem-lite at:"
echo "  /Users/shaansisodia/SISO_Workspace/agent_os/os_plugins/backlog/claude-mem-lite"
echo ""
echo "Next steps:"
echo "1. Edit identity.yaml with agent details"
echo "2. Start Claude Code in $AGENT_DIR"
echo "3. Run /mcp to verify mem connected"
