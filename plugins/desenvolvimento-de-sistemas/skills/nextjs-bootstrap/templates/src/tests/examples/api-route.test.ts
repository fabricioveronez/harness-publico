/**
 * Example: Testing a Next.js App Router API route
 *
 * Pattern: mock auth -> mock db -> call route handler -> assert response
 *
 * To use with a real route, replace the stub GET function below
 * with: import { GET } from '@/app/api/users/me/route'
 */

import { NextRequest } from 'next/server'
import { TEST_USER_SESSION } from '@/tests/helpers/auth'

// Mock auth before importing modules that use it
jest.mock('@/lib/auth', () => ({
  auth: jest.fn(),
}))

import { auth } from '@/lib/auth'
const mockAuth = auth as jest.MockedFunction<typeof auth>

// Stub route handler -- replace with your real import
async function GET() {
  const session = await auth()
  if (!session) {
    return Response.json({ error: 'Unauthorized' }, { status: 401 })
  }
  return Response.json({ user: session.user })
}

describe('GET /api/users/me', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  it('returns 401 when not authenticated', async () => {
    mockAuth.mockResolvedValue(null as never)

    const res = await GET()

    expect(res.status).toBe(401)
    const body = await res.json()
    expect(body.error).toBe('Unauthorized')
  })

  it('returns current user when authenticated', async () => {
    mockAuth.mockResolvedValue(TEST_USER_SESSION as never)

    const res = await GET()

    expect(res.status).toBe(200)
    const body = await res.json()
    expect(body.user.email).toBe(TEST_USER_SESSION.user.email)
  })
})
