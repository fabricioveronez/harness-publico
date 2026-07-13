# Harness Público — Marketplace de Plugins (Claude Code)

Marketplace **público** de plugins personalizados para o Claude Code, seguindo o padrão oficial de plugin marketplace. Reúne skills técnicas compartilháveis com a comunidade.

> Parte do conjunto `harness-repos/` (Pessoal · Público · Empresarial). Veja também `harness-pessoal` e `harness-empresarial`.

## Como instalar

Via [`npx skills`](https://github.com/vercel-labs/skills) (skills aninhadas em `plugins/*/skills/*` → `--full-depth`):

```bash
# Instalar todas as skills
npx skills add fabricioveronez/harness-publico --full-depth

# Instalar as skills de um plugin
npx skills add fabricioveronez/harness-publico/plugins/devops/skills

# Instalar uma skill específica
npx skills add fabricioveronez/harness-publico@docker-practices --full-depth
```

## Plugins

| Plugin | Descrição |
|--------|-----------|
| `spec-driven-development`     | Fluxo spec-driven para software: PRD, TRD, revisão, plano/tasks e implementação |
| `desenvolvimento-de-sistemas` | Boas práticas (Python/TypeScript), bootstrap Next.js e testes (unit/E2E) |
| `devops`                      | Docker, Kubernetes, Terraform, GitHub Actions, runbooks |

## Estrutura

```
harness-publico/
├── .claude-plugin/marketplace.json
├── plugins/<dominio>/
│   ├── .claude-plugin/plugin.json
│   ├── skills/<skill>/SKILL.md
│   └── docs/<skill>.md
└── site/               # vitrine local (Astro) — projeção pura do repositório
```

## Vitrine local (site)

```bash
cd site
npm install
npm run dev        # http://localhost:4321
npm run build      # dist/ + busca Pagefind (npm run preview para ver a busca)
```
