# Agent TMUX helpers — add to ~/.zshrc

# Spawn agent in persistent tmux (runs outside cmux)
spawn-agent() {
    local agent_name="${1}"
    local session_name="agent-os-${agent_name}"
    local agent_dir="/Users/shaansisodia/SISO_Workspace/agent_os/agents/${agent_name}"

    if [ ! -d "$agent_dir" ]; then
        echo "Agent not found: $agent_dir"
        return 1
    fi

    # Kill existing session if any (clean restart)
    tmux kill-session -t "$session_name" 2>/dev/null

    # Create detached session
    tmux new-session -d -s "$session_name" -c "$agent_dir"

    # Start claude
    tmux send-keys -t "$session_name" "claude" Enter

    echo "Spawned $agent_name in tmux session: $session_name"
    echo "In cmux: select 'Attach to tmux' → $session_name"
}

# List all agent sessions
agent-sessions() {
    tmux list-sessions -F "#{session_name}" | grep "^agent-os-" || echo "No agent sessions"
}

# Attach to agent session
attach-agent() {
    local session_name="agent-os-${1}"
    tmux attach -t "$session_name"
}
