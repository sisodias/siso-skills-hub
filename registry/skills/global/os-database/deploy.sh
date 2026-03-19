#!/bin/bash
# Deploy os-database skill to an agent with symlinks
# Usage: ./deploy-skill.sh <agent_path> <agent_id> <role> <department>

AGENT_PATH="$1"
AGENT_ID="$2"
ROLE="$3"
DEPARTMENT="$4"

if [ -z "$AGENT_PATH" ]; then
    echo "Usage: ./deploy-skill.sh <agent_path> <agent_id> <role> <department>"
    echo "Example: ./deploy-skill.sh /Users/.../agents/PM_Agent PM_Agent 'Project Manager' Meta"
    exit 1
fi

SKILL_SOURCE="/Users/shaansisodia/SISO_Workspace/agent_os/skills_hub/registry/skills/global/os-database"
SKILL_TARGET="$AGENT_PATH/.claude/skills/os-database"

# Create skills directory if needed
mkdir -p "$AGENT_PATH/.claude/skills"
mkdir -p "$SKILL_TARGET"

# Create symlinks for shared files
echo "Setting up os-database skill for $AGENT_ID..."

ln -sf "$SKILL_SOURCE/SKILL.md" "$SKILL_TARGET/SKILL.md"
ln -sf "$SKILL_SOURCE/schema.sql" "$SKILL_TARGET/schema.sql"
ln -sf "$SKILL_SOURCE/requirements.txt" "$SKILL_TARGET/requirements.txt"
ln -sf "$SKILL_SOURCE/README.md" "$SKILL_TARGET/README.md"
ln -sf "$SKILL_SOURCE/scripts" "$SKILL_TARGET/scripts"
ln -sf "$SKILL_SOURCE/rules" "$SKILL_TARGET/rules"
ln -sf "$SKILL_SOURCE/workflows" "$SKILL_TARGET/workflows"

# Create unique config.json
cat > "$SKILL_TARGET/config.json" << EOF
{
  "db_path": "env:SISO_SYSTEM_DB",
  "agent_id": "$AGENT_ID",
  "role": "$ROLE",
  "department": "$DEPARTMENT",
  "root_path": "$AGENT_PATH",
  "db_path_fallback": "~/.SystemDB/sisostem.db"
}
EOF

# Create unique state.json
cat > "$SKILL_TARGET/state.json" << EOF
{
  "current_session_id": null,
  "current_task_id": null,
  "run_number": null,
  "session_started_at": null
}
EOF

echo "✓ Skill deployed to $AGENT_PATH"
echo "✓ Config created for agent: $AGENT_ID ($ROLE - $DEPARTMENT)"
echo ""
echo "Files:"
ls -la "$SKILL_TARGET/"
