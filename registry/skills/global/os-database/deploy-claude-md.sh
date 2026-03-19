#!/bin/bash
# Generate CLAUDE.md from template with variable substitution
# Usage: ./deploy-claude-md.sh <agent_path> <agent_id> <role> <department>

AGENT_PATH="$1"
AGENT_ID="$2"
ROLE="$3"
DEPARTMENT="$4"

if [ -z "$AGENT_PATH" ]; then
    echo "Usage: ./deploy-claude-md.sh <agent_path> <agent_id> <role> <department>"
    exit 1
fi

TEMPLATE_SOURCE="/Users/shaansisodia/SISO_Workspace/agent_os/module_templates/agents/live/v4/CLAUDE.md"
TARGET_FILE="$AGENT_PATH/CLAUDE.md"

if [ ! -f "$TEMPLATE_SOURCE" ]; then
    echo "Error: Template not found at $TEMPLATE_SOURCE"
    exit 1
fi

# Copy template and replace variables
sed -e "s/Agent v4 — Bootloader/$ROLE - Agent/g" \
    -e "s/{AgentName}/$AGENT_ID/g" \
    "$TEMPLATE_SOURCE" > "$TARGET_FILE"

echo "✓ Created CLAUDE.md at $TARGET_FILE"
echo "  Agent: $AGENT_ID"
echo "  Role: $ROLE"
echo "  Department: $DEPARTMENT"
