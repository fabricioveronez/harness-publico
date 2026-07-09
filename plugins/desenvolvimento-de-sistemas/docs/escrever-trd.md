# escrever-trd

Cria e mantém o TRD (Technical Requirements Document) do projeto em `docs/trd.md`.

## O que é o TRD

O TRD é o documento técnico global do projeto: um arquivo único, versionado no repositório,
que captura stack, arquitetura, requisitos não-funcionais, dependências externas, padrões e
decisões globais. Ele é a fonte de contexto técnico que `criar-plan` e `implementar-task`
carregam automaticamente — sem ele, essas skills operam às cegas e podem gerar planos ou
implementações que divergem da realidade.

Granularidade deliberadamente baixa: o TRD cobre o que é global e estável. Requisitos de
uma feature ficam no PRD; decisões técnicas relevantes ficam em ADRs, criados por esta
skill no **Modo Decision**.

## Quando usar

- Ao iniciar um projeto novo que ainda não tem TRD
- Antes de gerar o primeiro plano via `criar-plan` (especialmente se ela pediu contexto técnico global)
- Quando a stack mudou e o TRD existente está desatualizado
- Quando novas dependências externas foram adicionadas ao projeto
- Quando o usuário mencionar "documentar a stack", "contexto técnico do projeto", "TRD" ou "arquitetura do projeto"

## Como invocar

A skill detecta Criação vs Edição automaticamente; o Modo Decision é acionado por intenção:

```
# Criação (docs/trd.md não existe)
escrever-trd

# Edição (docs/trd.md já existe)
escrever-trd
# ou: "atualizar o TRD", "o TRD está desatualizado"

# Decision (registrar uma decisão técnica como ADR)
"registra a decisão de usar Postgres em vez de Mongo"
# ou: "cria um ADR para…", "decidimos trocar X por Y"
```

## Fluxo interno

A skill executa 5 passos antes de gravar qualquer arquivo:

1. **Análise automática** — lê arquivos do projeto (`package.json`, lockfiles, `.env.example`,
   `docker-compose.yml`, configs de infra etc.) para inferir stack, arquitetura, padrões e
   dependências externas sem precisar perguntar
2. **Enriquecimento por busca externa** — para cada dependência externa identificada, busca
   constraints públicos (rate limits, SLAs, comportamentos padrão) via qualquer MCP ou
   ferramenta disponível; resultado vira sugestão pré-preenchida com fonte, validada pelo
   usuário no preview
3. **Mini-entrevista** — cobre apenas o que não foi inferível nem enriquecido (≤5 perguntas)
4. **Varredura de ADRs** — escaneia `docs/adrs/` e lista referências progressivas
5. **Preview e gravação** — exibe as 6 seções para confirmação antes de gravar

O **Modo Decision** segue um fluxo próprio e mais curto: numera o ADR, gera-o draft-first a
partir de `references/template-adr.md`, trata supersedência (novo ADR com `supersedes`, antigo
vira `obsoleto`) e atualiza a seção Decisões Globais do TRD.

## Estrutura do TRD gerado

O TRD segue a estrutura canônica de `references/template-trd.md` com 6 seções:

| Seção | Conteúdo |
|---|---|
| **Stack** | Linguagem, runtime, framework, banco, ferramentas de build e pacotes |
| **Arquitetura** | Padrão arquitetural, estrutura de pastas, módulos principais |
| **Requisitos Não-Funcionais** | Performance, disponibilidade/SLA, escalabilidade, segurança, observabilidade — com valores mensuráveis |
| **Dependências Externas** | APIs de terceiros, serviços de infraestrutura e sistemas internos com SLA, rate limit ou contrato relevante |
| **Padrões** | Testes (framework + comando), estilo de código, error handling, logging, auth |
| **Decisões Globais** | Referências progressivas a ADRs (título, data, status, link) |

## Posição no fluxo spec-driven

```
escrever-prd → escrever-trd → criar-plan → implementar-task → validar-implementacao
                    ▲
           gera docs/trd.md
                    │
          carregado automaticamente por
          criar-plan e implementar-task
```

## Relação com outras skills

| Skill | Relação |
|---|---|
| `criar-plan` | Consome `docs/trd.md` como contexto técnico global; sem ele, entra em mini-modo de coleta |
| `implementar-task` | Consome `docs/trd.md` quando referenciado pelo PLAN.md |
| `escrever-prd` | Independente — PRDs documentam features, TRD documenta o projeto |
| ADRs (`docs/adrs/`) | Criados pela própria skill no **Modo Decision** (`docs/adrs/NNN-slug.md`), que também atualiza a seção Decisões Globais |
