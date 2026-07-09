// Branding + taxonomia centralizados. Ponto único de reskin e a fronteira que
// torna barata a futura extração de um template genérico (ver plano site-first).

// Slug do repositório (owner/repo), usado para montar os comandos `npx skills add`.
const repoSlug = 'fabricioveronez/harness-publico';

export const site = {
  name: 'Harness Público',
  tagline: 'Marketplace público de plugins e skills para o Claude Code',
  // Logo servida de site/public/ (URL na raiz). Troque o arquivo para reskin — sem mudar código.
  logo: '/logo.svg',
  description:
    'Vitrine navegável dos plugins e skills técnicos compartilháveis (desenvolvimento de sistemas, devops) — derivada direto dos arquivos do repositório.',
  repo: {
    slug: repoSlug,
    // Instala todas as skills do repo (aninhadas em plugins/*/skills/*) — precisa de --full-depth.
    installAll: `npx skills add ${repoSlug} --full-depth`,
  },
  author: {
    name: 'Fabricio Veronez',
    email: 'fabricio@veronez.io',
  },
} as const;

export type SiteConfig = typeof site;
