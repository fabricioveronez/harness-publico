# docker-practices

Skill prescritiva e didática para Dockerfile, imagens Docker e docker-compose — multi-stage, segurança, camadas, healthchecks, networks, volumes e orquestração local. Aplica convenções diretamente ao código enquanto escreve, e tem guias de aprofundamento para quando o aluno quer entender o "porquê" das práticas.

Ativa sempre que a tarefa envolver criar ou revisar artefatos Docker, mesmo sem o usuário pedir explicitamente por "boas práticas".

## Estrutura

```
skills/docker-practices/
├── SKILL.md                                   ← guia prescritivo (sempre carregado)
└── references/                                ← carregados sob demanda
    ├── por-que-multi-stage-e-camadas.md       ← modelo mental + cache + multi-stage
    ├── escolhendo-base-image.md               ← alpine vs slim vs distroless
    ├── seguranca-em-containers.md             ← non-root, secrets, supply chain, scans
    └── compose-para-desenvolvimento.md        ← depends_on, healthchecks, override
```

O `SKILL.md` cobre o "o que fazer" (regras prescritivas). Os references explicam o "porquê" e cobrem casos do mundo real — incidentes, erros comuns de iniciante, anatomia de Dockerfiles linha a linha.

## Pré-requisitos e configuração

- Docker Engine 20.10+ (para BuildKit habilitado por default)
- Docker Compose V2 (`docker compose`, não `docker-compose`)

## Quando os references são carregados

A skill instrui o LLM a puxar reference sob demanda baseado no cenário:

| Cenário | Reference |
|---|---|
| Dockerfile do zero, build lento, dúvida sobre camadas/multi-stage | `por-que-multi-stage-e-camadas.md` |
| Dúvida entre alpine/slim/distroless, imagem enorme, "shared library not found" | `escolhendo-base-image.md` |
| Antes de produção, "scan", "supply chain", "CVE", non-root | `seguranca-em-containers.md` |
| Ambiente local com banco/Redis/fila, app não responde após `compose up` | `compose-para-desenvolvimento.md` |

## Skills relacionadas

- **kubernetes-practices** — imagens construídas seguindo estas práticas rodam bem em K8s
- **github-actions-practices** — build e push de imagens em workflows de CI
- **terraform-practices** — provisionar registry e infra para hospedar imagens

## Exemplos de uso

```
Revisa esse Dockerfile e aponta o que está fora do padrão

Melhora esse Dockerfile para reduzir tamanho e usar multi-stage

Cria um compose.yaml para subir postgres, redis e a API com healthchecks

Adiciona usuário não-root nessa imagem

Converte esse docker-compose.yml antigo para Compose V2

Por que minha imagem Python tá com 1.5 GB?
```

## Limitações conhecidas

- Guia prescritivo + didático — pode conflitar com convenções já estabelecidas no projeto. Quando houver conflito, as convenções do repositório prevalecem; informe no prompt
- Não cobre orquestração de produção (Kubernetes, Swarm, ECS) — docker-compose aqui é tratado como ferramenta de desenvolvimento local
- Não cobre build de imagens multi-arch (`buildx`) em profundidade — menciona pinning mas não estratégias de release
- Não substitui scanners (Trivy, Snyk, Docker Scout) — é guia de escrita, não verificação automatizada
- Exemplos predominantemente em Node.js por convenção — convenções aplicam-se a qualquer linguagem, ajuste base image e comandos

## Para o aluno

Esta skill ilustra um padrão de **progressive disclosure**: o `SKILL.md` é o "manual de bolso" do dia-a-dia, e os references são as "aulas profundas" para quando você quiser entender de verdade. Você pode usar a skill sem nunca abrir os references — mas vai abrir quando quiser entender por que cada regra existe, ou quando bater num problema do mundo real.
