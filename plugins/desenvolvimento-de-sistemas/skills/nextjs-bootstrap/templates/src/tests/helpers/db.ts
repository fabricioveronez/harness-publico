import { Pool } from 'pg'
import { PrismaPg } from '@prisma/adapter-pg'
import { PrismaClient } from '@/generated/prisma'

let testPool: Pool | null = null
let testPrisma: PrismaClient | null = null

export function getTestPrisma(): PrismaClient {
  if (!testPrisma) {
    testPool = new Pool({ connectionString: process.env.DATABASE_URL })
    const adapter = new PrismaPg(testPool)
    testPrisma = new PrismaClient({ adapter })
  }
  return testPrisma
}

/**
 * Delete all records in FK-safe order.
 * Update this list when you add new models to schema.prisma.
 */
export async function cleanupTestDb(): Promise<void> {
  const prisma = getTestPrisma()
  await prisma.user.deleteMany()
}

export async function disconnectTestDb(): Promise<void> {
  if (testPrisma) {
    await testPrisma.$disconnect()
    testPrisma = null
  }
  if (testPool) {
    await testPool.end()
    testPool = null
  }
}

export async function resetDb(): Promise<void> {
  await cleanupTestDb()
}
