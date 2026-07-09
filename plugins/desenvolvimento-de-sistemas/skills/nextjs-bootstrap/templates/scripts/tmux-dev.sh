#!/bin/bash

# Tmux Dev Session
# Creates a detached tmux session with server logs and process monitoring
# Usage: ./scripts/tmux-dev.sh
# Attach: tmux attach -t $PROJECT_NAME

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_DIR")
LOG_FILE="/tmp/${PROJECT_NAME}-server.log"

tmux kill-session -t "$PROJECT_NAME" 2>/dev/null

tmux new-session -d -s "$PROJECT_NAME" -x 200 -y 50 -c "$PROJECT_DIR"

tmux send-keys -t "$PROJECT_NAME":0.0 "tail -f $LOG_FILE 2>/dev/null || (echo 'Waiting for server to start...' && while [ ! -f $LOG_FILE ]; do sleep 2; done && tail -f $LOG_FILE)" Enter

tmux split-window -t "$PROJECT_NAME":0 -v -p 30 -c "$PROJECT_DIR"
tmux send-keys -t "$PROJECT_NAME":0.1 "$PROJECT_DIR/scripts/watch.sh --ps" Enter

echo "Tmux session '$PROJECT_NAME' created. Attach with: tmux attach -t $PROJECT_NAME"
