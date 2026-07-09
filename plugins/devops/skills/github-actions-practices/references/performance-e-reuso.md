# Performance e reuso

> **Quando ler:** quando seu CI passa de 5min e dói a cada commit, quando você está copiando os mesmos 8 steps em 4 workflows, quando push novo no PR não cancela o anterior, quando você precisa rodar o mesmo teste em múltiplas versões/OSes.

## Índice

1. [Por que CI rápido importa](#por-que-ci-rápido-importa)
2. [Cache: o ganho número 1](#cache-o-ganho-número-1)
3. [Concurrency: cancelar runs antigos sem matar produção](#concurrency-cancelar-runs-antigos-sem-matar-produção)
4. [Matrix strategy: testar em N variações](#matrix-strategy-testar-em-n-variações)
5. [Reusable workflows: copiar 8 steps nunca mais](#reusable-workflows-copiar-8-steps-nunca-mais)
6. [Composite actions: leve, sem novo job](#composite-actions-leve-sem-novo-job)
7. [Quando usar cada um: reusable workflow vs composite action](#quando-usar-cada-um-reusable-workflow-vs-composite-action)
8. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## Por que CI rápido importa

CI lento desestimula CI. Quando o pipeline demora 25 minutos:

- Devs fazem `--no-verify` para pular hooks locais
- PR fica aberto esperando teste, contexto se perde
- Code review é feito sem ver resultado de teste
- Quando algo quebra, demora muito até feedback
- Confiança no CI cai — "ah, deve ser flaky"

CI de 3-5 minutos para PR é alvo razoável. Acima de 10, vire prioridade. Acima de 20, é problema sério.

## Cache: o ganho número 1

A maior parte do tempo de CI é gasta:
1. Baixando dependências (`npm ci`, `pip install`, `cargo build`)
2. Compilando código

Ambos são repetitivos — mesmas dependências, mesmas compilações entre runs. Cache acelera drasticamente.

### Setup actions com cache embutido

Para a maioria das linguagens, use a action de setup oficial com cache:

```yaml
- uses: actions/setup-node@v4
  with:
    node-version: "20"
    cache: npm                     # cache automático para npm
    cache-dependency-path: package-lock.json
```

Isso já cuida do cache. Roda `npm ci` só baixa o que mudou. Em projetos típicos: 2min → 20s.

Equivalente para outras linguagens:

| Action | Linguagem | Caches |
|---|---|---|
| `actions/setup-node@v4` | Node | `npm`, `yarn`, `pnpm` |
| `actions/setup-python@v5` | Python | `pip`, `pipenv`, `poetry` |
| `actions/setup-go@v5` | Go | módulos + build cache |
| `actions/setup-java@v4` | Java | Maven, Gradle, sbt |
| `actions/setup-dotnet@v4` | .NET | NuGet (precisa configurar) |

### `actions/cache` para casos custom

Quando setup oficial não cobre seu cenário (cargo, custom build artifacts):

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.cargo
    key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
    restore-keys: |
      ${{ runner.os }}-cargo-
```

Anatomia da chave:

- `${{ runner.os }}` — não mistura cache de Linux com macOS
- `cargo` — namespace para evitar colisão com outros caches
- `${{ hashFiles('**/Cargo.lock') }}` — hash do lock file. **Quando lock muda, chave muda, cache é "perdido"** — força refresh.

### `restore-keys`: hits parciais

`key:` deve bater **exatamente** para hit total. Se Cargo.lock muda, key muda, sem hit.

`restore-keys:` é fallback prefix:

```yaml
key: linux-cargo-abc123
restore-keys: |
  linux-cargo-
```

Se key exata não existe, GitHub procura algum cache começando com `linux-cargo-` — pega o mais recente. Você economiza com cache parcial e atualiza incrementalmente.

### O que NÃO cachear

- `node_modules` direto — pode conter binários compilados para arch específica que não combine com runner
- Diretórios mutáveis (`/tmp`, `~/.cache` genérico) — invalidação imprevisível
- Build artifacts pequenos — overhead de cache > benefício

### Limite de 10 GB

Cada repo tem limite de 10 GB de cache (compartilhado entre todos os caches). Quando cheio, GitHub elimina os menos usados. Se seus caches passam de 10 GB, considere granularidade menor.

### Ganho típico

Workflow com setup-node@cache + restore-keys configurado:

| Cenário | Sem cache | Com cache |
|---|---|---|
| Build full após mudança de lock | 4 min | 4 min |
| Build após mudança só de código | 4 min | **30s** |
| Build após nenhuma mudança | 4 min | 30s |

Em CI rodando 50x por dia, são horas economizadas.

## Concurrency: cancelar runs antigos sem matar produção

Cenário: você abre PR. CI roda. Você faz mais 3 commits no mesmo PR rapidinho. Sem concurrency, **4 runs rodam em paralelo**, gastando minutos de runner por nada — só o último importa.

### Solução básica

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

`group:` define o "balde" — runs com mesmo group são gerenciados juntos. Aqui: por workflow + branch.

`cancel-in-progress: true` — quando novo run começa, cancela os antigos do mesmo group.

Resultado: você empurra commits, só o último termina. Os anteriores são abortados.

### O perigo: cancelar deploy em produção

```yaml
on:
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true     # ❌ — cancela deploy em produção!
```

Cenário ruim:
1. Push em main dispara deploy em produção.
2. Deploy começa (puxa imagem, atualiza serviço).
3. Outro push em main dispara workflow.
4. Cancela o deploy no meio. Estado intermediário em produção.

### Solução: cancelar só em PR

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}
```

Em PR cancela; em push para main, não. Push em main fica em fila — segundo run começa quando primeiro terminar.

### Concurrency por job

Para casos específicos (ex: deploy), pode declarar no job:

```yaml
jobs:
  deploy:
    concurrency:
      group: production-deploy
      cancel-in-progress: false    # nunca cancela; sempre fila
    runs-on: ubuntu-latest
    # ...
```

Mesmo com push em main rapidamente, deploys vão na fila um após o outro — nunca em paralelo.

### Padrão recomendado

```yaml
# Workflow CI normal (test, lint, build)
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

# Workflow de deploy
concurrency:
  group: deploy-${{ github.event.inputs.environment || 'production' }}
  cancel-in-progress: false
```

CI cancela em PR. Deploy nunca cancela.

## Matrix strategy: testar em N variações

Quando o mesmo teste precisa rodar em múltiplas versões, OSes, configurações:

```yaml
jobs:
  test:
    strategy:
      matrix:
        node: ["18", "20", "22"]
        os: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
      - run: npm ci
      - run: npm test
```

Roda 3 × 3 = 9 jobs em paralelo. Cada combinação independente.

### `fail-fast` — abortar tudo no primeiro fail?

Por default, GitHub aborta todos os jobs da matrix quando um falha (`fail-fast: true`). Útil para feedback rápido.

Mas se cada combinação é informativa, você quer ver tudo:

```yaml
strategy:
  fail-fast: false   # mesmo se um falhar, continua os outros
  matrix:
    node: ["18", "20", "22"]
```

Trade-off: mais runner usage, mais info.

### `include` e `exclude` para combinações cirúrgicas

```yaml
strategy:
  matrix:
    node: ["18", "20", "22"]
    os: [ubuntu-latest, windows-latest]
    exclude:
      - os: windows-latest
        node: "18"        # node 18 + windows não testa
    include:
      - os: macos-latest
        node: "20"        # adiciona um único job extra
```

`exclude` remove combinações específicas (ex: combinação que não funciona ou não importa).
`include` adiciona combinações que não fazem parte do produto cartesiano.

### Limite de 256 jobs

Matrix tem limite de 256 jobs por run. Se você tiver `5 versões × 3 OSes × 5 databases × 4 caches = 300`, vai falhar. Reduza ou separe em workflows.

### Quando NÃO usar matrix

- Combinações que não são realmente "mesmo teste em variantes" (use jobs separados)
- Quando você só rodaria as variantes em scheduled job, não em todo PR (separe — não polui PR com 20 jobs)

### Padrão útil: matrix para nightly

```yaml
on:
  pull_request:
  schedule:
    - cron: "0 3 * * *"

jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        # PRs testam só em ubuntu+latest
        # Nightly testa matriz completa
        node: ${{ github.event_name == 'schedule' && fromJSON('["18","20","22"]') || fromJSON('["20"]') }}
        os: ${{ github.event_name == 'schedule' && fromJSON('["ubuntu-latest","windows-latest","macos-latest"]') || fromJSON('["ubuntu-latest"]') }}
    runs-on: ${{ matrix.os }}
    steps: [...]
```

PR roda 1 job (rápido). Nightly roda 9. Você tem coverage sem castigar PRs.

## Reusable workflows: copiar 8 steps nunca mais

Cenário: 5 microsserviços no mesmo repo (monorepo). Cada um tem workflow CI quase idêntico — checkout, setup-node, npm ci, lint, test, build. 8 steps × 5 = 40 steps duplicados. Mudar um significa atualizar em 5 lugares.

**Reusable workflow** resolve.

### Definindo

```yaml
# .github/workflows/node-ci.yml
name: Node CI Reusable

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: "20"
      working-directory:
        type: string
        required: true
    secrets:
      NPM_TOKEN:
        required: false

jobs:
  ci:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ${{ inputs.working-directory }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
        env:
          NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
      - run: npm run lint
      - run: npm test
      - run: npm run build
```

`on: workflow_call` é o trigger especial — esse workflow só roda quando outro chama.

### Consumindo

```yaml
# .github/workflows/services-ci.yml
name: Services CI

on: pull_request

jobs:
  api-ci:
    uses: ./.github/workflows/node-ci.yml      # caminho relativo
    with:
      working-directory: services/api
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

  worker-ci:
    uses: ./.github/workflows/node-ci.yml
    with:
      working-directory: services/worker
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}

  scheduler-ci:
    uses: ./.github/workflows/node-ci.yml
    with:
      working-directory: services/scheduler
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Mudar a sequência de steps = mudar em 1 lugar.

### Reusable workflow entre repos

```yaml
jobs:
  ci:
    uses: myorg/shared-workflows/.github/workflows/node-ci.yml@v1.2.0
    with:
      working-directory: .
```

Permite organização inteira compartilhar workflows. Versionado por tag/SHA.

### Limites importantes

- Reusable workflow é **um job inteiro** — não pode ser usado como step
- Tem que ter pelo menos um job
- Pode ter múltiplos jobs, mas todos rodam quando chamado
- Aninhamento: máximo 4 níveis de chamada
- 20 chamadas no máximo por workflow

## Composite actions: leve, sem novo job

Quando você tem **uma sequência de steps** que se repete, mas dentro do mesmo job — composite action é mais leve que reusable workflow.

### Definindo

```yaml
# .github/actions/setup-node-project/action.yml
name: Setup Node Project
description: Checkout, install Node, install deps, with caching

inputs:
  node-version:
    description: Node version
    required: false
    default: "20"

runs:
  using: composite
  steps:
    - uses: actions/setup-node@v4
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm

    - run: npm ci
      shell: bash      # ESSENCIAL — composite actions exigem shell explícito
```

### Usando

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-node-project   # caminho relativo
        with:
          node-version: "20"
      - run: npm test                                 # depois do setup
```

Composite action vira "um step" do ponto de vista do workflow consumidor — mas internamente são vários steps.

### Vantagens sobre reusable workflow

- **Roda no mesmo runner** — sem overhead de iniciar runner novo
- **Compartilha filesystem** com outros steps do job — pode preceder e suceder steps específicos do consumidor
- **Mais leve** — útil para "5 steps comuns que sempre vêm juntos"

## Quando usar cada um: reusable workflow vs composite action

| Aspecto | Reusable workflow | Composite action |
|---|---|---|
| **Granularidade** | Job inteiro (várias steps, talvez vários jobs) | Sequência de steps |
| **Runner** | Novo runner por chamada | Mesmo runner do consumidor |
| **Compartilha files com consumidor?** | Não | Sim |
| **Consumido como** | `uses:` em job | `uses:` em step |
| **Pode ter múltiplos jobs?** | Sim | Não |
| **Pode ter `runs-on:` próprio?** | Sim | Não — herda do consumidor |

### Heurística

- "Os 3 microsserviços fazem CI praticamente igual" → **reusable workflow**
- "Todo workflow de Node começa com 4 steps idênticos antes do que é específico" → **composite action**
- "Quero rodar deploy completo (build + push + apply)" → **reusable workflow**
- "Quero passo de 'login no registry e build da imagem'" → **composite action**

### Combinar os dois

Frequentemente faz sentido:

```yaml
# Composite action: setup-base
# Reusable workflow: full-ci (que usa setup-base internamente)

jobs:
  ci:
    uses: ./.github/workflows/full-ci.yml   # reusable workflow

# full-ci.yml usa composite por dentro:
# steps:
#   - uses: ./.github/actions/setup-base
#   - run: npm test
```

## Erros comuns de iniciante

### "CI demora 8 minutos no primeiro run e 8 no segundo. Cache não tá funcionando."

Conferir:
- `setup-node@v4` está com `cache: npm`?
- `package-lock.json` realmente existe? Sem ele, `cache: npm` não tem o que cachear
- Em runs novos (ex: primeira vez), o cache é construído mas não usado — segundo run em diante deveria pegar

### "Cache hit retorna mas npm ci ainda demora muito"

`cache: npm` cacheia o **download** dos pacotes (`~/.npm`), não o `node_modules`. `npm ci` ainda precisa "instalar" (extrair, link). É mais rápido que baixar + instalar, mas não instantâneo.

Para cachear `node_modules` direto, custom cache + cuidado com diferenças de plataforma.

### "Concurrency cancelou meu deploy de produção"

Ajuste para `cancel-in-progress: false` em workflows de deploy ou para `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`.

### "Matrix tem 100 jobs, runner pool da empresa esgotou"

Se vocês usam runners self-hosted, matrix grande pode saturar. Considere:
- Reduzir matrix
- Mover full matrix para nightly
- Aumentar pool de runners

### "Reusable workflow não compartilha cache com workflow chamador"

Caches são por repo + chave. Funciona entre runs do mesmo repo, então sim, deveria compartilhar. Verifique se a chave (`hashFiles(...)`) é a mesma.

### "Composite action `run` não funcionou — `shell` não definido"

Composite actions exigem `shell:` em todo `run:`:

```yaml
runs:
  using: composite
  steps:
    - run: echo hello
      shell: bash   # ESSENCIAL
```

Sem isso, action falha ao tentar rodar.

### "Migrei pra reusable workflow e secrets não passam"

Em `workflow_call`, secrets têm que ser declarados explicitamente:

```yaml
on:
  workflow_call:
    secrets:
      NPM_TOKEN:
        required: true
```

E o consumidor passa explicitamente:

```yaml
uses: ./.github/workflows/x.yml
secrets:
  NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
```

Alternativa: `secrets: inherit` — herda todos os secrets do chamador. Conveniente mas menos explícito.

### "Cache key sem `hashFiles` — cache nunca invalida"

```yaml
key: linux-cargo-cache       # ❌ — sempre o mesmo, nunca invalida
```

Se você nunca atualiza, build pega artefatos antigos para sempre. Use `hashFiles` em algo que muda quando deps mudam:

```yaml
key: ${{ runner.os }}-cargo-${{ hashFiles('**/Cargo.lock') }}
```

### "Workflow ficou enorme (500 linhas), difícil de manter"

Sinal de que é hora de quebrar:
- Em jobs com `needs`
- Em reusable workflows ou composite actions
- Em workflows separados por propósito

---

**Princípio que resume tudo:** CI rápido é cultura — devs confiam, fazem mais commits incrementais, qualidade sobe. Cache resolve 80% do tempo. Concurrency evita desperdício. Matrix dá coverage barato. Reusable workflow + composite action eliminam duplicação e centralizam evolução. Investir uma manhã melhorando o pipeline economiza horas todo dia, para sempre.
