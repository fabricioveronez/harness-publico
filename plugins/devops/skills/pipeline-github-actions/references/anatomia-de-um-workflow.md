# Anatomia de um workflow

> **Quando ler:** ao escrever seu primeiro workflow, quando você herda um workflow e não sabe o que cada parte faz, quando o workflow "subiu" mas não rodou e você não entende por quê, quando precisa entender contexto/expressões/outputs.

## Índice

1. [O modelo mental: workflow, job, step, runner](#o-modelo-mental-workflow-job-step-runner)
2. [Anatomia comentada de um workflow CI](#anatomia-comentada-de-um-workflow-ci)
3. [Eventos: o que faz um workflow disparar](#eventos-o-que-faz-um-workflow-disparar)
4. [Contexto e expressões: `${{ ... }}` decifrado](#contexto-e-expressões-----decifrado)
5. [Jobs paralelos vs sequenciais com `needs`](#jobs-paralelos-vs-sequenciais-com-needs)
6. [Outputs entre jobs](#outputs-entre-jobs)
7. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## O modelo mental: workflow, job, step, runner

Quatro conceitos que confundem iniciantes. Vamos separar.

### Workflow

Um arquivo YAML em `.github/workflows/`. Descreve **um pipeline completo**.

```
.github/
└── workflows/
    ├── ci.yml          ← um workflow
    ├── release.yml     ← outro workflow
    └── nightly.yml     ← outro
```

Cada arquivo é independente. Você pode ter 1 ou 50 workflows num repo. Convenção: arquivo por propósito (CI, release, scheduled jobs separados, deploy a staging, deploy a prod).

### Job

Um workflow tem um ou mais **jobs**. Cada job:

- Roda em um **runner** (máquina virtual fresca, Linux ou Windows ou macOS)
- É **isolado** dos outros jobs (filesystem, processos)
- Por padrão, **roda em paralelo** com outros jobs do mesmo workflow

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    # ...
  
  lint:
    runs-on: ubuntu-latest
    # ...
```

`test` e `lint` rodam em runners diferentes, ao mesmo tempo, sem comunicação direta.

### Step

Um job tem **steps**. Cada step:

- É um comando shell (`run:`) ou uso de uma action (`uses:`)
- Roda **sequencialmente** (em ordem) **no mesmo runner**
- Compartilha filesystem com outros steps do mesmo job

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4    # step 1: clona repo
      - uses: actions/setup-node@v4   # step 2: instala node
        with:
          node-version: "20"
      - run: npm ci                    # step 3: instala deps
      - run: npm test                  # step 4: roda testes
```

Os steps rodam um após o outro, no mesmo runner, no mesmo diretório.

### Runner

A máquina virtual onde o job roda. GitHub oferece runners gerenciados:

- `ubuntu-latest` (Ubuntu 22.04 ou similar)
- `windows-latest`
- `macos-latest`

Você também pode usar **self-hosted runners** (sua própria máquina/cluster), útil para acessar recursos internos ou ter hardware específico.

Cada job ganha runner novo. Quando o job termina, runner é descartado. Estado não persiste entre jobs do mesmo workflow.

### O diagrama mental

```
Workflow (ci.yml)
│
├── Job "test" ───────────────► Runner A (Ubuntu novo)
│   ├── Step: checkout
│   ├── Step: setup-node
│   ├── Step: npm ci
│   └── Step: npm test
│
├── Job "lint" ───────────────► Runner B (Ubuntu novo, paralelo a A)
│   ├── Step: checkout
│   └── Step: lint
│
└── Job "build" (needs: [test, lint]) ───► Runner C (espera A e B)
    ├── Step: checkout
    └── Step: npm run build
```

## Anatomia comentada de um workflow CI

```yaml
name: CI
```

Nome amigável que aparece na aba "Actions" do GitHub. Pode ter espaços, emojis (se quiser). Se omitir, GitHub usa o nome do arquivo.

```yaml
on:
  push:
    branches: [main]
  pull_request:
```

**Triggers** — eventos que disparam o workflow. Veja seção dedicada. Aqui: roda em push para main e em qualquer pull request.

```yaml
permissions:
  contents: read
```

**Permissões do `GITHUB_TOKEN`**. Por default, GitHub dá um conjunto amplo. Restringir é boas práticas — workflow que só roda testes não precisa escrever em nada. Veja `references/seguranca-em-pipelines.md`.

```yaml
concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

**Concurrency control** — evita workflows simultâneos para o mesmo PR/branch. Veja `references/performance-e-reuso.md`.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
```

Início do job `test`. `ubuntu-latest` indica o runner.

```yaml
    steps:
      - uses: actions/checkout@v4
```

**Action** `actions/checkout@v4`. Clona o repo no runner. Por default, faz checkout do commit que disparou o workflow.

`@v4` é uma **tag** — apontador para um commit. Mais sobre pinning em `references/seguranca-em-pipelines.md`.

```yaml
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
```

Action `setup-node`. Instala Node.js 20 e configura cache automático para `npm`.

`with:` passa parâmetros para a action — nomes e tipos definidos pela própria action.

```yaml
      - run: npm ci
```

Step `run` — comando shell. Executa `npm ci` no runner.

```yaml
      - run: npm test
        env:
          NODE_ENV: test
```

Outro `run`, com variável de ambiente injetada via `env:` (escopo do step).

`env:` também pode ser declarado a nível de job ou workflow (escopo maior).

### Outras coisas que podem aparecer

```yaml
      - name: Build artifacts
        run: |
          npm run build
          tar czf dist.tar.gz dist/
```

`name:` é label legível (aparece nos logs). `|` permite multi-line shell.

```yaml
      - if: failure()
        run: cat error.log
```

`if:` controla condicionalmente. `failure()` é função built-in que retorna true se algum step anterior falhou.

```yaml
      - id: meta
        run: echo "tag=v$(date +%s)" >> $GITHUB_OUTPUT
```

`id:` permite outras steps referenciarem este. `$GITHUB_OUTPUT` é um arquivo especial — escrever `name=value` lá expõe como output do step.

## Eventos: o que faz um workflow disparar

GitHub Actions suporta dezenas de eventos. Os que você usa 90% do tempo:

### `push`

Dispara quando alguém faz push.

```yaml
on:
  push:
    branches: [main, develop]
    paths-ignore: ["**.md", "docs/**"]
    tags: ["v*"]
```

- `branches:` — só push nessas branches dispara
- `paths-ignore:` — ignora pushes que **só** mudam esses paths (CI roda? não)
- `tags: ["v*"]` — também dispara quando tag é criada com nome começando em `v`

### `pull_request`

Dispara quando PR é aberto/atualizado/sincronizado.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]
```

Por default, `types` inclui esses três. Sincroniza = novo push no PR.

**Importante:** workflows em PRs vindo de **forks** rodam em contexto restrito — sem acesso a secrets, com `GITHUB_TOKEN` apenas read-only. Isso é por segurança (PR de fork pode ter código malicioso).

### `workflow_dispatch`

Permite disparar manualmente pela UI do GitHub.

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: 'Ambiente para deploy'
        required: true
        type: choice
        options: [staging, prod]
      version:
        description: 'Versão a deployar'
        required: true
        type: string
```

UI do GitHub mostra formulário para preencher os inputs. Útil para deploys manuais com gate humano.

### `schedule`

Roda em cron schedule.

```yaml
on:
  schedule:
    - cron: "0 3 * * *"   # 3h UTC todo dia
    - cron: "0 9 * * 1"   # 9h UTC toda segunda
```

**Importante:** schedule usa UTC. Esquecer disso e marcar "9h" pensando no horário local é erro comum.

Schedules em repos sem atividade nas últimas 60 dias ficam pausados — GitHub não roda. Faça push em algum branch para reativar.

### `workflow_call`

Outro workflow chama este — usado para reusable workflows. Veja `references/performance-e-reuso.md`.

### `pull_request_target` (cuidado!)

Variante perigosa de `pull_request`. Roda no contexto do **repo base** (com secrets), mas pode receber código de fork. Risco de RCE. Veja `references/seguranca-em-pipelines.md`.

### Múltiplos eventos

Pode combinar:

```yaml
on:
  push:
    branches: [main]
  pull_request:
  schedule:
    - cron: "0 3 * * *"
  workflow_dispatch:
```

Mesmo workflow dispara em qualquer um.

## Contexto e expressões: `${{ ... }}` decifrado

`${{ ... }}` é a sintaxe de **expressões** do GitHub Actions. Permite acessar contexto e fazer operações.

### Contextos disponíveis

| Contexto | O que tem |
|---|---|
| `github` | Info do evento (sha, ref, actor, event_name, repository) |
| `env` | Variáveis de ambiente |
| `secrets` | Secrets do repo/org/environment |
| `vars` | Variáveis do repo/org (não-secret) |
| `runner` | Info do runner (os, arch, temp) |
| `steps` | Outputs de steps anteriores no mesmo job |
| `needs` | Outputs de jobs dependentes |
| `inputs` | Inputs de workflow_dispatch ou workflow_call |
| `matrix` | Valor atual de matrix strategy |

### Casos comuns

```yaml
# Branch atual
${{ github.ref }}                    # refs/heads/main, refs/pull/42/merge
${{ github.ref_name }}               # main (limpo)

# Quem disparou
${{ github.actor }}                  # username

# SHA do commit
${{ github.sha }}                    # abc123def...

# Tipo de evento
${{ github.event_name }}             # push, pull_request, etc

# Acessar secret
${{ secrets.NPM_TOKEN }}

# Output de step anterior
${{ steps.meta.outputs.tag }}

# Output de job anterior
${{ needs.build.outputs.image_tag }}
```

### Expressões com lógica

```yaml
# Boolean
if: github.ref == 'refs/heads/main'
if: github.event_name == 'pull_request'
if: ${{ !cancelled() }}

# Combinação
if: github.ref == 'refs/heads/main' && github.event_name == 'push'

# Funções built-in
${{ contains(github.event.head_commit.message, '[skip ci]') }}
${{ startsWith(github.ref, 'refs/tags/') }}
${{ format('v{0}.{1}', steps.major.outputs.value, steps.minor.outputs.value) }}
${{ toJSON(github.event) }}
${{ fromJSON(steps.api.outputs.response).data }}
```

### Funções de status (úteis em `if:`)

| Função | Quando usar |
|---|---|
| `success()` | Step anterior passou (default em steps; explícito em jobs) |
| `failure()` | Algum step anterior falhou — útil para cleanup, notificação |
| `always()` | Sempre roda — útil para upload de logs (mas cuidado com deploy) |
| `cancelled()` | Workflow foi cancelado |

```yaml
- name: Upload logs
  if: always()                # mesmo se falhar
  uses: actions/upload-artifact@v4
  with:
    name: logs
    path: logs/
```

### Pegadinha: `${{ }}` em `run`

Em strings simples, expressões funcionam. Em `run`, cuidado com **shell injection**:

```yaml
# RUIM — usuário pode injetar shell command via título do PR
- run: echo "Title: ${{ github.event.pull_request.title }}"
```

Se alguém abre PR com título `"; rm -rf $HOME; "`, o shell tenta executar.

```yaml
# SEGURO — usar variável de ambiente
- run: echo "Title: $TITLE"
  env:
    TITLE: ${{ github.event.pull_request.title }}
```

A diferença: `${{ }}` é interpolado pelo GitHub **antes** do shell ver. Variável de ambiente passa o valor sem interpretar como código.

## Jobs paralelos vs sequenciais com `needs`

Por default, jobs do mesmo workflow rodam **em paralelo** — cada um em seu runner.

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]
  
  test:
    runs-on: ubuntu-latest
    steps: [...]
  
  build:
    runs-on: ubuntu-latest
    steps: [...]
```

Os três sobem ao mesmo tempo. Total: tempo do mais demorado.

### Quando você precisa de ordem

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]
  
  test:
    runs-on: ubuntu-latest
    steps: [...]
  
  build:
    needs: [lint, test]    # ← espera lint e test passarem
    runs-on: ubuntu-latest
    steps: [...]
```

`build` só começa quando `lint` E `test` terminam (e ambos com sucesso).

### Padrão típico de CI

```yaml
jobs:
  lint:        # rápido (~30s)
    # ...
  
  test:        # médio (~3min)
    # ...
  
  build:       # demorado (~5min)
    needs: [lint, test]
    # ...
  
  deploy:      # produção
    needs: build
    if: github.ref == 'refs/heads/main'
    # ...
```

Lint e test rodam paralelos — feedback rápido. Build espera os dois. Deploy só em main.

### Continuar mesmo se anteriores falharem

```yaml
jobs:
  notify:
    needs: [test]
    if: ${{ always() }}    # roda mesmo se test falhar
    # ...
```

Útil para notificações, cleanup, upload de artefatos de debug.

### Anti-pattern: serial sem necessidade

```yaml
jobs:
  step1:
    # ...
  step2:
    needs: step1
    # ...
  step3:
    needs: step2
    # ...
```

Se eles **não dependem** de fato (não compartilham artefato, não validam mesma coisa), você está pagando tempo serial sem motivo. CI lento desestimula CI.

## Outputs entre jobs

Jobs em runners separados não compartilham filesystem. Para passar dados:

### Outputs declarados

```yaml
jobs:
  version:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.meta.outputs.tag }}
    steps:
      - id: meta
        run: echo "tag=v$(date +%s)" >> $GITHUB_OUTPUT

  publish:
    needs: version
    runs-on: ubuntu-latest
    steps:
      - run: echo "Tagging as ${{ needs.version.outputs.tag }}"
```

Step `meta` escreve no `$GITHUB_OUTPUT`. Job `version` declara isso como output. Job `publish` consome via `needs.version.outputs.tag`.

### Anti-pattern: `::set-output::` (legado)

Antes existia `echo "::set-output name=foo::value"`. Foi descontinuado em 2022 por questões de segurança (injeção via valor). Use `>> $GITHUB_OUTPUT`.

### Artefatos para arquivos

Outputs são para strings curtas. Para arquivos:

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/
      - run: ls dist/
```

Artefatos persistem entre jobs e ficam disponíveis no run para download manual também.

## Erros comuns de iniciante

### "Coloquei o workflow em `.github/workflow/` (sem 's') e não roda"

Diretório precisa ser exatamente `.github/workflows/` (plural). GitHub não avisa nada quando o diretório está errado.

### "Sintaxe de YAML quebrou"

Erros comuns:
- Indentação inconsistente (2 espaços vs 4)
- `tab` em vez de espaços
- `:` esquecido após `name`, `runs-on`
- String com `:` interno sem aspas

Use yamllint ou plugin do editor antes de commitar.

### "Workflow não roda mesmo no push para a branch certa"

Conferir:
- Arquivo está em `.github/workflows/*.yml` (não `.yaml.txt`, não outro lugar)
- Sintaxe YAML válida (vai aparecer erro na aba Actions)
- `on:` cobre o evento de fato (talvez você só fez merge sem push?)
- Branch tem o arquivo (você commitou em outra branch?)

### "Variáveis não passam entre steps"

Cada step roda em shell **diferente** (mesmo runner, processos separados). `export FOO=bar` em um step não persiste no próximo. Use:

```yaml
- run: echo "FOO=bar" >> $GITHUB_ENV
- run: echo "$FOO"   # funciona — $GITHUB_ENV é lido pelo runner
```

`$GITHUB_ENV` é arquivo especial que o runner lê entre steps.

### "Quero usar `${{ secrets.X }}` mas é `null`"

- Secret precisa existir no repo (Settings → Secrets and variables → Actions)
- Em PR de fork, secrets **não** estão disponíveis (proteção)
- Workflows em forks rodam com `GITHUB_TOKEN` read-only

### "Job rodou mas não fez nada"

Provavelmente todo step tinha `if:` que não atendeu. Use `name:` em cada step e leia os logs — vão mostrar "skipped" ou similar.

### "`pull_request` workflow rodou em fork mas não tem secrets"

Por design (proteção contra RCE). Para workflows que precisam de secrets em PR, considere:
- Mover para `pull_request_target` com cuidado (veja segurança)
- Pedir contributor mergiar via branch interna em vez de fork
- Mover lógica que precisa secret para job que roda só após merge em main

### "Cron schedule virou meio que aleatório, não rodou no horário certo"

GitHub schedules são "best effort" — durante alta carga, podem atrasar 5-10min. Schedule não é garantia de pontualidade. Para cron exato, use ferramenta externa.

---

**Princípio que resume tudo:** Workflow é uma máquina de estado disparada por evento. Workflow → jobs (paralelos, em runners separados) → steps (sequenciais, no mesmo runner). Contexto e expressões são "como o workflow vê o mundo". Bem desenhado, ele te dá feedback rápido e ações automáticas; mal desenhado, vira gargalo lento que ninguém entende.
