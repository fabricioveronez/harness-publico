# Isolamento e merge — git worktree por fatia

Mecânica canônica que a skill `orquestrar-execucao` usa para rodar as fatias em
paralelo sem corrida nos commits automáticos do `implementar-task`. Cada fatia
vive numa **branch** e num **worktree** próprios; o merge de volta à base
acontece **ao fim da onda**, em sequência.

Convenções:

- **Base** — a branch/commit de onde a orquestração parte (registrada no passo 2
  do fluxo). Todas as fatias saem dela.
- **Branch da fatia** — `exec/{base}-{fatia}` (ex.: `exec/003-auth-login`).
- **Worktree da fatia** — diretório isolado fora da árvore versionada, sugestão
  `../.aidev-wt/{base}-{fatia}/` (irmão do repo, para não sujar o working tree
  nem o `./.aidev/`).

## 1. Criar o worktree de uma fatia

A partir da raiz do repo, com a base em check-out e limpa:

```bash
git worktree add ../.aidev-wt/{base}-{fatia} -b exec/{base}-{fatia}
```

- Cria a branch `exec/{base}-{fatia}` a partir do HEAD atual (a base) e faz o
  check-out dela no worktree isolado.
- O worktree é um check-out completo do repo → o bundle
  `./.aidev/{base}-{fatia}/` existe lá dentro. O `implementar-task` roda **com o
  cwd no worktree** e aponta o slug da fatia.
- Se a branch já existe (execução anterior não limpa), ver a seção 4 (órfãos)
  antes de recriar.

## 2. Merge da fatia de volta na base (fim da onda)

Depois que a instância de `implementar-task` daquela fatia retornou (concluída
ou pausada, com o progresso commitado na branch da fatia), a partir da **base**:

```bash
git merge --no-ff exec/{base}-{fatia} -m "merge(exec): {base}-{fatia}"
```

- Fatias da mesma onda têm **arquivos afetados disjuntos** → o merge não
  conflita. `--no-ff` preserva a fronteira da fatia no histórico; alternativa é
  fast-forward quando a base não andou.
- **Merges são sequenciais**: mergear uma fatia por vez, nunca em paralelo (o
  merge escreve no index/HEAD da base).
- **Conflito** aqui = a decomposição não era disjunta (corte ruim). **Parar**,
  preservar os worktrees, reportar as fatias envolvidas e mandar reconciliar via
  `preparar-execucao`. **Nunca** resolver conflito automaticamente.

## 3. Remover o worktree e a branch mergeados

Após o merge bem-sucedido de uma fatia concluída:

```bash
git worktree remove ../.aidev-wt/{base}-{fatia}
git branch -d exec/{base}-{fatia}
```

- Fatia **pausada**: mergear o progresso já commitado (tasks `[X]`), então
  remover o worktree, **mas manter** a fatia marcada como pausada no relatório.
  Na retomada, o worktree é recriado a partir da base (que já tem o progresso) e
  o `implementar-task` continua pelo estado do `TASKS.md`.

## 4. Limpeza de worktrees órfãos

Antes de iniciar (passo 2 do fluxo), conferir e limpar restos de execução
anterior:

```bash
git worktree list                      # inspecionar
git worktree prune                     # remover registros de worktrees sumidos
git worktree remove --force ../.aidev-wt/{base}-{fatia}   # se preciso
git branch -D exec/{base}-{fatia}      # remover branch órfã (após confirmar merge/descartar)
```

- Só apagar branch órfã com `-D` (force) após confirmar que o progresso dela já
  foi mergeado ou que o usuário aceitou descartar. Na dúvida, **reportar e
  perguntar** — não descartar trabalho silenciosamente.

## Regras duras

- **Um worktree por fatia, uma branch por fatia.** Nunca duas fatias no mesmo
  working tree.
- **Merge sempre ao fim da onda, sempre sequencial.**
- **Conflito de merge nunca é resolvido aqui** — volta para `preparar-execucao`.
- **Nunca** `--no-verify`, `--force` (em merge) ou flags que burlam hooks.
