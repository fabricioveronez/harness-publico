# orquestrar-execucao

Orquestra a execução **paralela** de uma decomposição multi-fatia gerada pela
`preparar-execucao`. Lê o manifesto `./.aidev/{base}-manifest.md`, computa as
**ondas** (ordenamento topológico sobre o grafo `needs`/`[P]` das fatias) e, em
cada onda, dispara **uma instância de `implementar-task` por fatia em paralelo**,
cada uma isolada em seu **git worktree** próprio (branch `exec/{base}-{fatia}`)
para evitar corrida nos commits automáticos. Ao fim de cada onda faz o **merge**
dos worktrees de volta na base e libera a próxima onda. É uma camada de
**fan-out** por cima do `implementar-task` — não reimplementa nada dele.

## Pré-requisitos e configuração

- Uma decomposição **multi-fatia** com manifesto `./.aidev/{base}-manifest.md`,
  gerada pela `preparar-execucao`. Com **1 fatia** (sem manifesto), não há
  paralelismo a orquestrar — rode `implementar-task` direto no bundle.
- **Manifesto coerente com os bundles.** A skill valida que cada fatia listada
  existe como bundle íntegro; incoerência → **aborta** e manda reconciliar via
  `preparar-execucao`.
- **Working tree limpo** na base antes de iniciar (a skill cria worktrees a
  partir dela). Estado sujo → aborta pedindo commit/stash.
- `git` com suporte a `worktree` (Git ≥ 2.5), `user.name`/`user.email` e, quando
  o projeto exigir, chave de assinatura. Nem o `implementar-task` disparado nem a
  própria orquestração passam `--no-verify`, `--no-gpg-sign` ou `--force` — a
  regra vale também para os **merges e pushes feitos por esta skill**.

## Dependências externas

- `git worktree` — cria um working tree isolado por fatia; requer Git recente.
- Test runner do projeto (indireto) — cada `implementar-task` disparado usa o
  `Comando de teste:` do PLAN da fatia, como no fluxo normal.

### Como funciona (resumo)

1. Lê o manifesto e valida que cada fatia existe como bundle coerente.
2. Confere pré-condições de git (working tree limpo, sem worktrees órfãos).
3. Calcula as ondas elegíveis (fatia elegível quando todas as `needs`
   concluíram).
4. Por onda: cria worktree + branch por fatia e dispara `implementar-task` em
   paralelo (via subagentes).
5. Ao fim da onda: merge sequencial das branches na base (arquivos disjuntos →
   sem conflito), remove worktrees, recalcula ondas.
6. Reentrante: reinvocar retoma das fatias/ondas pendentes pelo estado dos
   `TASKS.md`.

### Estados de fatia no relatório

| Estado | Significado |
|---|---|
| **concluída** | todas as tasks `[X]`, branch mergeada na base |
| **pausada** | o `implementar-task` da fatia pausou; o motivo acompanha o estado |
| **bloqueada** | alguma `needs` não concluiu; o relatório diz por qual fatia |
| **pendente** | ainda não entrou em nenhuma onda executada |

Erro fatal ao **criar o worktree ou disparar** a fatia (path ocupado, branch já
existe) é reportado como **erro de orquestração**, não como falha de código: as
demais fatias da onda seguem, e a skill sugere limpar os worktrees órfãos.

## Skills relacionadas

- **preparar-execucao** — gera as fatias e o manifesto que esta skill consome; é
  quem decide a decomposição e reconcilia o corte. Conflito de merge aqui volta
  para ela.
- **implementar-task** — a unidade de trabalho disparada por fatia (uma
  instância por bundle, isolada em worktree). Esta skill só faz o fan-out.
- **validar-implementacao** — fecha o ciclo depois, **uma invocação por fatia**.
  Esta skill **para na implementação**; não valida nem promove status.

## Exemplos de uso

```
Executa as fatias do PRD 003 em paralelo

Roda o manifesto de autenticação

Orquestra os bundles que acabamos de preparar

Retoma a orquestração — a fatia de recuperação pausou ontem

Dispara as implementações em paralelo
```

## Limitações conhecidas

- **Não resolve conflito de merge** — conflito significa que a decomposição não
  era disjunta (corte ruim); a skill para e manda reconciliar via
  `preparar-execucao`.
- **Não valida nem fecha o ciclo** — a validação código↔contrato e a promoção de
  status para `concluido` são da `validar-implementacao`.
- **Não decide a decomposição** — corte, grafo e manifesto são da
  `preparar-execucao`; esta skill só lê o manifesto.
- **Não roda com 1 fatia** — sem manifesto não há paralelismo; use
  `implementar-task` direto.
- **Uma fatia que pausa bloqueia só as dependentes** — as irmãs da mesma onda
  seguem; o progresso commitado da fatia pausada é mergeado e ela é retomável.
- **Merge é sequencial ao fim da onda** — o paralelismo real está na fase de
  trabalho de cada fatia, não no merge (que escreve no HEAD da base).

### Referências da skill

- `references/isolamento-e-merge.md` — criação dos worktrees, política de merge
  e limpeza.
- `references/template-relatorio.md` — formato do relatório de ondas e estados
  de fatia.
