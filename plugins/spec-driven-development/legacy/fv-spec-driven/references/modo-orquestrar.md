# Modo Orquestrar — fatias em paralelo

Roda as fatias de uma onda em paralelo, cada uma isolada num git worktree, e
mergeia de volta ao fim. É uma camada de **fan-out** sobre o modo Implementar —
não reimplementa nada dele: cada fatia é tocada por uma instância normal do modo
Implementar, só que noutro diretório e em paralelo com as irmãs.

Só entra com **2+ fatias**. Com bundle único, vá direto ao modo Implementar.

## 1. Ler o estado

```bash
python3 scripts/bundle_state.py --slug {base}
```

Confira antes de qualquer coisa:

- **`incoerencias` vazio.** Manifesto e bundles dessincronizados travam tudo —
  o caminho é reconciliar no modo Preparar, nunca contornar.
- **`git.bundle_commitado` verdadeiro.** O worktree é um check-out do HEAD. Bundle
  não commitado não existe lá dentro, e a fatia abriria um `.aidev/` vazio.
- **`git.clean` verdadeiro.** Commits automáticos dependem de escopo limpo.
- **`ondas_elegiveis`** diz o que roda agora. Fatia é elegível quando está pendente
  e **todas** as suas `needs` estão concluídas.

Se não há fatia elegível — tudo concluído, ou o que resta está bloqueado por uma
pausa — pule direto ao relatório.

## 2. Criar os worktrees da onda

```bash
python3 scripts/worktree.py criar --base {base} --fatias api,ui
```

O script revalida as pré-condições e recusa se alguma falhar. Falha ao criar
worktree é **erro de orquestração**, não falha de código da fatia: reporte
separado, siga com as demais da onda, e sugira `worktree.py orfaos` para inspecionar
restos de execução anterior.

## 3. Disparar a onda

Uma instância do modo Implementar **por fatia, via subagente**, com o cwd no
worktree daquela fatia e apontando o slug dela.

Instruções que cada subagente precisa receber:

- o caminho do worktree e o slug da fatia (`.aidev/{base}-{fatia}/`);
- que ele deve seguir `references/modo-implementar.md` normalmente, inclusive a
  avaliação de skills relevantes ao domínio e o commit por task;
- que a memória daquela fatia vai em **`docs/.memory/{base}-{fatia}.md`**, não em
  `docs/MEMORY.md`, e entra no commit da task.

Esse último ponto é o que mantém o merge trivial. `docs/MEMORY.md` seria o único
arquivo compartilhado por todas as fatias — não-disjunto por construção — e
conflitaria em toda onda, fazendo a orquestração acusar corte ruim por algo que o
próprio fluxo causou. Caminho por fatia mantém a disjunção real e a consolidação
acontece depois, fora do merge de branch.

**Pausa numa fatia não derruba as irmãs.** As outras seguem até terminar. Só as
fatias **dependentes** ficam bloqueadas.

## 4. Fechar a onda

Na ordem, e só depois que **todas** as fatias da onda retornaram:

```bash
python3 scripts/worktree.py mergear --base {base} --fatias api,ui   # sequencial
python3 scripts/memory_fold.py                                      # consolida a memória
python3 scripts/worktree.py limpar  --base {base} --fatias api,ui
git add docs/MEMORY.md && git commit -m "chore(exec): consolida memória da onda {N}"
```

Merge é **sequencial**, nunca em paralelo — ele escreve no index e no HEAD da base.

**Conflito de merge para a onda.** O script aborta o merge, preserva os worktrees
e reporta os arquivos envolvidos. Conflito significa que a decomposição não era
disjunta: o caminho é reconciliar o corte no modo Preparar. Não resolva o conflito
à mão — resolver esconde o defeito do corte e a próxima onda repete.

Se o conflito for em `docs/MEMORY.md`, o script avisa: alguma fatia escreveu na
memória consolidada em vez do caminho por fatia. Aí o defeito é de instrução ao
subagente, não do corte.

**Fatia pausada** também mergeia: o progresso já commitado (tasks `[X]`) entra na
base, o worktree é removido, e a fatia fica marcada como pausada. Na retomada, o
worktree é recriado a partir da base — que já tem o progresso — e o modo
Implementar continua pelo estado do próprio `TASKS.md`.

**Worktree que se recusa a sair** está sujo: a fatia deixou arquivo não commitado.
O script preserva e avisa. Investigue antes de forçar — `--forcar` descarta o que
estiver lá.

Depois de fechar a onda, volte ao passo 1: a conclusão desta onda pode liberar a
próxima.

## 5. Retomada

Reinvocação é o caso normal, não a exceção. `bundle_state.py` relê o progresso
(`[X]`, pausas) e devolve as elegíveis; fatias concluídas são puladas. Fatias
pausadas voltam a ser tentadas.

## 6. Relatório

Formato em `templates/template-relatorio.md`. Precisa conter:

- estado por fatia: **concluída | pausada (motivo) | bloqueada (por qual fatia) |
  pendente | erro-orquestracao**;
- ondas executadas nesta invocação e o que foi mergeado;
- próxima ação apontando o gargalo real.

O relatório termina no estado da implementação. Fechar o ciclo é do modo Validar,
e ele tem a guarda de fechamento do conjunto — não promova status aqui.

## Regras duras

- Uma branch e um worktree **por fatia**; nunca duas fatias no mesmo working tree.
- Merge sempre ao fim da onda, sempre sequencial.
- Conflito de merge nunca é resolvido aqui.
- Nunca `--no-verify`, `--force` em merge, ou flag que burla hook.
- Branch não mergeada carrega trabalho: confirme com o usuário antes de apagar.

## Fora deste modo

Não executa task (só dispara quem executa), não decide nem edita a decomposição,
não marca `[X]`, não valida e não promove status para `concluido`.
