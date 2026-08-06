# Detecção de ambiente e implementação dos scripts

Índice:
- [As duas perguntas](#as-duas-perguntas)
- [Sinais de detecção](#sinais-de-detecção)
- [Precedência](#precedência)
- [O caso composto](#o-caso-composto)
- [Implementação por ambiente](#implementação-por-ambiente)
- [Provas de validação](#provas-de-validação)
- [Esqueleto de script](#esqueleto-de-script)

---

## As duas perguntas

Não pergunte "qual é o ambiente". Pergunte duas coisas, porque o formato mais comum tem resposta diferente
para cada uma:

- **Onde as dependências vivem** — compose, devcontainer, serviço externo já rodando, nenhuma.
- **Onde o código do projeto executa** — devcontainer, container da própria aplicação, venv/uv, node local,
  host puro.

Tratar isso como uma pergunta só é o erro que produz um `exec` errado: `exec psql` quer o ambiente de
dependências, `exec pytest` quer o de execução. Quando os dois coincidem, a distinção não custa nada. Quando
não coincidem, é ela que salva o script.

---

## Sinais de detecção

| Sinal no repositório | Conclusão |
|---|---|
| `.devcontainer/devcontainer.json` | devcontainer é o ambiente de execução |
| `docker-compose.yml` com serviço da própria app (tem `build:`) | app roda em container; compose é execução **e** dependências |
| `docker-compose.yml` só com banco/cache/fila | compose é só dependências; execução está em outro lugar |
| `Dockerfile` sem compose | há imagem, mas o ciclo de vida não está definido — provável execução local, containerização parcial |
| `pyproject.toml` / `uv.lock` / `poetry.lock` / `requirements.txt` | gerenciador Python |
| `package.json` + `.nvmrc` / `engines` | Node local com versão fixada |
| `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle` | toolchain da linguagem no host |
| `Makefile` / `Taskfile.yml` com alvos de run/test | **já existe interface** — leia antes de escrever qualquer script |
| `mise.toml` / `.tool-versions` / `flake.nix` | gerenciador de toolchain |
| CI (`.github/workflows/`) | fonte mais confiável de "como isso roda de verdade" |

O CI merece atenção especial: ele é o único lugar do repositório onde alguém foi obrigado a escrever a
sequência completa que funciona numa máquina limpa. Quando houver conflito entre o README e o CI, o CI ganha.

Se já existe `Makefile` ou `Taskfile` cobrindo o ciclo, **os scripts envolvem essa interface em vez de
competir com ela**. Duas interfaces para a mesma operação divergem, e a mais nova costuma perder.

---

## Precedência

Quando mais de um candidato serve, **o ambiente é onde os testes já rodam hoje**:

```
devcontainer  >  compose  >  gerenciador de linguagem  >  host puro
```

Mas só com evidência na ficha. Sem evidência, é host — e essa conclusão vira linha do relatório de exclusão
("não achei ambiente declarado, assumi host"), nunca chute silencioso.

---

## O caso composto

O formato mais comum na prática:

```
compose sobe o Postgres          → ambiente de dependências
uv/venv/npm roda o teste         → ambiente de execução
```

Consequências para os quatro scripts:

- `up` — sobe as dependências **e** garante o ambiente de execução (instala deps, aplica lock).
- `down` — derruba as dependências. O ambiente de execução costuma não ter o que derrubar.
- `test` — roda no ambiente de execução, com as dependências de pé. Depende dos dois.
- `exec` — precisa decidir. Padrão: **ambiente de execução**, que é o que o agente quer em 90% dos casos.
  Se acesso ao ambiente de dependências for recorrente (abrir psql, inspecionar fila), isso justifica um
  script próprio pelo critério de "operação recorrente de invocação não adivinhável" — não sobrecarregue o
  `exec` com uma flag que o agente vai esquecer.

---

## Implementação por ambiente

### Devcontainer

```bash
up    → devcontainer up --workspace-folder .          # idempotente por natureza
exec  → devcontainer exec --workspace-folder . -- "$@"
test  → devcontainer exec --workspace-folder . -- <runner>
down  → docker compose -f .devcontainer/... down      # ou docker rm do container
```

Cuidado com recursão: dentro do container, `up` não deve tentar subir outro. Guarde com uma variável de
ambiente marcadora (`REMOTE_CONTAINERS`, `DEVCONTAINER`, ou uma sua).

O CLI `devcontainer` é pré-requisito de máquina — instrução para humano. Não instale, **registre no relatório
como item de endereço README**.

### Compose com a app dentro

```bash
up    → docker compose up -d --wait      # --wait respeita healthcheck e é idempotente
exec  → docker compose exec -T <servico> "$@"
test  → docker compose exec -T <servico> <runner>
down  → docker compose down              # + -v se o volume for descartável
```

O `-T` é obrigatório: sem ele o Docker aloca TTY e o script vira interativo em contexto não-interativo.

Se `down -v` remover o volume do banco, isso **precisa** virar linha proibitiva no bloco de políticas.

### Compose só com dependências

```bash
up    → docker compose up -d --wait  &&  <instalar deps no ambiente local>
exec  → <ativar ambiente> && "$@"
test  → <ativar ambiente> && cd <dir onde imports resolvem> && <runner>
down  → docker compose down
```

### Gerenciador de linguagem, sem container

```bash
up    → uv sync            # ou npm ci, poetry install, go mod download
exec  → uv run "$@"        # ou npm exec --, source .venv/bin/activate && "$@"
test  → uv run <runner>
down  → nada a derrubar; sai com sucesso e imprime que não há ambiente ativo
```

`down` que não tem o que derrubar **não é erro**. Ele sai zero e diz isso. O contrato precisa ser uniforme
para o agente não ter que raciocinar sobre exceções.

### Host puro

O `exec` continua valendo, e essa é a parte contraintuitiva. Ele nunca existiu por isolamento — existe para
haver **um lugar único por onde tudo passa**. Mesmo quase-passthrough, ele carrega ativação de ambiente,
variáveis e diretório de trabalho, e impede o agente de inventar invocação própria na primeira necessidade
não prevista.

---

## Provas de validação

Cada script tem uma prova específica. Rode todas antes de escrever o `AGENTS.md`.

| Script | Prova | Falha aceitável |
|---|---|---|
| `up` | executar duas vezes seguidas; a segunda não pode falhar | nenhuma |
| `exec` | comando que só responde certo dentro do ambiente: `hostname`, caminho exclusivo, variável do ambiente. **Compare com o valor do host** | nenhuma |
| `test` | alcançou o runner, a partir do diretório onde os imports resolvem | suíte vermelha ou inexistente → achado do projeto, não falha do portão |
| `down` | derrubou; validar por último | nenhuma |

Para o `exec`, "comparar com o host" é o que separa prova de teatro. Se `hostname` dentro e fora dão a mesma
resposta e o ambiente deveria ser um container, o `exec` está furado.

Ordem sugerida: `up` → `up` → `exec` → `test` → `down` → (`up` se o usuário for continuar trabalhando).

---

## Esqueleto de script

Referência de forma. O conteúdo sai da ficha de evidências.

```bash
#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if ! docker compose ps --status running --quiet >/dev/null 2>&1; then
  echo "erro: docker não está acessível. Inicie o Docker e rode novamente." >&2
  exit 1
fi

docker compose up -d --wait >/dev/null

echo "ambiente de pé em http://localhost:8080"
```

O que esse esqueleto está exercendo:

- `set -euo pipefail` — falha cedo e alto, em vez de seguir com estado meio pronto.
- `cd` relativo ao próprio script — funciona de qualquer diretório, e o agente chama de lugares imprevisíveis.
- checagem de pré-condição com **mensagem acionável** — a mensagem de erro é o que substitui a linha de regra
  que você não escreveu. "erro: docker não está acessível" sem o "inicie o Docker" força o agente a adivinhar.
- `>/dev/null` no comando ruidoso — o log de build não ajuda e queima contexto.
- uma linha final útil — o agente precisa saber que terminou e onde a coisa está.
