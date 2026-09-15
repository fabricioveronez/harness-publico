# fv-spec-driven

Executa o ciclo spec-driven completo de uma feature — do contrato ao fechamento — sobre um bundle `SPEC` + `PLAN` + `TASKS` em `./.aidev/`. Reúne num único fluxo a preparação (decompor o escopo em fatias independentes), a orquestração paralela (uma fatia por git worktree), a implementação (tasks em cadeia, com loop de correção e commit por task) e a validação (coerência código × contrato e fechamento). O modo é detectado a partir do estado no disco — não é preciso saber qual fase pedir.

## Por que uma skill só

O fluxo anterior tinha quatro skills — `preparar-execucao`, `orquestrar-execucao`, `implementar-task` e `validar-implementacao` — e os defeitos que impediam o caminho paralelo de rodar estavam todos na **costura** entre elas: ninguém commitava o bundle (e o worktree nasce do HEAD, então não o enxergava); a memória de projeto não tinha dono e conflitava no merge de toda onda; o PRD fechava na primeira fatia validada e trancava as irmãs, já que PRD concluído é imutável.

Fundir as quatro resolve a fronteira, mas não bastaria: mecânica escrita em prosa continua sendo pulável, ainda mais num documento longo. Por isso a metade determinística do ciclo virou `scripts/` — o passo que commita, consolida ou fecha não depende de o modelo lembrar dele.

Três artefatos continuam com donas próprias e são apenas consumidos: PRD (`escrever-prd`), TRD e ADR (`escrever-trd`). O ciclo roda sem os três — sem PRD, o `SPEC.md` é a própria fonte de verdade.

## Os quatro modos

| Modo | Entra quando | Produz |
|---|---|---|
| **Preparar** | não há bundle, ou o usuário pede edição/reconciliação | bundles + manifesto, commitados |
| **Orquestrar** | há manifesto com 2+ fatias e fatia elegível | fatias da onda executadas em worktree e mergeadas |
| **Implementar** | há bundle com task elegível | código, `[X]`, um commit semantic por task |
| **Validar** | as tasks estão `[X]`, ou o usuário pede | relatório de coerência e fechamento guardado |

## O plano de teste é declarado, não inferido

A tabela de critérios de aceite do `SPEC.md` carrega `ID`, `Nível`, `Automatizável` e `Alvo`; as tasks referenciam os critérios pelo ID; o `PLAN.md` ganha uma seção de estratégia de teste (níveis, fixtures, o que fica fora da automação e por quê).

Antes, a classificação de um critério em automatizável ou manual era feita por regex sobre prosa, em dois lugares diferentes — o gate final da implementação e a validação — que podiam chegar a conclusões distintas sobre o mesmo texto. Declarado uma vez, os dois executam o mesmo conjunto, e a cobertura vira contagem verificável (`scripts/cobertura.py`) em vez de impressão.

## Scripts

| Script | Papel |
|---|---|
| `bundle_state.py` | estado do `.aidev/` + git em JSON; sugere o modo |
| `transicao.py` | promove status com a guarda de fechamento do conjunto |
| `worktree.py` | cria / mergeia onda / limpa worktrees e branches |
| `memory_fold.py` | consolida `docs/.memory/*.md` em `docs/MEMORY.md`, idempotente |
| `cobertura.py` | tabela US × critério de aceite × task |

Todos usam só a biblioteca padrão do Python 3.

## Skills legadas

As quatro skills que este ciclo substitui — `preparar-execucao`,
`orquestrar-execucao`, `implementar-task` e `validar-implementacao` — vivem em
`plugins/spec-driven-development/legacy/`, fora de `skills/`.

Ficam preservadas para consulta e histórico, mas **fora do diretório de skills**:
enquanto estavam lá, disputavam com esta as mesmas frases de acionamento
("implementa as tasks", "valida a implementação", "prepara a execução"), sem que
houvesse como escolher qual acordaria. Ver `legacy/README.md` para o mapa de
migração e as notas de compatibilidade de bundle.
