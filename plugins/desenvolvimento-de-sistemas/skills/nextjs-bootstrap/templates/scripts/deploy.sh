#!/bin/bash

# Vercel Deploy Script
# Runs migrations and builds

set -e

export DATABASE_SSL="true"

npx prisma generate

MIGRATION_URL="${POSTGRES_URL_NON_POOLING:-${DIRECT_DATABASE_URL:-$DATABASE_URL}}"
export DATABASE_URL="$MIGRATION_URL"

npx prisma migrate deploy

npm run build
