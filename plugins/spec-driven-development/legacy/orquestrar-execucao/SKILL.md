---
name: orquestrar-execucao
description: >
  Orquestra a execução **paralela** de uma decomposição multi-fatia gerada por
  `preparar-execucao`. Lê o manifesto `./.aidev/{base}-manifest.md`, computa as
  **ondas** (ordenamento topológico sobre o grafo `needs`/`[P]` das fatias) e,
  em cada onda, dispara **uma instância de `implementar-task` por fatia em
  paralelo**, cada uma isolada em seu **git worktree** próprio (branch
  `exec/{base}-{fatia}`) para evitar corrida nos commits automáticos. Ao fim de
  cada onda faz o **merge** dos worktrees de volta na base (arquivos disjuntos
  entre fatias → merge sem conflito), remove os worktrees e libera a próxima
  onda. Uma fatia que pausa não bloqueia as irmãs da mesma onda — bloqueia só as
  dependentes; a onda seguinte só roda as fatias cujas dependências fecharam. A
  skill **para na implementação**: reporta o estado por fatia e **não** encadeia
  `validar-implementacao`, não decide a decomposição (papel de
  `preparar-execucao`) nem edita bundles/SPEC/PRD. Use quando o usuário quiser
  executar as fatias em paralelo, rodar a decomposição, orquestrar os bundles,
  disparar as implementações em paralelo, "executar o manifesto", "rodar as
  ondas", "tocar todas as fatias", retomar uma orquestração pausada, ou
  mencionar "orquestrar execução", "execução paralela", "worktree por bundle",
  "fan-out das tasks".
---

# Orquestrar Execução (fatias em paralelo)

Executa em paralelo os bundles de uma decomposição multi-fatia, coordenando pelo
**manifesto** e isolando cada fatia num **git worktree**. É uma camada de
**fan-out** por cima do `implementar-task` — não reimplementa nada dele: cada
fatia é tocada por uma instância normal de `implementar-task`, só que num
worktree isolado e disparada em paralelo com as irmãs da mesma onda.

## Papel no fluxo spec-driven

O fluxo é: `escrever-prd` (opcional) → `preparar-execucao` (decompõe em fatias +
manifesto) → **`orquestrar-execucao`** → `implementar-task` (×N, em paralelo) →
`validar-implementacao`. Esta skill entra **entre** a preparação e a
implementação, quando a decomposição tem **2+ fatias** e vale rodá-las em
paralelo.

Princípios:

- **O manifesto manda** — a topologia (fatias, `needs`, ondas) vem do
  `./.aidev/{base}-manifest.md`. A skill não recomputa o corte nem infere
  dependências do zero; consome o que `preparar-execucao` já resolveu.
- **Isolamento por worktree** — cada fatia roda em `git worktree` próprio com
  branch dedicada. Motivo: `implementar-task` **commita por task**; rodar
  várias fatias no mesmo working tree causaria corrida no index/HEAD mesmo com
  arquivos disjuntos.
- **Independência = paralelismo** — fatias na mesma onda têm arquivos afetados
  disjuntos (garantido pela decomposição), então rodam juntas e dão merge sem
  conflito.
- **Não valida, não decide** — para no `implementar-task`. Fechar o ciclo é da
  `validar-implementacao`; decompor/re-cortar é da `preparar-execucao`.
- **Reentrante** — pode ser reinvocada; relê o estado (marcações `[X]` nos
  TASKS de cada fatia, notas de pausa) e retoma das fatias/ondas pendentes.

## Entrada

`$ARGUMENTS` — se fornecido, referência ao slug base / ao manifesto (número/slug
do PRD, slug base da feature, ou caminho de `./.aidev/{base}-manifest.md`). Se
ausente:

- **Único manifesto em `./.aidev/`** → autodetecta esse slug base.
- **Múltiplos manifestos** → listar e pedir ao usuário qual usar.
- **Nenhum manifesto, mas há um bundle único** (`./.aidev/{base}/`, decomposição
  N=1) → não há paralelismo a orquestrar; sugerir rodar `implementar-task`
  direto naquele bundle.
- **Nada em `./.aidev/`** → abortar sugerindo `preparar-execucao`.

## Fluxo de Execução

### 1. Localização e leitura do manifesto

1. Resolver o slug base a partir de `$ARGUMENTS` ou autodetecção.
2. Ler o manifesto `./.aidev/{base}-manifest.md`: tabela de fatias
   (`Fatia | USs | Marco | needs | [P]`) e a seção **Ondas**.
3. Validar coerência: toda fatia da tabela existe como diretório
   `./.aidev/{base}-{fatia}/` com `SPEC.md`+`PLAN.md`+`TASKS.md`; todo `needs:`
   referencia uma fatia existente; as ondas são consistentes com o grafo. Se
   houver incoerência (manifesto ↔ bundles dessincronizados), **abortar** e
   sugerir reconciliação via `preparar-execucao`.

### 2. Pré-condições de git

1. Exigir **working tree limpo** na base (`git status --porcelain` vazio) antes
   de criar worktrees. Sujo → abortar pedindo ao usuário resolver (commit/stash).
2. Registrar a branch/commit base de partida (todas as fatias saem dela).
3. Conferir que não há worktrees órfãos de uma execução anterior (ver seção 4 do
   `references/isolamento-e-merge.md` para limpeza).

### 3. Cálculo do estado das ondas

1. Para cada fatia, ler o `TASKS.md` do bundle e classificar:
   - **Concluída** — todas as tasks `[X]`.
   - **Pendente** — há tasks `[ ]` e nenhuma nota de pausa aberta.
   - **Pausada** — há bloco `> Pausa em ...` aberto (motivo do `implementar-task`).
2. Recalcular as ondas elegíveis: uma fatia é **elegível** quando está pendente
   e todas as suas dependências (`needs`) estão **concluídas**. Fatias cujas
   dependências pausaram/falharam ficam **bloqueadas**.
3. Se não há fatia elegível (tudo concluído, ou o que resta está bloqueado por
   pausa) → ir direto ao relatório (passo 7).

### 4. Execução da onda (fan-out isolado)

Para a onda elegível corrente:

1. **Criar um worktree por fatia** — `git worktree add` num caminho isolado com
   branch `exec/{base}-{fatia}` a partir da base (comandos canônicos na seção 1
   do `references/isolamento-e-merge.md`).
2. **Disparar `implementar-task` em paralelo** — uma instância por fatia (via
   subagentes), cada uma rodando **dentro do seu worktree** e apontando o slug
   da sua fatia. Cada instância segue o fluxo normal do `implementar-task`
   (inclusive o passo 2b de avaliação/carga de skills e o commit por task).
3. **Aguardar a onda** — coletar o resultado de cada fatia: concluída, pausada
   (com motivo) ou erro.
4. **Pausa/erro numa fatia não derruba as irmãs** — as outras fatias da onda
   seguem até terminar. Só as fatias **dependentes** (ondas seguintes) da que
   pausou ficam bloqueadas.

### 5. Merge da onda

Após todas as fatias da onda retornarem:

1. **Merge de cada branch de volta na base**, em sequência (não em paralelo).
   Como os arquivos afetados são disjuntos entre fatias, os merges são
   conflict-free (fast-forward ou merge trivial). Comandos na seção 2 do
   `references/isolamento-e-merge.md`.
2. **Conflito inesperado no merge** = sinal de que a decomposição não era
   disjunta (corte ruim). **Parar**, preservar os worktrees, reportar as fatias
   em conflito e sugerir reconciliação via `preparar-execucao`. Não resolver
   conflito automaticamente.
3. **Remover os worktrees** já mergeados e apagar suas branches (seção 3 do
   `references/isolamento-e-merge.md`). Fatias pausadas: mergear o progresso
   **já commitado** (tasks `[X]`), remover o worktree, e deixar a fatia marcada
   como pausada para retomada futura.
4. Voltar ao passo 3 (recalcular ondas) — a conclusão desta onda pode liberar a
   próxima.

### 6. Retomada (reinvocação)

Acionada automaticamente quando já há progresso (`[X]`/pausas nos TASKS das
fatias). A skill relê o estado (passo 3), pula fatias concluídas, e retoma as
elegíveis. Fatias pausadas voltam a ser tentadas quando reinvocadas: recria-se o
worktree a partir da base (que já tem o progresso mergeado) e o `implementar-task`
retoma do ponto exato pelo estado do próprio `TASKS.md`.

### 7. Relatório final

Devolver controle com o relatório por fatia (formato em
`references/template-relatorio.md`):

- Estado de cada fatia: **concluída | pausada (motivo) | bloqueada (por qual
  fatia) | pendente**.
- Ondas executadas e o que foi mergeado nesta invocação.
- Próxima ação sugerida (retomar após sanar pausa, rodar `validar-implementacao`
  nas fatias concluídas, ou reconciliar via `preparar-execucao`).
- **Lembrete**: a validação e o fechamento do ciclo são da
  `validar-implementacao`; esta skill não os executa.

## Regras transversais

### Isolamento e merge

Detalhes canônicos (criar/listar/remover worktree, branch por fatia, merge por
onda, limpeza de órfãos) em `references/isolamento-e-merge.md`. Regras duras:

- **Uma branch por fatia** (`exec/{base}-{fatia}`), **um worktree por fatia**,
  nunca duas fatias no mesmo working tree.
- **Merge sequencial** ao fim da onda, nunca durante a execução paralela.
- **Nunca resolver conflito de merge automaticamente** — conflito é bug de corte,
  volta para `preparar-execucao`.
- **Nunca `--no-verify`/`--force`** em merge ou push — hook que falha é sinal
  real.

### Falha, pausa e bloqueio

- **Pausa de fatia** (o `implementar-task` registrou `> Pausa em ...`): merge do
  progresso commitado, fatia marcada como pausada, dependentes bloqueadas,
  segue com as demais.
- **Erro fatal ao criar worktree / disparar** (path ocupado, branch já existe,
  etc.): reportar a fatia como erro de orquestração, não como falha de código;
  seguir com as demais da onda; sugerir limpeza de órfãos.
- **Bloqueio**: fatia elegível apenas quando **todas** as `needs` concluíram.

### Saída ao usuário (formato curto e fixo)

Relatório compacto (ver `references/template-relatorio.md`): estado por fatia,
ondas executadas, próxima ação. Sem narração extensa, sem emoji.

## Fora do escopo

Esta skill **não**:

- Executa as tasks em si — isso é do `implementar-task` (a skill só o dispara
  isolado e em paralelo).
- Decide a decomposição, corta fatias, infere dependências ou edita o manifesto
  (papel de `preparar-execucao`).
- Edita SPEC/PLAN/TASKS/PRD, marca `[X]` ou cria commits de task (o
  `implementar-task` faz isso dentro de cada worktree).
- Valida a implementação nem promove status para `concluido` (papel de
  `validar-implementacao`).
- Resolve conflitos de merge (conflito = corte não-disjunto → reconciliar).
- Roda quando há só 1 fatia (sem manifesto) — nesse caso, `implementar-task`
  direto.

## Referências

- `references/isolamento-e-merge.md` — comandos canônicos de git worktree
  (criar, listar, remover), branch por fatia, estratégia de merge por onda e
  limpeza de worktrees órfãos.
- `references/template-relatorio.md` — formato canônico do relatório de
  orquestração (estado por fatia, ondas, próxima ação).
