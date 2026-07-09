# escrever-prd

Cria e edita PRDs (Product Requirements Documents) estruturados — o **documento de negócio** da feature. Trabalha em modo draft-first: gera o documento a partir do que o usuário fornecer, marcando premissas inline para revisão pontual. O PRD cobre problema, solução de produto, escopo, funcionalidades (User Stories com Rules e Edge cases), critérios de aceite e métricas, fluxo de negócio e milestones. Detalhe técnico (stack, arquitetura, NFR global) fica no TRD; decisão arquitetural durável vira ADR. Também funciona como documento de controle de estado da feature, via campo `status` e grafo de `depends_on`.

## Pré-requisitos e configuração

Nenhum. Funciona sem configuração prévia.

## Dependências externas

Nenhuma.

## Skills relacionadas

- **brainstorm** — use brainstorm para madurar a ideia antes de formalizar com escrever-prd
- **banco-de-ideias** — registre a ideia no Notion antes de escrever o PRD formal

## Exemplos de uso

```
Quero criar um PRD para um sistema de autenticação com SSO

Cria um documento de requisitos para uma API de pagamentos

Preciso planejar uma feature de notificações em tempo real para o nosso app

Criar PRD: plataforma de agendamento de consultas médicas online

Ajusta o PRD 003 para incluir o fluxo de convite por e-mail

Refinar o PRD de pagamentos: faltou o edge case de reembolso parcial
```

## Limitações conhecidas

- O PRD é salvo por padrão em `./docs/prds/<nome>.md` — se o diretório não existir, é criado automaticamente
- A qualidade do documento depende da riqueza das informações fornecidas — quanto mais contexto, menos perguntas de complemento
- Não gera código, diagramas de banco de dados ou especificações técnicas detalhadas — foca em requisitos e escopo
- Critérios de sucesso vagos ou não verificáveis são sinalizados para revisão
- PRDs com `status: concluído` são imutáveis e não devem ser editados — mudanças posteriores de comportamento devem abrir um novo PRD
