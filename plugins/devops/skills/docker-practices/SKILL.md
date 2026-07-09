---
name: docker-practices
description: "Boas práticas e padrões de qualidade para Dockerfile, imagens Docker e docker-compose. Use esta skill sempre que estiver escrevendo, revisando ou otimizando Dockerfile, .dockerignore, docker-compose.yml, compose.yaml ou executando comandos docker/docker compose — inclui multi-stage builds, segurança, camadas, healthchecks, networks, volumes e orquestração local para desenvolvimento. Ativar mesmo quando o usuário não pedir explicitamente por 'boas práticas', bastando que a tarefa envolva criar ou revisar artefatos Docker."
---

# Docker Practices

Guia prescritivo de boas práticas para Dockerfile, imagens Docker e docker-compose. Aplique estas convenções diretamente ao código sem explicar cada decisão — o objetivo é consistência, segurança e performance, não ensinar conceitos.

O documento tem duas partes:
1. **Dockerfile e imagem** — build e convenções de artefato
2. **docker-compose** — orquestração local para desenvolvimento

## Quando aprofundar

Os guias em `references/` aprofundam o "porquê" das práticas e cobrem casos do mundo real. Carregue sob demanda quando:

| Cenário | Reference |
|---|---|
| Escrevendo Dockerfile do zero, ou debugando build lento, ou tentando entender camadas/multi-stage | `references/por-que-multi-stage-e-camadas.md` |
| Em dúvida entre alpine/slim/distroless, ou imagem ficou enorme, ou falha "shared library" em runtime | `references/escolhendo-base-image.md` |
| Antes de subir imagem em produção pela primeira vez, ou alguém menciona "scan", "supply chain", "CVE" | `references/seguranca-em-containers.md` |
| Montando ambiente local com banco/Redis/fila, ou `docker compose up` sobe mas app não responde | `references/compose-para-desenvolvimento.md` |

---

## Parte 1 — Dockerfile e imagem

### Base image

- Use tags pinadas com versão específica — nunca `latest` em produção
- Prefira imagens oficiais ou de fornecedores confiáveis (Microsoft, Bitnami, Chainguard)
- Prefira variantes slim/alpine/distroless quando compatíveis com o runtime — reduzem superfície de ataque e tamanho
- Distroless para binários estáticos (Go, Rust, Java com jlink) — sem shell, sem package manager
- Alpine apenas quando a lib C (musl vs glibc) não for problema — alguns binários Python/Node precisam glibc

```dockerfile
# Bom — tag pinada e slim
FROM node:20.11.1-slim

# Ruim — latest e base cheia
FROM node:latest
```

### Multi-stage builds

- Separe estágios de build e runtime — imagem final carrega só o necessário para rodar
- Nomeie estágios com `AS` para referenciar em `COPY --from=`
- Stage final deve ser mínimo — sem compiladores, sem dev dependencies

```dockerfile
FROM node:20.11.1-slim AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20.11.1-slim AS runtime
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./
USER node
CMD ["node", "dist/index.js"]
```

### Ordem de camadas e cache

- Instruções que mudam menos vão primeiro — cache é invalidado em cascata
- Copie manifestos de dependência antes do código-fonte, instale, depois copie o resto
- Agrupe comandos `RUN` relacionados com `&&` para reduzir camadas, sem sacrificar legibilidade

```dockerfile
# Bom — manifestos antes do código
COPY package*.json ./
RUN npm ci
COPY . .

# Ruim — qualquer mudança de código reinstala dependências
COPY . .
RUN npm ci
```

### .dockerignore

- Sempre criar `.dockerignore` — arquivos desnecessários em build context degradam performance e podem vazar secrets
- Incluir: `.git`, `node_modules`, `.env*`, `*.log`, diretórios de IDE, artefatos de build local

```
.git
.gitignore
node_modules
npm-debug.log*
.env
.env.*
!.env.example
.vscode
.idea
dist
build
coverage
*.md
```

### Non-root user

- Nunca rode como `root` em runtime — crie um usuário dedicado ou use o do runtime oficial (ex.: `USER node`)
- Ajuste ownership antes de mudar para non-root

```dockerfile
RUN addgroup --system --gid 1001 app && \
    adduser --system --uid 1001 --ingroup app app
COPY --chown=app:app . .
USER app
```

### HEALTHCHECK

- Defina `HEALTHCHECK` para imagens de serviço — orquestradores usam para rotear tráfego
- Intervalos conservadores (30s–60s) para não pressionar o app

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD curl -fsS http://localhost:3000/health || exit 1
```

### Secrets em build

- Nunca use `ARG` ou `ENV` para secrets — ficam gravados nas camadas
- Use BuildKit secrets com `--mount=type=secret`
- Variáveis de runtime (senhas de banco, tokens) passam via `docker run -e` ou gerenciador de secrets, nunca via Dockerfile

```dockerfile
# syntax=docker/dockerfile:1.7
RUN --mount=type=secret,id=npm_token \
    NPM_TOKEN=$(cat /run/secrets/npm_token) npm ci
```

### Labels (OCI annotations)

- Adicione labels OCI para rastreabilidade — úteis em registries e scanners
- Passe via `ARG` para não fixar valores no Dockerfile

```dockerfile
ARG VERSION=dev
ARG COMMIT_SHA=unknown
LABEL org.opencontainers.image.source="https://github.com/org/repo" \
      org.opencontainers.image.version="${VERSION}" \
      org.opencontainers.image.revision="${COMMIT_SHA}" \
      org.opencontainers.image.licenses="MIT"
```

### ENTRYPOINT vs CMD

- `ENTRYPOINT` para o binário principal — não deve ser sobrescrito casualmente
- `CMD` para argumentos default — fáceis de sobrescrever em `docker run`
- Use forma exec (`["cmd", "arg"]`), não forma shell — garante que sinais (SIGTERM) cheguem ao processo

```dockerfile
ENTRYPOINT ["node"]
CMD ["dist/index.js"]
```

### Tamanho de imagem

- Instale só o necessário — evite ferramentas de debug em runtime
- Limpe cache de package managers na mesma camada em que instalou
- `--no-install-recommends` em apt, `--no-cache` em apk
- Verifique tamanho com `docker images` e `dive` antes de publicar

```dockerfile
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*
```

---

## Parte 2 — docker-compose

### Estrutura base

- Use `compose.yaml` como nome padrão (Compose V2) — `docker-compose.yml` ainda funciona mas é legado
- Não declare `version:` — obsoleto no Compose V2
- Organize em blocos: `services`, `networks`, `volumes`, `configs`, `secrets`

```yaml
services:
  api:
    build: .
    ports:
      - "3000:3000"
    environment:
      DATABASE_URL: postgres://postgres:postgres@db:5432/app
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16.2-alpine
    volumes:
      - db-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      retries: 10

volumes:
  db-data:
```

### depends_on com healthcheck

- `depends_on` simples apenas espera o container iniciar — não espera o serviço estar pronto
- Use `condition: service_healthy` para aguardar o healthcheck passar
- Todo serviço com dependências deve ter healthcheck declarado

### Healthchecks em serviços

- Healthcheck local (sem depender de rede externa) — `pg_isready`, `curl localhost`, `redis-cli ping`
- `start_period` suficiente para o serviço subir antes da primeira checagem começar a contar como falha

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 3s
  retries: 10
  start_period: 10s
```

### profiles

- Use `profiles` para serviços opcionais (observability, seeders, ferramentas de dev) que não devem subir por padrão
- Ative com `docker compose --profile <name> up`

```yaml
services:
  app:
    image: myapp

  grafana:
    image: grafana/grafana
    profiles: ["observability"]
```

### Variáveis de ambiente

- `.env` na raiz é lido automaticamente — commitar `.env.example`, nunca `.env`
- Use interpolação `${VAR}` com default `${VAR:-default}` e obrigatório `${VAR:?mensagem}`
- Arquivos específicos por serviço via `env_file:`

```yaml
services:
  api:
    env_file:
      - .env.local
    environment:
      NODE_ENV: ${NODE_ENV:-development}
      DATABASE_URL: ${DATABASE_URL:?precisa estar definida}
```

### Volumes

- Named volumes para dados persistentes (bancos, filas) — `docker compose down` preserva por padrão
- Bind mounts para código em dev (hot reload) — não use em produção
- `:ro` para volumes que devem ser read-only

```yaml
services:
  api:
    volumes:
      - ./src:/app/src          # bind mount — hot reload em dev
      - /app/node_modules       # evita sobrescrever node_modules do container
      - configs:/app/configs:ro # named volume read-only
```

### Override pattern

- `compose.yaml` é o arquivo base — descreve o cenário comum
- `compose.override.yaml` é lido automaticamente e sobrescreve para dev (ports expostos, volumes bind, debug)
- `compose.prod.yaml` para produção, ativado com `-f compose.yaml -f compose.prod.yaml`

```yaml
# compose.yaml
services:
  api:
    image: myapp:${TAG:-latest}

# compose.override.yaml
services:
  api:
    build: .
    volumes:
      - ./src:/app/src
    ports:
      - "9229:9229"  # debug port
```

---

## Anti-patterns

- `FROM <imagem>:latest` — imprevisibilidade, builds não reprodutíveis
- `COPY . .` antes dos manifestos de dependência — invalida cache a cada commit
- `RUN apt-get install` sem `rm -rf /var/lib/apt/lists/*` — infla layer
- Secrets em `ARG` ou `ENV` — gravados na história da imagem
- Rodar como root em runtime
- Healthcheck externo (curl para outro serviço) — falha em cascata durante incidentes
- `depends_on` sem `condition: service_healthy` quando há ordem real de inicialização
- `compose.yaml` com `version:` — obsoleto, gera warning
- Bind mount de `node_modules`/`.venv` do host para dentro do container — arquitetura do host pode diferir
