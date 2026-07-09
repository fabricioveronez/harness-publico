export default function Home() {
  return (
    <main className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-[var(--color-background)]">
      {/* Background gradient orbs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-40 -left-40 h-96 w-96 rounded-full bg-[var(--color-primary)] opacity-10 blur-3xl" />
        <div className="absolute -right-40 -bottom-40 h-96 w-96 rounded-full bg-[var(--color-secondary)] opacity-10 blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 flex flex-col items-center gap-8 px-6 text-center">
        {/* Badge */}
        <span className="inline-flex items-center gap-2 rounded-full border border-[var(--color-primary)]/20 bg-[var(--color-primary)]/5 px-4 py-1.5 text-sm font-medium text-[var(--color-primary)]">
          Bootstrapped with a Custom Skill
        </span>

        {/* Heading */}
        <h1 className="max-w-2xl text-5xl font-bold tracking-tight text-[var(--color-foreground)] sm:text-6xl">
          Welcome to your
          <span className="bg-gradient-to-r from-[var(--color-primary)] to-[var(--color-secondary)] bg-clip-text text-transparent">
            {' '}new project
          </span>
        </h1>

        {/* Description */}
        <p className="max-w-lg text-lg text-[var(--color-secondary)]">
          Next.js + TypeScript + Tailwind CSS 4 + Prisma 7 + NextAuth v5.
          Everything is configured and ready to build.
        </p>

        {/* Tech stack pills */}
        <div className="flex flex-wrap justify-center gap-2">
          {['Next.js', 'TypeScript', 'Tailwind 4', 'Prisma 7', 'NextAuth v5', 'PostgreSQL'].map(
            (tech) => (
              <span
                key={tech}
                className="rounded-lg border border-[var(--color-foreground)]/10 bg-[var(--color-foreground)]/5 px-3 py-1 text-sm text-[var(--color-foreground)]/70"
              >
                {tech}
              </span>
            ),
          )}
        </div>

      </div>

    </main>
  )
}
