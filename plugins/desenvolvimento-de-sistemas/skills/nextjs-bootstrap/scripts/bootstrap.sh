#!/bin/bash

# Bootstrap Script
# Scaffolds a new Next.js project with standard architecture
#
# Usage: bootstrap.sh <project-name> <description> <target-dir>
#
# Example:
#   bootstrap.sh my-app "My awesome app" /path/to/my-app

set -e

# --- Arguments ---
PROJECT_NAME="${1:?Usage: bootstrap.sh <project-name> <description> <target-dir>}"
PROJECT_DESCRIPTION="${2:?Usage: bootstrap.sh <project-name> <description> <target-dir>}"
TARGET_DIR="${3:?Usage: bootstrap.sh <project-name> <description> <target-dir>}"

# Derive DB name: kebab-case to snake_case
PROJECT_DB_NAME=$(echo "$PROJECT_NAME" | tr '-' '_')

# Resolve paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATES_DIR="$SKILL_DIR/templates"

echo "Bootstrapping: $PROJECT_NAME"
echo "Description:   $PROJECT_DESCRIPTION"
echo "Target:        $TARGET_DIR"
echo "DB name:       $PROJECT_DB_NAME"
echo ""

# --- Helper: copy file with placeholder replacement ---
copy_template() {
  local src="$1"
  local dest="$2"

  mkdir -p "$(dirname "$dest")"
  sed \
    -e "s|{{PROJECT_NAME}}|$PROJECT_NAME|g" \
    -e "s|{{PROJECT_DESCRIPTION}}|$PROJECT_DESCRIPTION|g" \
    -e "s|{{PROJECT_DB_NAME}}|$PROJECT_DB_NAME|g" \
    "$src" > "$dest"
}

# --- Step 1: Create Next.js app if target is empty/missing ---
if [ ! -f "$TARGET_DIR/package.json" ]; then
  echo "Step 1: Creating Next.js app..."
  npx create-next-app@latest "$TARGET_DIR" \
    --typescript \
    --tailwind \
    --eslint \
    --app \
    --src-dir \
    --import-alias "@/*" \
    --turbopack \
    --yes
  echo ""
else
  echo "Step 1: package.json exists, skipping create-next-app"
  echo ""
fi

cd "$TARGET_DIR"

# --- Step 2: Clean up Tailwind 4 incompatible files ---
echo "Step 2: Cleaning up for Tailwind 4..."
rm -f tailwind.config.ts tailwind.config.js
# Recreate postcss.config.mjs with @tailwindcss/postcss (Tailwind 4 requirement)
cat > postcss.config.mjs <<'POSTCSS'
/** @type {import('postcss-load-config').Config} */
const config = {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}

export default config
POSTCSS
echo ""

# --- Step 3: Install dependencies ---
echo "Step 3: Installing dependencies..."
npm install prisma @prisma/client @prisma/adapter-pg pg
npm install -D @types/pg tsx
npm install next-auth@beta bcryptjs
npm install -D @types/bcryptjs
npm install zod
npm install -D dotenv-cli

# Jest and testing libraries
echo "Step 3b: Installing Jest dependencies..."
npm install -D jest jest-environment-jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event @types/jest
echo ""

# --- Step 4: Copy script templates ---
echo "Step 4: Copying scripts..."
mkdir -p scripts
for script in init.sh down.sh check.sh watch.sh tmux-dev.sh deploy.sh; do
  copy_template "$TEMPLATES_DIR/scripts/$script" "scripts/$script"
done
chmod +x scripts/*.sh
echo ""

# --- Step 5: Copy source templates ---
echo "Step 5: Copying source files..."
copy_template "$TEMPLATES_DIR/src/lib/db.ts" "src/lib/db.ts"
copy_template "$TEMPLATES_DIR/src/lib/auth.ts" "src/lib/auth.ts"
copy_template "$TEMPLATES_DIR/src/lib/validations.ts" "src/lib/validations.ts"
copy_template "$TEMPLATES_DIR/src/middleware.ts" "src/middleware.ts"
mkdir -p "src/app/api/auth/[...nextauth]"
copy_template "$TEMPLATES_DIR/src/app/api/auth/[...nextauth]/route.ts" "src/app/api/auth/[...nextauth]/route.ts"
copy_template "$TEMPLATES_DIR/src/app/globals.css" "src/app/globals.css"
copy_template "$TEMPLATES_DIR/src/app/layout.tsx" "src/app/layout.tsx"
copy_template "$TEMPLATES_DIR/src/app/page.tsx" "src/app/page.tsx"

# Create empty component directories
mkdir -p src/components/layout src/components/shared

# --- Step 5b: Copy Jest config and test templates ---
echo "Step 5b: Copying Jest config and test templates..."
copy_template "$TEMPLATES_DIR/jest.config.ts" "jest.config.ts"
copy_template "$TEMPLATES_DIR/jest.setup.ts" "jest.setup.ts"
mkdir -p src/tests/helpers src/tests/examples
copy_template "$TEMPLATES_DIR/src/tests/helpers/db.ts" "src/tests/helpers/db.ts"
copy_template "$TEMPLATES_DIR/src/tests/helpers/auth.ts" "src/tests/helpers/auth.ts"
copy_template "$TEMPLATES_DIR/src/tests/examples/validations.test.ts" "src/tests/examples/validations.test.ts"
copy_template "$TEMPLATES_DIR/src/tests/examples/api-route.test.ts" "src/tests/examples/api-route.test.ts"
echo ""

# --- Step 6: Copy Prisma files ---
echo "Step 6: Setting up Prisma..."
mkdir -p prisma
copy_template "$TEMPLATES_DIR/prisma-schema.prisma" "prisma/schema.prisma"
copy_template "$TEMPLATES_DIR/prisma-config.ts" "prisma.config.ts"
copy_template "$TEMPLATES_DIR/prisma/seed.ts" "prisma/seed.ts"
echo ""

# --- Step 7: Copy .env.example ---
echo "Step 7: Creating .env.example..."
copy_template "$TEMPLATES_DIR/env-example.txt" ".env.example"
echo ""

# --- Step 7b: Create .env.test for test database ---
echo "Step 7b: Creating .env.test..."
cat > .env.test <<EOF
DATABASE_URL="postgresql://postgres:postgres@localhost:5433/${PROJECT_DB_NAME}_test"
EOF
echo ""

# --- Step 8: Generate CLAUDE.md ---
echo "Step 8: Generating CLAUDE.md..."
copy_template "$TEMPLATES_DIR/claude-md.md" "CLAUDE.md"
echo ""

# --- Step 9: Add package.json scripts ---
echo "Step 9: Adding package.json scripts..."
node -e "
const fs = require('fs');
const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
pkg.scripts = {
  ...pkg.scripts,
  'db:push': 'prisma db push',
  'db:push:test': 'dotenv -e .env.test -- prisma db push',
  'db:seed': 'tsx prisma/seed.ts',
  'db:migrate': 'prisma migrate dev',
  'db:reset': 'prisma migrate reset',
  'lint:fix': 'next lint --fix',
  'test': 'dotenv -e .env.test -- jest',
  'test:watch': 'dotenv -e .env.test -- jest --watch',
  'test:coverage': 'dotenv -e .env.test -- jest --coverage'
};
fs.writeFileSync('package.json', JSON.stringify(pkg, null, 2) + '\n');
"
echo ""

# --- Step 10: Update .gitignore ---
echo "Step 10: Updating .gitignore..."
if ! grep -q "src/generated/prisma/" .gitignore 2>/dev/null; then
  echo "" >> .gitignore
  echo "# Prisma generated client" >> .gitignore
  echo "src/generated/prisma/" >> .gitignore
fi
if ! grep -q "coverage/" .gitignore 2>/dev/null; then
  echo "" >> .gitignore
  echo "# Jest coverage" >> .gitignore
  echo "coverage/" >> .gitignore
fi
echo ""

# --- Step 11: Generate Prisma client ---
echo "Step 11: Generating Prisma client..."
npx prisma generate
echo ""

echo "Bootstrap complete!"
echo ""
echo "Next steps:"
echo "  cd $TARGET_DIR"
echo "  ./scripts/init.sh"
