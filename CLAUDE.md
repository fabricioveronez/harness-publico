# CLAUDE.md

Guia para o Claude Code neste repositório.

## Sobre o Repositório

Marketplace **público** de plugins para o Claude Code, seguindo o padrão oficial de plugin marketplace. Cada domínio é um plugin independente que pode conter skills, agents, hooks e commands.

Faz parte do conjunto `~/projetos/harness-repos/`:

- `harness-pessoal` — skills pessoais (gestao-pessoal, spec-driven-ops, uso-geral) — **privado**
- `harness-publico` — **este repo**: skills técnicas compartilháveis (desenvolvimento-de-sistemas, devops)
- `harness-empresarial` — IP de conteúdo (producao-de-conteudo, edicao-de-video, educacao-e-cursos) — **privado**

## Estrutura

```
harness-publico/
├── .claude-plugin/marketplace.json   # catálogo do marketplace
├── plugins/<dominio>/
│   ├── .claude-plugin/plugin.json    # manifesto do plugin
│   ├── skills/<skill>/SKILL.md       # skills
│   └── docs/<skill>.md               # documentação das skills
└── site/                             # vitrine local (Astro) — projeção pura do repo
```

## Plugins (Domínios)

- `desenvolvimento-de-sistemas` — PRDs, TRDs, planos, testes, bootstrap, TypeScript
- `devops` — Docker, Kubernetes, Terraform, GitHub Actions, runbooks

## Formato de uma Skill

`SKILL.md` com frontmatter mínimo (`name`, `description`). Versão/autor ficam no `plugin.json` e no `marketplace.json`.

## Regras

- Skills em `plugins/<dominio>/skills/<nome>/SKILL.md`; docs em `plugins/<dominio>/docs/<nome>.md`.
- Metadados de versão/autor no `plugin.json` do domínio.
- Novas skills dentro do plugin/domínio correspondente.

## Como mover um plugin entre repos (harness-pessoal / -publico / -empresarial)

Ao rebalancear um plugin de escopo:

1. **Copiar** o plugin inteiro para o repo destino: `rsync -a --exclude='.DS_Store' plugins/<x> <destino>/plugins/`.
2. **Registrar** no `.claude-plugin/marketplace.json` do destino (adicionar entrada do plugin) e ajustar `site/src/site.config.ts` se necessário.
3. **Remover** da origem: `git rm -r plugins/<x>` (ou `rm -rf` se não versionado) e tirar do `marketplace.json` da origem.
4. **Repontar symlinks**: qualquer symlink em `~/.claude/skills/*` ou `~/projetos/*/.claude/skills/*` que apontava para o caminho antigo precisa ser recriado apontando para o novo repo. Detectar quebrados: `find ~/projetos ~/.claude -type l ! -exec test -e {} \; -print`.
5. **Commit** nos dois repos.
