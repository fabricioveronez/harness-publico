#!/bin/bash

# Status Check Script
# Displays OK/PENDING/DEGRADED status for environment setup items
#
# Usage:
#   ./scripts/check.sh        # Diagnostic only (read-only)
#   ./scripts/check.sh --fix  # Diagnostic + auto-fix degraded/stopped server and orphan processes

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_NAME=$(basename "$PROJECT_DIR")
HEALTH_TIMEOUT=3
AUTO_FIX=false
SERVER_STATUS="none"

SERVER_PORT=$(grep '^SERVER_PORT=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2 | tr -d '"')
SERVER_PORT="${SERVER_PORT:-3000}"

if [ "$1" == "--fix" ]; then
  AUTO_FIX=true
fi

echo "$PROJECT_NAME Status Check"
echo ""

if [ -f "$PROJECT_DIR/.env.local" ]; then
  echo "[OK] .env.local configured"
else
  echo "[PENDING] .env.local not found"
fi

DATABASE_URL=$(grep '^DATABASE_URL=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2- | tr -d '"')
if [ -n "$DATABASE_URL" ]; then
  echo "[OK] Database configured (PostgreSQL)"
else
  echo "[PENDING] DATABASE_URL not configured"
fi

PORT_PID=$(lsof -ti:$SERVER_PORT 2>/dev/null | head -1)
if [ -n "$PORT_PID" ]; then
  PROC_CWD=$(lsof -p $PORT_PID 2>/dev/null | grep cwd | awk '{print $9}')
  if [ "$PROC_CWD" == "$PROJECT_DIR" ]; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time $HEALTH_TIMEOUT "http://localhost:$SERVER_PORT/" 2>/dev/null)
    if [ "$HTTP_STATUS" -ge 200 ] 2>/dev/null && [ "$HTTP_STATUS" -lt 500 ] 2>/dev/null; then
      echo "[OK] Development server running"
      echo "     URL: http://localhost:$SERVER_PORT"
      echo "     Health: responding (HTTP $HTTP_STATUS)"
      SERVER_STATUS="healthy"
    else
      echo "[DEGRADED] Development server on port $SERVER_PORT (PID $PORT_PID) is NOT responding"
      echo "           HTTP status: ${HTTP_STATUS:-timeout}"
      SERVER_STATUS="degraded"
    fi
  else
    echo "[PENDING] Development server not running (port $SERVER_PORT used by another process)"
    SERVER_STATUS="pending"
  fi
else
  echo "[PENDING] Development server not running"
  SERVER_STATUS="pending"
fi

ORPHAN_COUNT=0
for PROC_NAME in playwright jest; do
  PIDS=$(pgrep -f "$PROC_NAME.*$PROJECT_DIR" 2>/dev/null)
  if [ -n "$PIDS" ]; then
    COUNT=$(echo "$PIDS" | wc -l | tr -d ' ')
    ORPHAN_COUNT=$((ORPHAN_COUNT + COUNT))
  fi
done

if [ "$ORPHAN_COUNT" -gt 0 ]; then
  echo ""
  echo "[WARNING] $ORPHAN_COUNT orphan test process(es) detected (playwright/jest)"
fi

if [ "$AUTO_FIX" = true ]; then
  FIXED_SOMETHING=false

  if [ "$ORPHAN_COUNT" -gt 0 ]; then
    echo ""
    echo "Fixing: killing orphan processes..."
    "$PROJECT_DIR/scripts/down.sh" --force 2>/dev/null
    FIXED_SOMETHING=true
    if [ "$SERVER_STATUS" == "healthy" ]; then
      sleep 1
      PORT_PID=$(lsof -ti:$SERVER_PORT 2>/dev/null | head -1)
      if [ -z "$PORT_PID" ]; then
        SERVER_STATUS="pending"
      fi
    fi
  fi

  if [ "$SERVER_STATUS" == "degraded" ]; then
    echo ""
    echo "Fixing: killing degraded server and restarting..."
    "$PROJECT_DIR/scripts/down.sh" --force 2>/dev/null
    rm -rf "$PROJECT_DIR/.next" 2>/dev/null
    echo ""
    "$PROJECT_DIR/scripts/init.sh"
    FIXED_SOMETHING=true
  fi

  if [ "$SERVER_STATUS" == "pending" ]; then
    echo ""
    echo "Fixing: cleaning .next and starting server..."
    rm -rf "$PROJECT_DIR/.next" 2>/dev/null
    "$PROJECT_DIR/scripts/init.sh"
    FIXED_SOMETHING=true
  fi

  if [ "$FIXED_SOMETHING" = false ] && [ "$SERVER_STATUS" == "healthy" ]; then
    echo ""
    echo "Nothing to fix. All good."
  fi
else
  if [ "$SERVER_STATUS" != "healthy" ] || [ "$ORPHAN_COUNT" -gt 0 ]; then
    echo ""
    echo "Run './scripts/check.sh --fix' to auto-fix issues"
  fi
fi
