import NextAuth from 'next-auth'

const { auth } = NextAuth({
  providers: [],
  pages: {
    signIn: '/login',
  },
})

export default auth

export const config = {
  matcher: ['/((?!api/auth|login|_next/static|_next/image|favicon.ico).*)'],
}
