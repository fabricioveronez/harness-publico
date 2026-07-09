# nextjs-bootstrap

Cria a estrutura inicial de um novo projeto Next.js com arquitetura battle-tested (App Router, TypeScript strict, Prisma 7, PostgreSQL, NextAuth v5, Tailwind CSS 4). Gera CLAUDE.md completo, scripts operacionais idempotentes (init, down, check, watch, tmux, deploy), schema Prisma, seed, middleware, rota de auth e `.env.example` — tudo adaptado ao nome do projeto informado.

## Pré-requisitos e configuração

- Node.js e gerenciador de pacotes (npm/pnpm) instalados
- PostgreSQL acessível localmente (ou via Docker) — o script configura dois bancos: `<nome>_dev` e `<nome>_test`
- `tmux` instalado se quiser usar o script de sessão

## Dependências externas

- **Next.js** (App Router, TypeScript)
- **Prisma 7** como ORM
- **PostgreSQL** como banco de dados
- **NextAuth v5** para autenticação
- **Tailwind CSS 4** para estilização
- **bcryptjs** e **Zod** para hashing e validação

## Skills relacionadas

- **escrever-prd** — escreva o PRD da primeira feature antes de iniciar o bootstrap
- **typescript-practices** — aplica automaticamente após o bootstrap, pois o projeto nasce em TypeScript strict
- **guia-de-testes** e **teste-e2e-navegacao** — usadas nas features criadas a partir do scaffold

## Exemplos de uso

```
Cria um novo projeto Next.js chamado "loja-online"

Bootstrap de um nextjs para um app de agendamento de consultas

Scaffold um projeto greenfield com nossa arquitetura padrão

Configura um novo nextjs com IA nesse diretório

Inicia um projeto do zero com Prisma e NextAuth para um marketplace
```

## Limitações conhecidas

- Stack fixa — não suporta troca de banco (MySQL/SQLite), ORM alternativo (Drizzle/TypeORM) ou outro provider de auth sem edição manual pós-bootstrap
- O diretório de destino precisa estar vazio ou não existir — o script não sobrescreve projetos existentes
- `.env.example` nunca contém credenciais reais — o usuário precisa preencher o `.env.local` antes de rodar `./scripts/init.sh`
- Scripts assumem Linux/macOS — Windows exige WSL ou adaptação manual
- Nome do projeto deve ser kebab-case — é usado como diretório, nome do banco e sessão tmux simultaneamente
- Instalação de pacotes fora do stack principal exige confirmação explícita antes de ser feita
