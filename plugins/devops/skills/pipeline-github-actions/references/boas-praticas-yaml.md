# Boas práticas de YAML do GitHub Actions

Guia prescritivo para escrever e revisar workflows. Aplique as convenções direto no código sem explicar cada decisão — o objetivo é consistência, segurança e performance. A seção **Lições de pipelines reais** (no fim) traz regras que vieram de pipelines que falharam na primeira execução; elas valem tanto quanto as demais.

## Quando aprofundar

Os guias ao lado (`references/`) aprofundam o "porquê" das práticas e cobrem casos do mundo real. Carregue sob demanda quando:

| Cenário | Reference |
|---|---|
| Escrevendo primeiro workflow, herdando workflow e não entendendo, decifrando `${{ ... }}`, debugando "não rodou" | `references/anatomia-de-um-workflow.md` |
| Antes de adicionar secret, escrevendo workflow em PR, deployando em cloud, alguém menciona OIDC/RCE | `references/seguranca-em-pipelines.md` |
| CI passou de 5min e dói, copiando 8 steps em 4 workflows, push novo no PR não cancela anterior | `references/performance-e-reuso.md` |

## Estrutura de workflow

Todo workflow tem pelo menos `name`, `on` e `jobs`. Organize na ordem: `name → on → permissions → concurrency → env → jobs`.

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
          cache: npm
      - run: npm ci
      - run: npm test
```

## Triggers

### Princípios

- Seja específico — `push` sem filtro roda em todo push, inclusive em branches temporárias
- Separe workflows por propósito (CI em PR, release em tag) em vez de um mega-workflow com lógica interna

### Triggers comuns

```yaml
on:
  push:
    branches: [main]
    paths-ignore: ["**.md", "docs/**"]

  pull_request:
    types: [opened, synchronize, reopened]

  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, prod]

  schedule:
    - cron: "0 3 * * *"  # diário às 3h UTC
```

### `pull_request` vs `pull_request_target`

- Use **`pull_request`** para CI normal — roda no contexto do fork, sem secrets
- **`pull_request_target` é perigoso** — roda no contexto do repo base com secrets disponíveis, mas pode executar código do fork. Risco de RCE
- Se precisar de `pull_request_target` (ex.: comentar em PR de fork), **nunca** faça checkout do código do fork no mesmo job

## Permissions

### Default restrito

- Declare `permissions:` no nível do workflow — o default do GitHub é amplo demais
- Comece com `permissions: contents: read` e adicione só o necessário
- Escopo por job quando possível — job que só testa não precisa escrever em `contents`

```yaml
permissions:
  contents: read

jobs:
  release:
    permissions:
      contents: write       # para criar release
      id-token: write       # para OIDC
    runs-on: ubuntu-latest
```

## Secrets e OIDC

### OIDC sobre credenciais long-lived

- Prefira OIDC para autenticar em clouds (AWS, GCP, Azure, HashiCorp Vault) — sem secrets long-lived armazenados
- OIDC requer `permissions: id-token: write` no job
- Configure trust relationship na cloud restringindo por `sub` (repo, branch, environment)

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123:role/gh-deploy
      aws-region: us-east-1
```

### Quando secrets long-lived são inevitáveis

- Use `environments` com required reviewers para secrets sensíveis
- Rotacione regularmente
- Nunca loga secrets — masking do GitHub não cobre transformações (base64, split)

## Jobs paralelos e `needs`

- Por default, jobs rodam em paralelo — use `needs:` apenas para dependências reais
- Separe lint/test/build em jobs distintos — feedback mais rápido e logs mais claros

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    runs-on: ubuntu-latest
    steps: [...]

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps: [...]
```

## Matrix strategy

- Use matrix para rodar o mesmo job em múltiplas configurações (versões, OSes)
- `fail-fast: false` quando cada combinação é informativa — evita abortar todas ao primeiro fail
- `include` e `exclude` para combinações específicas

```yaml
strategy:
  fail-fast: false
  matrix:
    node: ["18", "20", "22"]
    os: [ubuntu-latest, windows-latest]
    exclude:
      - os: windows-latest
        node: "18"
```

## Cache

### Use setup actions com cache embutido

- `actions/setup-node@v4` com `cache: npm` já gerencia cache do package manager
- `actions/setup-go@v5`, `actions/setup-python@v5`, `actions/setup-java@v4` — idem

### `actions/cache` para cache manual

- Chave do cache deve incluir hash dos arquivos de lock — `key: ${{ runner.os }}-deps-${{ hashFiles('**/package-lock.json') }}`
- `restore-keys:` com prefixos para hits parciais

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

## Concurrency

- PRs: cancele runs antigos ao fazer novo push (`cancel-in-progress: true`)
- `main`: nunca cancele — garante que todo commit tem um run completo
- Diferencie por `github.ref` no `group`

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

## Reusable workflows

- Extraia workflows compartilhados (test suite comum, deploy pipeline) em `.github/workflows/*.yml` com `on: workflow_call`
- Declare `inputs` e `secrets` explicitamente
- Versione via tag/SHA ao chamar de outro repo

```yaml
# .github/workflows/deploy.yml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true

# Uso
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

## Composite actions

- Extraia sequências de steps repetidas em composite action (`.github/actions/<name>/action.yml`)
- Mais leve que reusable workflow — não cria novo job
- Útil para setup comum (checkout + setup + login)

```yaml
# .github/actions/setup-node-project/action.yml
name: Setup Node Project
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: "20"
        cache: npm
    - run: npm ci
      shell: bash
```

## Pinning de actions

### Produção: pin por SHA

- Tags (`@v4`) são mutáveis — mantenedor pode mover para um commit diferente, inclusive malicioso
- Para workflows sensíveis (deploy, release), pin por SHA completo do commit
- Use Dependabot ou Renovate para manter atualizado

```yaml
# Seguro — SHA imutável
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11  # v4.1.1

# Comum — aceitável para CI básico em actions oficiais
- uses: actions/checkout@v4
```

### Actions de terceiros

- Prefira actions oficiais de organizações reconhecidas
- Actions de terceiros: sempre pin por SHA

## Conditional steps

- `if:` para executar condicionalmente — usa a sintaxe de expressões do GitHub
- Centralize condicionais em steps ou jobs, não em cada comando shell

```yaml
- name: Deploy to prod
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  run: ./deploy.sh prod
```

## Outputs entre jobs

- Declare `outputs:` no job produtor, referencie via `needs.<job>.outputs.<name>` no consumidor
- No step, use `echo "name=value" >> $GITHUB_OUTPUT` — nunca o legado `::set-output::`

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

## Environments

- Use `environments` do GitHub para separar staging/prod com proteções
- Required reviewers + wait timer + deployment branches

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://api.example.com
    steps: [...]
```

## Anti-patterns

- `pull_request_target` com checkout do código do PR no mesmo job — RCE em fork
- Secrets em logs (`echo ${{ secrets.TOKEN }}`) ou em outputs de jobs
- `actions/checkout@master` ou qualquer tag flutuante em workflows sensíveis
- `permissions:` ausente — workflow herda permissões amplas do repo
- `if: always()` em step de deploy — deploya mesmo quando testes falham
- Um mega-workflow com 500 linhas em vez de dividir em jobs/reusable workflows
- Matrix sem `fail-fast: false` quando combinações são independentes — perde informação diagnóstica
- Cache key sem hash de lock file — cache nunca invalida, build pega artefatos antigos
- Long-lived cloud credentials em secrets quando OIDC é suportado
- `concurrency` sem `github.ref` no group — cancelamento cross-PR

## Lições de pipelines reais

Regras que nasceram de pipelines que só falharam quando rodaram de verdade. Cada uma custou pelo menos um run.

### Todo workflow que muda estado tem caminho de retry

Workflow de apply/deploy disparado só por `push` + `paths` não pode ser reprocessado depois de uma falha externa (secret corrigido, recurso cadastrado na cloud) sem um commit artificial. Inclua `workflow_dispatch` **e** faça o `if:` dos jobs aceitar o evento — senão o botão "Run workflow" dispara um run sem nenhum job.

```yaml
on:
  push:
    branches: [main]
    paths: ["terraform/**", "ansible/**", ".github/workflows/provisionamento.yml"]
  pull_request:
    paths: ["terraform/**", "ansible/**", ".github/workflows/provisionamento.yml"]
  workflow_dispatch:

jobs:
  apply:
    if: github.ref == 'refs/heads/main' && (github.event_name == 'push' || github.event_name == 'workflow_dispatch')
```

### `paths` inclui o próprio workflow

Sem isso, uma correção feita só no YAML do workflow não dispara o workflow corrigido.

### Não conte com o primeiro push para disparar

Num repositório recém-criado, o primeiro `git push` com workflow filtrado por `paths` já foi observado sem gerar run nenhum. Planeje o primeiro disparo via `gh workflow run` e confirme com `gh run list` — não espere o push.

### Gates do PR não protegem o que roda fora do PR

Jobs com `if: github.event_name == 'pull_request'` (plan, lint, validate) ficam `skipped` em push/dispatch. Se o apply na main pode rodar sem ter passado por PR (dispatch, push direto), ele precisa repetir os gates baratos (`fmt -check`, `validate`, lint) ou depender deles via `needs:`.

### Nada de placeholder de configuração externa

Nome de organização/workspace do backend remoto, nome de chave SSH no provedor, nome de repositório no registry: se o valor foi suposto e não confirmado, marque com comentário `# CONFIRMAR:` e liste no relatório de preflight. Um placeholder plausível (`organization = "minha-org"`) passa em `terraform validate` e só falha no init remoto.

### Concurrency compartilhada entre workflows

Dois workflows no mesmo `concurrency.group` (ex.: provisionamento e deploy no mesmo ambiente) formam uma fila de **um** pendente: um terceiro run cancela o pendente anterior. Aceitável, mas documente no workflow.

### Firewall temporário para o runner

Quando o runner precisa alcançar uma porta fechada (SSH, API do Kubernetes), abra só para o IP do runner (/32), remova regras órfãs antes, mascare o IP (`::add-mask::`) e feche num step com `if: always()`.

### Teste que parseia o YAML prova estrutura, não execução

Teste unitário que lê o workflow com uma lib YAML confirma gatilhos e `needs`, mas não pega uid de container, firewall, permissão de banco ou credencial errada. Só um run real (PR antes do merge) valida execução.
