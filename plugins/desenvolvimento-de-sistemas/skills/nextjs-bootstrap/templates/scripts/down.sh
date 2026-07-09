#!/bin/bash

# Shutdown Script
#
# Usage:
#   ./scripts/down.sh                # Stop server (graceful)
#   ./scripts/down.sh --force        # Kill server + orphan processes (playwright, jest, next-server)
#   ./scripts/down.sh --clean        # Stop server + remove .env.local, node_modules, .next, .turbo
#   ./scripts/down.sh --force --clean # Force kill everything + clean

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_DIR")

# Read SERVER_PORT from .env.local
SERVER_PORT=$(grep '^SERVER_PORT=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2 | tr -d '"')
SERVER_PORT="${SERVER_PORT:-3000}"

# Parse flags
FORCE=false
CLEAN=false
for arg in "$@"; do
  case "$arg" in
    --force) FORCE=true ;;
    --clean|-clean) CLEAN=true ;;
  esac
done

echo "$PROJECT_NAME Shutdown"
echo ""

if [ "$FORCE" = true ]; then
  KILLED=false

  PORT_PIDS=$(lsof -ti:$SERVER_PORT 2>/dev/null)
  if [ -n "$PORT_PIDS" ]; then
    echo "$PORT_PIDS" | xargs kill -9 2>/dev/null
    echo "Killed process(es) on port $SERVER_PORT"
    KILLED=true
  fi

  PLAYWRIGHT_PIDS=$(pgrep -f "playwright.*$PROJECT_DIR" 2>/dev/null)
  if [ -n "$PLAYWRIGHT_PIDS" ]; then
    echo "$PLAYWRIGHT_PIDS" | xargs kill -9 2>/dev/null
    COUNT=$(echo "$PLAYWRIGHT_PIDS" | wc -l | tr -d ' ')
    echo "Killed $COUNT orphan Playwright process(es)"
    KILLED=true
  fi

  JEST_PIDS=$(pgrep -f "jest.*$PROJECT_DIR" 2>/dev/null)
  if [ -n "$JEST_PIDS" ]; then
    echo "$JEST_PIDS" | xargs kill -9 2>/dev/null
    COUNT=$(echo "$JEST_PIDS" | wc -l | tr -d ' ')
    echo "Killed $COUNT orphan Jest process(es)"
    KILLED=true
  fi

  NEXT_PIDS=$(pgrep -f "next-server.*$PROJECT_DIR" 2>/dev/null)
  if [ -n "$NEXT_PIDS" ]; then
    echo "$NEXT_PIDS" | xargs kill -9 2>/dev/null
    COUNT=$(echo "$NEXT_PIDS" | wc -l | tr -d ' ')
    echo "Killed $COUNT orphan Next.js server process(es)"
    KILLED=true
  fi

  if [ "$KILLED" = false ]; then
    echo "No processes found"
  fi
else
  PORT_PID=$(lsof -ti:$SERVER_PORT 2>/dev/null | head -1)
  if [ -n "$PORT_PID" ]; then
    PROC_CWD=$(lsof -p $PORT_PID 2>/dev/null | grep cwd | awk '{print $9}')
    if [ "$PROC_CWD" == "$PROJECT_DIR" ]; then
      kill -9 $PORT_PID 2>/dev/null
      echo "Stopped server on port $SERVER_PORT"
    else
      echo "Port $SERVER_PORT is not this project's server"
    fi
  else
    echo "No server running on port $SERVER_PORT"
  fi
fi

if [ "$CLEAN" = true ]; then
  echo ""
  [ -f "$PROJECT_DIR/.env.local" ] && rm "$PROJECT_DIR/.env.local" && echo ".env.local removed"
  [ -d "$PROJECT_DIR/node_modules" ] && rm -rf "$PROJECT_DIR/node_modules" && echo "node_modules removed"
  [ -d "$PROJECT_DIR/.next" ] && rm -rf "$PROJECT_DIR/.next" && echo ".next removed"
  [ -d "$PROJECT_DIR/.turbo" ] && rm -rf "$PROJECT_DIR/.turbo" && echo ".turbo removed"
  [ -d "$PROJECT_DIR/.playwright-cli" ] && rm -rf "$PROJECT_DIR/.playwright-cli" && echo ".playwright-cli removed"
fi

echo ""
echo "Done"
