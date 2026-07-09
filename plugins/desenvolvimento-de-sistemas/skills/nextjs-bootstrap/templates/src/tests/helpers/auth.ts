export type MockSession = {
  user: {
    id: string
    email: string
    name?: string | null
  }
  expires: string
}

export const TEST_USER_SESSION: MockSession = {
  user: {
    id: 'test-user-id',
    email: 'test@example.com',
    name: 'Test User',
  },
  expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
}
