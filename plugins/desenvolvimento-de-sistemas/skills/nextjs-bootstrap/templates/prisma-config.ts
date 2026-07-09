import path from 'node:path'
import { config } from 'dotenv'
import { defineConfig } from 'prisma/config'

// Load .env.local for Prisma CLI commands
config({ path: path.resolve(process.cwd(), '.env.local') })

export default defineConfig({
  earlyAccess: true,
  schema: path.resolve(process.cwd(), 'prisma/schema.prisma'),
  datasource: {
    url: process.env.DATABASE_URL!,
  },
})
