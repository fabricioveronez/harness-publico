## Project Overview

{{PROJECT_DESCRIPTION}}. Built with Next.js 16+ (App Router), TypeScript, Tailwind CSS 4, and Prisma 7.

## Environment Setup

### Scripts

```bash
./scripts/init.sh                  # Setup: .env + deps + prisma generate + db push + seed + start server + health check
./scripts/down.sh         # Stop server (graceful)
./scripts/down.sh --force # Kill server + orphan processes (playwright, jest, next-server)
./scripts/down.sh --clean # Stop server + remove .env.local, node_modules, .next, .turbo
./scripts/down.sh --force --clean # Force kill everything + clean
./scripts/check.sh        # Diagnostic: status (OK/PENDING/DEGRADED) with HTTP health check
./scripts/check.sh --fix  # Diagnostic + auto-fix: kills orphans, restarts if degraded/stopped
./scripts/watch.sh        # Tail server logs
./scripts/watch.sh --ps   # Show running processes (updates every 1s)
```

**Server port:** Configured via `SERVER_PORT` in `.env.local`. All scripts read from this variable. **Obs:** If using worktrees, always use ./scripts/down.sh --force --clean in order to clean the port and start a new server by using the init script.

### Common Commands

```bash
npm run build               # Production build
npm run lint                # ESLint check
npm run lint:fix            # ESLint with auto-fix
npm run db:push             # Sync schema to dev DB (prisma db push)
npm run db:push:test        # Sync schema to test DB
npm run db:seed             # Seed database with test data
npm run db:migrate          # Generate PostgreSQL migration (production only)
npm run db:reset            # Reset DB + migrate + seed
npm test                    # Jest tests (uses test DB)
npm run test:watch          # Jest watch mode
npm run test:coverage       # Jest coverage report
```

## Tech Stack

- Next.js 16 (App Router)
- React 19
- TypeScript (strict mode)
- Tailwind CSS 4 (tokens via `@theme inline` in globals.css, NO tailwind.config.js)
- NextAuth.js v5 beta
- Prisma 7 (client generated in src/generated/prisma/)
- PostgreSQL (dev, test, and production). Driver: pg + @prisma/adapter-pg

## Project Structure

```
├── src/
│   ├── app/
│   │   ├── api/
│   │   │   └── auth/[...nextauth]/
│   │   ├── globals.css                 # Tailwind 4 tokens (@theme inline)
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── layout/
│   │   └── shared/
│   ├── generated/prisma/           # Prisma 7 client (gitignored)
│   ├── lib/                        # auth, db, validations
│   ├── tests/
│   │   ├── helpers/
│   │   │   ├── db.ts               # Test DB client + cleanup utilities
│   │   │   └── auth.ts             # NextAuth session mocking helpers
│   │   └── examples/               # Reference patterns (safe to delete)
│   └── middleware.ts
├── prisma/
│   ├── schema.prisma
│   └── seed.ts
├── scripts/                        # init, down, check, watch, tmux, deploy
├── .env.example
├── prisma.config.ts                # Prisma 7 config (dotenv loading)
├── next.config.ts
├── tsconfig.json
└── eslint.config.mjs
```

## Testing

- Before running tests, verify the environment is set up and the server is running. Otherwise, run `./scripts/init.sh`.

### Test Quality Rules

**Test behavior and logic, not implementation details.**
- Every test must validate a business decision or user flow, not static markup.
- Do not test CSS classes, static HTML attributes, or element presence without interaction.
- Do not mock an entire dependency -- if everything is mocked, the test validates mocks, not code.

### Unit & Integration Tests (Jest)

**Commands:**

```bash
npm test                    # Run all Jest tests (uses .env.test DB)
npm run test:watch          # Watch mode (re-runs on file save)
npm run test:coverage       # Coverage report (output in coverage/)
npm run db:push:test        # Sync schema to test DB (run after schema changes)
```

**Test file locations:**
- Unit tests: colocated alongside source files as `*.test.ts` / `*.test.tsx`
- Shared helpers: `src/tests/helpers/` (db.ts, auth.ts)
- Example tests: `src/tests/examples/` (reference only, safe to delete)

**Patterns:**

1. **Pure logic (Zod schemas, utils):** No setup needed. Import and call directly.
2. **DB integration tests:** Use `getTestPrisma()` from `@/tests/helpers/db`. Call `resetDb()` in `beforeEach`. Call `disconnectTestDb()` in `afterAll`.
3. **API route tests with auth:** Mock `@/lib/auth` and `@/lib/db` at the top of the file (before imports). Use `mockAuth.mockResolvedValue(TEST_USER_SESSION)` per test.
4. **React component tests:** Add `@jest-environment jsdom` docblock at top. Use `@testing-library/react`.

**Rules:**
- Always run `npm run db:push:test` after changing `prisma/schema.prisma`.
- Update `cleanupTestDb()` in `src/tests/helpers/db.ts` when adding new models (FK-safe delete order).
- Never import from `@/lib/db` in test helpers — use `getTestPrisma()` directly.
- `jest.mock(...)` calls must appear before `import` statements (Jest hoists them automatically).

### E2E Verification Rules

- Run `./scripts/check.sh --fix` before E2E tests to ensure the server is running.

**Rules:**

1. Read `SERVER_PORT` from `.env.local`. Use it in all URLs: `http://localhost:<SERVER_PORT>/path`.
2. Use playwright-cli for navigation, web testing, form filling, and screenshots.
3. After each navigation, check browser console for errors -- any compilation/runtime error means FAILURE.
4. Use playwright-cli with headless mode.
5. Never create playwright test files for E2E UI verification.
6. Save screenshots to `.playwright-cli/`, never the project root.
7. After testing, remove all files in `.playwright-cli/` folder.

## Database

PostgreSQL for all environments (dev, test, production).

- Dev: `postgresql://postgres:postgres@localhost:5433/{{PROJECT_DB_NAME}}`
- Test: `postgresql://postgres:postgres@localhost:5433/{{PROJECT_DB_NAME}}_test`
- Production: `POSTGRES_URL_NON_POOLING` or `DIRECT_DATABASE_URL` (Vercel/Supabase)

### How it works

- `src/lib/db.ts` uses `pg.Pool` + `PrismaPg` adapter. Prisma 7 always requires an adapter.

### Schema changes

- **Dev/test:** `npm run db:push` (dev DB) or `npm run db:push:test` (test DB).
- **Production:** `prisma migrate dev --name <name>` to generate, `prisma migrate deploy` to apply.
- **First deploy:** Run `npx prisma migrate dev --name init` locally before the first production deploy to generate the initial migration.

## Development

### Code Patterns

- Private components in `_components/` inside each route folder
- `"use client"` only on interactive components (modals, forms, managers)
- API routes: session check -> Zod validation -> Prisma query -> NextResponse.json()
- Always use `@/` import alias
- Zod schemas centralized in `lib/validations.ts`

### Commit Convention

```
Format: <type>: <description in English>
Types: feat, fix, docs, test, chore, refactor
- Lowercase after the type
- Co-Authored-By is included automatically
```

## Rules
- Never skip a task because you don't have a running server. Always run `./scripts/init.sh`.
- Never run `npm run dev` or `next dev` directly. Always use `./scripts/init.sh` to start the server.
- Never install packages or dependencies without asking the user first.


### Tmux

Run `./scripts/tmux-dev.sh` to create a detached tmux session named after the project. Attach with: `tmux attach -t {{PROJECT_NAME}}`