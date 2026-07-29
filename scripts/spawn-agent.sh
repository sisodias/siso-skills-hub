#!/bin/bash
# spawn-agent.sh — Spawns an agent in a persistent tmux session
# Usage: ./spawn-agent.sh <agent-name> [command]
# Example: ./spawn-agent.sh meta-pm

AGENT_NAME="${1}"
COMMAND="${2:-cla}"
SISO_WORKSPACE="${SISO_WORKSPACE:-$HOME/SISO_Workspace}"

if [ -z "$AGENT_NAME" ]; then
    echo "Usage: $0 <agent-name> [command]"
    echo "Example: $0 meta-pm"
    exit 1
fi

SESSION_NAME="agent-os-${AGENT_NAME}"
AGENT_DIR="${SISO_WORKSPACE}/agent_os/agents/${AGENT_NAME}"

# Check if agent exists
if [ ! -d "$AGENT_DIR" ]; then
    echo "Error: Agent directory not found: $AGENT_DIR"
    exit 1
fi

# Check if session already exists
if tmux has-session -t "$SESSION_NAME" 2>/dev/null; then
    echo "Session $SESSION_NAME already exists. Attaching..."
    tmux attach -t "$SESSION_NAME"
    exit 0
fi

# Create new session (detached)
echo "Creating session: $SESSION_NAME"
tmux new-session -d -s "$SESSION_NAME" -c "$AGENT_DIR"

# Send command to run
tmux send-keys -t "$SESSION_NAME" "$COMMAND" C-m

echo "Session $SESSION_NAME created at: $AGENT_DIR"
echo "To attach: tmux attach -t $SESSION_NAME"
echo "To view in cmux: open cmux and select the session"
