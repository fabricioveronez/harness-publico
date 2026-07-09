#!/bin/bash

# Watch Script
# Default: tail server logs. With --ps: show running processes.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_DIR")
SERVER_PORT=$(grep '^SERVER_PORT=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2 | tr -d '"')
SERVER_PORT="${SERVER_PORT:-3000}"
LOG_FILE="/tmp/${PROJECT_NAME}-server.log"

if [ "$1" == "--ps" ]; then
  while true; do
    clear
    echo "=== $PROJECT_NAME Processes (port $SERVER_PORT) ==="
    echo ""

    PID=$(pgrep -f "npm run dev" | head -1)
    if [ -n "$PID" ]; then
      echo "* npm run dev > next-server (localhost:$SERVER_PORT)"
    else
      echo "* server not running"
    fi

    ps -eo command | grep "$PROJECT_DIR" | \
      grep -v grep | \
      grep -v watch | \
      grep -v Cursor | \
      grep -v jest-worker | \
      grep -v postcss | \
      grep -v "node_modules/.bin/next" | \
      grep -v "npm run dev" | \
      grep -v tail | \
      grep -v tmux | \
      grep -v "watch.sh" | \
      sed "s|$PROJECT_DIR/||g" | \
      sed "s|node_modules/.bin/||g" | \
      sed "s|node ||g" | \
      sort -u | \
      while read line; do
        [ -n "$line" ] && echo "* $line"
      done

    sleep 1
  done
else
  echo "$PROJECT_NAME server logs (port $SERVER_PORT)"
  echo ""
  tail -f "$LOG_FILE" 2>/dev/null || echo "No log file yet. Start the server with ./scripts/init.sh"
fi
