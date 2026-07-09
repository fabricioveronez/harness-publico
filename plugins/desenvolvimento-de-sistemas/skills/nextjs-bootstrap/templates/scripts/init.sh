#!/bin/bash

# Initialization Script
# Sets up env, database, and starts dev server with health check

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

PROJECT_NAME=$(basename "$PROJECT_DIR")
LOG_FILE="/tmp/${PROJECT_NAME}-server.log"
HEALTH_TIMEOUT=60
HEALTH_INTERVAL=2

echo "$PROJECT_NAME Initialization"
echo ""

# Setup env if needed
FIRST_RUN=false
if [ ! -f .env.local ]; then
  cp .env.example .env.local
  echo ".env.local created"
  FIRST_RUN=true
fi

# Read SERVER_PORT and PORT_RANGE from .env.local
SERVER_PORT=$(grep '^SERVER_PORT=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2 | tr -d '"')
SERVER_PORT="${SERVER_PORT:-3000}"
PORT_RANGE=$(grep '^PORT_RANGE=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'"' -f2)
PORT_RANGE="${PORT_RANGE:-3000 3010}"
PORT_START=$(echo "$PORT_RANGE" | awk '{print $1}')
PORT_END=$(echo "$PORT_RANGE" | awk '{print $2}')

# On first run, find a free port if default is occupied
if [ "$FIRST_RUN" = true ] && lsof -ti:$SERVER_PORT >/dev/null 2>&1; then
  echo "Port $SERVER_PORT in use, finding a free port..."
  for P in $(seq $PORT_START $PORT_END); do
    if ! lsof -ti:$P >/dev/null 2>&1; then
      SERVER_PORT=$P
      sed -i '' "s/^SERVER_PORT=.*/SERVER_PORT=$P/" "$PROJECT_DIR/.env.local"
      sed -i '' "s|^NEXTAUTH_URL=.*|NEXTAUTH_URL=\"http://localhost:$P\"|" "$PROJECT_DIR/.env.local"
      echo "Assigned port $P"
      break
    fi
  done
fi

# Install dependencies if needed
if [ ! -d node_modules ]; then
  echo "Installing dependencies..."
  npm install
  echo ""
fi

# Read DATABASE_URL from .env.local
export DATABASE_URL=$(grep '^DATABASE_URL=' "$PROJECT_DIR/.env.local" 2>/dev/null | cut -d'=' -f2- | tr -d '"')

npx prisma generate > /dev/null 2>&1

# Setup database (PostgreSQL)
echo "Setting up PostgreSQL database..."
createdb {{PROJECT_DB_NAME}} 2>/dev/null
createdb {{PROJECT_DB_NAME}}_test 2>/dev/null
npx prisma db push
npm run db:seed 2>/dev/null
echo ""

# Check if port is already in use
PORT_PID=$(lsof -ti:$SERVER_PORT 2>/dev/null | head -1)
if [ -n "$PORT_PID" ]; then
  PROC_CWD=$(lsof -p $PORT_PID 2>/dev/null | grep cwd | awk '{print $9}')
  if [ "$PROC_CWD" == "$PROJECT_DIR" ]; then
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:$SERVER_PORT/" 2>/dev/null)
    if [ "$HTTP_STATUS" -ge 200 ] 2>/dev/null && [ "$HTTP_STATUS" -lt 500 ] 2>/dev/null; then
      echo "Server already running!"
      echo "URL: http://localhost:$SERVER_PORT"
      echo "PID: $PORT_PID"
      exit 0
    fi
  fi
  echo "Port $SERVER_PORT in use (PID $PORT_PID), killing..."
  kill -9 $PORT_PID 2>/dev/null
  sleep 1
fi

echo ""
echo "Starting server on port $SERVER_PORT..."

# Start server in background
PORT=$SERVER_PORT npm run dev > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# Wait for server to become healthy
ELAPSED=0
HEALTHY=false

while [ $ELAPSED -lt $HEALTH_TIMEOUT ]; do
  if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo ""
    echo "ERROR: Server process died. Last 20 lines of log:"
    tail -20 "$LOG_FILE"
    exit 1
  fi

  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 "http://localhost:$SERVER_PORT/" 2>/dev/null)
  if [ "$HTTP_STATUS" -ge 200 ] 2>/dev/null && [ "$HTTP_STATUS" -lt 500 ] 2>/dev/null; then
    HEALTHY=true
    break
  fi

  sleep $HEALTH_INTERVAL
  ELAPSED=$((ELAPSED + HEALTH_INTERVAL))
  printf "."
done

echo ""

if [ "$HEALTHY" = true ]; then
  echo "Server is ready!"
  echo "URL: http://localhost:$SERVER_PORT"
  echo "PID: $SERVER_PID"
  echo "Log: $LOG_FILE"
else
  echo "ERROR: Server failed to become healthy after ${HEALTH_TIMEOUT}s"
  echo "Last 20 lines of log:"
  tail -20 "$LOG_FILE"
  echo ""
  echo "Killing unresponsive server (PID $SERVER_PID)..."
  kill -9 $SERVER_PID 2>/dev/null
  exit 1
fi
