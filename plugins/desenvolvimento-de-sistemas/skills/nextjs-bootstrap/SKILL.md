---
name: nextjs-bootstrap
description: |
  Cria a estrutura inicial de um novo projeto Next.js com nossa arquitetura padrão, CLAUDE.md e scripts operacionais.
  Use esta skill sempre que o usuário quiser iniciar um novo projeto Next.js, criar um novo app, começar um projeto
  do zero ou configurar uma aplicação greenfield. Também use quando o usuário disser coisas como
  "novo projeto", "bootstrap", "scaffold", "configurar nextjs", ou "criar um nextjs com IA".
---

# Bootstrap de Projeto Next.js

Configura um novo projeto Next.js com uma arquitetura battle-tested: App Router, TypeScript strict, Prisma 7, PostgreSQL, NextAuth v5 e Tailwind CSS 4. Gera um CLAUDE.md completo, scripts operacionais (init, down, check, watch, tmux, deploy) e estrutura de projeto pronta para desenvolvimento assistido por IA.

## Fluxo de Trabalho

### 1. Coletar Informações do Projeto

Pergunte ao usuário:

1. **Nome do projeto** (kebab-case, usado para diretório, nome do banco e sessão tmux)
2. **Descrição do projeto** (uma linha para o CLAUDE.md)
3. **Diretório de destino** (onde criar/configurar o projeto)

### 2. Executar Script de Bootstrap

Execute o script de bootstrap com as informações coletadas:

```bash
<skill-path>/scripts/bootstrap.sh <nome-do-projeto> "<descrição-do-projeto>" <diretório-de-destino>
```

O script irá:
- Criar um app Next.js (se o destino estiver vazio ou não existir)
- Remover arquivos incompatíveis com Tailwind 4 (tailwind.config, postcss.config)
- Instalar todas as dependências (Prisma, NextAuth, bcryptjs, Zod)
- Copiar e configurar scripts operacionais (init, down, check, watch, tmux, deploy)
- Copiar templates de arquivos fonte (lib/db, lib/auth, lib/validations, middleware, rota de auth)
- Configurar schema Prisma, config e arquivo seed
- Gerar CLAUDE.md e .env.example com os valores corretos do projeto
- Adicionar scripts ao package.json (db:push, db:seed, db:migrate, etc.)
- Atualizar .gitignore e gerar o cliente Prisma

Todos os templates ficam em `<skill-path>/templates/` como arquivos editáveis. O script substitui os placeholders `{{PROJECT_NAME}}`, `{{PROJECT_DESCRIPTION}}` e `{{PROJECT_DB_NAME}}`.

### 3. Reportar Resultados

Informe ao usuário:
1. Execute `./scripts/init.sh` para iniciar tudo (env, banco de dados, servidor dev)
2. O CLAUDE.md está pronto — o Claude Code seguirá os padrões do projeto
3. Sugira próximos passos: criar a primeira feature, adicionar dados seed, etc.

## Regras de Adaptação

- **Nome do projeto** substitui todas as instâncias de valores específicos do projeto (nome do banco, sessão tmux, caminho do arquivo de log)
- **Nomes de banco** são derivados do nome do projeto: `nome_projeto` (dev), `nome_projeto_test` (test)
- Scripts sempre leem `SERVER_PORT` do `.env.local` — nunca hardcoded
- Scripts usam `PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"` para portabilidade
- Todos os scripts são idempotentes — seguros para executar múltiplas vezes

## Padrões de Código

Todos os padrões de código e convenções estão definidos no template CLAUDE.md gerado (`<skill-path>/templates/claude-md.md`). Siga esses padrões ao gerar qualquer código durante o bootstrap.

## Regras
- .env.example nunca deve conter credenciais reais
- Sempre pergunte antes de instalar pacotes adicionais além do stack principal
