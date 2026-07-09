# github-actions-practices

Skill prescritiva e didática para workflows do GitHub Actions — estrutura de workflow, triggers, permissions mínimas, OIDC, secrets, matrix, cache, concurrency, reusable workflows, composite actions e pinning de actions. Aplica convenções diretamente aos arquivos, e tem guias de aprofundamento para quando o aluno quer entender o "porquê" das práticas.

Ativa sempre que a tarefa envolver criar ou revisar workflows em `.github/workflows/`, mesmo sem o usuário pedir explicitamente por "boas práticas".

## Estrutura

```
skills/github-actions-practices/
├── SKILL.md                              ← guia prescritivo (sempre carregado)
└── references/                           ← carregados sob demanda
    ├── anatomia-de-um-workflow.md        ← workflow/job/step, contexto, expressões
    ├── seguranca-em-pipelines.md         ← pull_request_target, OIDC, permissions, pinning
    └── performance-e-reuso.md            ← cache, matrix, concurrency, reusable, composite
```

O `SKILL.md` cobre o "o que fazer" (regras prescritivas). Os references explicam o "porquê" e cobrem casos do mundo real — incidentes de segurança, anatomia de workflows linha a linha, decisões de performance.

## Pré-requisitos e configuração

- Repositório no GitHub com Actions habilitado
- Para OIDC: trust relationship configurado na cloud de destino (AWS IAM Role, GCP Workload Identity, Azure Federated Credentials)

## Quando os references são carregados

| Cenário | Reference |
|---|---|
| Primeiro workflow, herdando workflow alheio, decifrando `${{ ... }}`, "não rodou" | `anatomia-de-um-workflow.md` |
| Adicionando secret, workflow em PR, deploy em cloud, OIDC, `pull_request_target` | `seguranca-em-pipelines.md` |
| CI passou de 5min, copiando 8 steps em 4 workflows, push novo não cancela | `performance-e-reuso.md` |

## Skills relacionadas

- **docker-practices** — build e push de imagens em workflows
- **kubernetes-practices** — deploy de manifests via pipeline
- **terraform-practices** — execução de `terraform plan`/`apply` em workflows com OIDC

## Exemplos de uso

```
Revisa esse workflow e aponta problemas de segurança e performance

Adiciona permissions mínimas e concurrency nesse workflow

Converte esse workflow para usar OIDC em vez de AWS access keys

Extrai esses steps repetidos em uma composite action

Cria um reusable workflow para o deploy de staging e prod

Por que meu CI demora 8 minutos mesmo com cache?
```

## Limitações conhecidas

- Específico de **GitHub Actions** — não cobre GitLab CI, Jenkins, Azure Pipelines, CircleCI. Para outras ferramentas, consulte documentação nativa
- Não cobre self-hosted runners em detalhe — exemplos assumem runners hospedados do GitHub
- Não aborda GitHub Actions em **enterprise/on-prem** (GHES) — sintaxe é idêntica, mas integrações podem divergir
- Não substitui scanners de workflow (actionlint, StepSecurity) — é guia de escrita
- Não cobre bilhetagem/cost optimization — foco é qualidade e segurança

## Para o aluno

Esta skill ilustra **progressive disclosure**: o `SKILL.md` é o "manual de bolso" prescritivo, e os references são as "aulas profundas" para entender de verdade os porquês. O reference `seguranca-em-pipelines.md`, em particular, ensina o modelo de ameaça do CI/CD e por que `pull_request_target` é uma armadilha comum — vale ler **antes** de copiar workflow de fonte desconhecida.
