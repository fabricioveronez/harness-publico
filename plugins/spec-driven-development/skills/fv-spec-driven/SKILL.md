---
name: fv-spec-driven
description: >
  Ciclo completo de execução spec-driven de uma feature, do contrato ao fechamento.
  Cobre quatro modos sobre o mesmo bundle `./.aidev/{slug}/` (`SPEC.md` + `PLAN.md` +
  `TASKS.md`): **Preparar** (decompõe o escopo em 1..N fatias independentes, gera o
  bundle de cada uma e o manifesto com as ondas de paralelismo), **Orquestrar**
  (roda as fatias de uma onda em paralelo, cada uma isolada em git worktree, e
  mergeia de volta), **Implementar** (executa as tasks em cadeia, com loop de
  correção e commit semantic por task verde) e **Validar** (confere código contra
  o contrato, trata drift e fecha o ciclo). O modo é detectado a partir do estado
  no disco — não é preciso saber qual fase pedir.
  Use sempre que o usuário quiser preparar a execução de uma feature, gerar
  SPEC/PLAN/TASKS, projetar a spec a partir de um PRD ou de um brainstorm,
  quebrar uma feature em tasks ou em fatias, gerar o manifesto, rodar as fatias em
  paralelo, executar o manifesto, implementar as tasks, tocar a implementação,
  retomar de onde parou, continuar implementando, validar a implementação, checar
  drift entre documento e código, fechar a feature, ou mencionar `.aidev`, "bundle
  de execução", "plano de implementação", "loop de correção", "worktree por
  fatia", "execução paralela", "reconciliar plano", "fechar o ciclo spec-driven".
  Use mesmo quando o usuário não nomear a fase — o estado do `./.aidev/` diz qual é.
  Não escreve nem edita PRD (skill `escrever-prd`), TRD ou ADR (skill
  `escrever-trd`); consome os três quando existem.
---

# fv-spec-driven

Executa o ciclo spec-driven de uma feature sobre um **bundle** em `./.aidev/{slug}/`:

- **`SPEC.md`** — o contrato de comportamento (US Rules, Edge cases, critérios de
  aceite). É o contexto primário de todos os modos.
- **`PLAN.md`** — a abordagem técnica, os arquivos afetados e a estratégia de teste.
- **`TASKS.md`** — o checklist de execução, com o progresso `[X]` e as notas de pausa.

Quando o escopo rende mais de uma **fatia** (feature independente e testável), cada
fatia vira um bundle `./.aidev/{base}-{fatia}/` e o conjunto ganha um **manifesto**
`./.aidev/{base}-manifest.md` com o grafo de dependência e as ondas de paralelismo.

## O que esta skill não faz

Três artefatos têm donas próprias e são consumidos, nunca editados aqui:

| Artefato | Dona | Papel aqui |
|---|---|---|
| PRD (`docs/prds/`) | `escrever-prd` | fonte de verdade quando existe; lido sob demanda |
| TRD (`docs/trd.md`) | `escrever-trd` | contexto técnico global; lido na preparação |
| ADR (`docs/adrs/`) | `escrever-trd` | decisões que embasam o contrato; referenciadas |

O ciclo roda **sem** os três. Sem PRD, o `SPEC.md` é a própria fonte de verdade.
A única escrita permitida fora do bundle é a promoção de `status` do PRD — e só
sob a guarda do passo de fechamento (ver *Regras invioláveis*).

## Os quatro modos

| Modo | Entra quando | Produz |
|---|---|---|
| **Preparar** | não há bundle para o escopo, ou o usuário pede edição/reconciliação | bundles + manifesto, commitados |
| **Orquestrar** | há manifesto com 2+ fatias e fatia elegível pendente | fatias da onda executadas em worktree e mergeadas |
| **Implementar** | há bundle único (ou uma fatia alvo) com task `[ ]` elegível | código, `[X]`, um commit semantic por task |
| **Validar** | as tasks do bundle estão `[X]`, ou o usuário pede validação | relatório de coerência e fechamento por status |

Os modos são fases de um ciclo, não skills concorrentes: Preparar → (Orquestrar →)
Implementar → Validar. Orquestrar é uma camada de fan-out sobre Implementar — ela
não reimplementa nada, só roda N instâncias isoladas.

## Detecção de modo

Não deduza a fase a partir da frase do usuário. **Pergunte ao disco:**

```bash
python3 scripts/bundle_state.py [--slug {base}]
```

Devolve JSON com: bundles encontrados, manifesto e fatias, contagem de tasks
`[ ]`/`[X]` por fatia, notas de pausa abertas, `status` de cada artefato, ondas
elegíveis, e o estado do git (working tree limpo? bundle já commitado?). O campo
`modo_sugerido` traz a fase que o estado indica.

Por que via script e não por leitura: a decisão depende de cruzar seis sinais em
N fatias, e é o tipo de contagem que a leitura em prosa erra em silêncio quando
o bundle cresce. O script erra alto — se o estado for incoerente, ele diz qual
incoerência, e aí o caminho é reconciliar (modo Preparar), nunca adivinhar.

O usuário pode sempre forçar um modo ("valida mesmo com task aberta", "reconcilia
o plano"). Pedido explícito vence a sugestão do script; estado incoerente não.

## Regras invioláveis

Estas cinco regras existiam como fronteira entre skills separadas. Numa skill só,
elas dependem de disciplina — e são justamente o que impede o modo mais destrutivo
de falha, que é o documento ser reescrito para justificar o código que se desviou.

1. **Autoridade `PRD > SPEC > código`.** Em conflito, vence o documento de maior
   autoridade. Nunca ajuste o contrato para bater com um código divergente sem que
   o usuário decida — é isso que apaga a intenção original.

2. **O modo Validar não edita código; o modo Implementar não edita contrato.**
   Gap de código encontrado na validação vira relatório e volta ao modo Implementar.
   Lacuna de contrato encontrada na implementação vira pausa `lacuna-spec` e volta
   ao modo Preparar (ou ao `escrever-prd`). Nenhum dos dois resolve sozinho o
   problema do outro, mesmo tendo permissão técnica para isso agora.

3. **Progresso `[X]` nunca é apagado.** Edição e reconciliação preservam tudo que
   já foi concluído. Se uma mudança invalida uma conclusão, pergunte — não
   sobrescreva.

4. **Commit só sob task verde e escopo fechado.** Nunca `git add -A`, nunca
   `--no-verify`, nunca `--no-gpg-sign`. Um hook que falha é sinal real, não
   obstáculo.

5. **Transição de status passa pelo script.** `python3 scripts/transicao.py` é o
   único caminho para promover status de bundle, manifesto ou PRD. Ele carrega as
   guardas que a prosa esquece — principalmente a de que **o PRD só fecha quando
   todas as fatias do manifesto fecharam**.

## Modo Preparar

Lê `references/modo-preparar.md`.

Resumo: identifica a origem (PRD, brainstorm/documento solto, ou descrição direta),
carrega contexto técnico (TRD ou mini-coleta), **decompõe o escopo em fatias** e
apresenta o corte para aprovação **antes** de gerar arquivo. Só então gera os
bundles e o manifesto em lote atômico, e **commita o bundle**.

O commit do bundle não é zelo: o modo Orquestrar cria worktrees a partir do HEAD,
e um bundle não commitado simplesmente não existe dentro do worktree. Preparar que
não commita produz uma decomposição que não roda.

Cobre também **edição** (ajustar bundle existente) e **reconciliação** (absorver
mudança do PRD/SPEC sem perder progresso).

## Modo Orquestrar

Lê `references/modo-orquestrar.md`.

Resumo: lê o manifesto, calcula as ondas elegíveis, cria um worktree por fatia
(`scripts/worktree.py create`), dispara **uma instância do modo Implementar por
fatia via subagente** dentro do seu worktree, e ao fim da onda mergeia em sequência
(`scripts/worktree.py merge-wave`), consolida a memória
(`scripts/memory_fold.py`) e limpa os worktrees.

Fatia que pausa não derruba as irmãs — bloqueia só as dependentes.

Conflito de merge é sinal de corte não-disjunto: **pare e reconcilie**, nunca
resolva automaticamente. A única exceção é a memória, que é compartilhada por
construção e por isso tem consolidação própria, fora do merge de branch.

## Modo Implementar

Lê `references/modo-implementar.md`.

Resumo: linha de base verde → seleciona a próxima task elegível (respeitando
`needs:` e grupos `[P]`) → executa passos → roda o bloco `Validação:` → em falha,
loop de correção de até 5 ciclos com execução seletiva de testes → task verde
vira `[X]` e um commit semantic.

Pausa registra bloco no `TASKS.md` com **vocabulário controlado** de motivo e
devolve controle. Nunca invente motivo em texto livre — o vocabulário é o que
torna a retomada e o relatório legíveis por máquina.

Ao fim da cadeia, gate final: executa os critérios de aceite automatizáveis e
emite a tabela de cobertura via `scripts/cobertura.py`.

## Modo Validar

Lê `references/modo-validar.md`.

Resumo: confere o código contra o contrato (cobertura de US, Rules, Edge cases,
critérios de aceite), classifica cada divergência por **impacto** antes de agir
(pequena → ajusta o texto do SPEC; grande → pergunta), respeita a autoridade na
direção do ajuste, e fecha o ciclo via `scripts/transicao.py`.

Fechar é terminal e guardado: bundle fecha sozinho; **PRD e manifesto só fecham
quando a última fatia fechar**. Fechar o PRD cedo trancaria as fatias irmãs, já
que PRD `concluido` é imutável e bloqueia tanto implementação quanto reconciliação.

## Onde o estado vive

```
<projeto>/
├── .aidev/                          # versionado — o worktree precisa enxergar
│   ├── {base}-manifest.md           # só com 2+ fatias
│   ├── {base}-{fatia}/              # SPEC.md + PLAN.md + TASKS.md
│   └── {base}/                      # bundle único quando N=1
├── docs/
│   ├── MEMORY.md                    # memória consolidada do projeto
│   ├── .memory/{fatia}.md           # memória por fatia, durante a onda; consolidada e removida
│   ├── prds/, trd.md, adrs/         # de outras skills, só leitura
└── ../.aidev-wt/{base}-{fatia}/     # worktrees efêmeros, fora do repo
```

`.aidev/` é **versionado**. Duas razões: o commit por task já inclui o `TASKS.md`
para o histórico refletir o progresso, e o worktree só enxerga o que está em HEAD.

## Scripts

Rodam sem entrar em contexto. Use-os em vez de reimplementar a mecânica em prosa —
é o que impede que um passo determinístico seja pulado num contexto longo.

| Script | Para quê |
|---|---|
| `scripts/bundle_state.py` | estado do `.aidev/` + git em JSON; sugere o modo |
| `scripts/transicao.py` | promove status com as guardas de fechamento |
| `scripts/worktree.py` | cria / mergeia onda / limpa worktrees e branches |
| `scripts/memory_fold.py` | consolida `docs/.memory/*.md` em `docs/MEMORY.md` |
| `scripts/cobertura.py` | tabela US × critério de aceite × task |

Todos usam só a biblioteca padrão do Python 3 e aceitam `--help`.

## Saída ao usuário

Formato curto e fixo, sem narração longa e sem emoji:

```
Modo: <preparar | orquestrar | implementar | validar>
Estado: <uma linha>
Próxima ação sugerida: <uma linha>
```

Nos modos Orquestrar e Validar, o relatório completo segue
`references/templates/template-relatorio.md`.

## Referências

Carregue sob demanda, conforme o modo:

- `references/modo-preparar.md` — decomposição em fatias, geração, edição, reconciliação
- `references/modo-orquestrar.md` — ondas, worktree, merge, memória
- `references/modo-implementar.md` — loop de correção, commit, pausa, retomada
- `references/modo-validar.md` — divergência, autoridade, fechamento
- `references/heuristicas-execucao.md` — teste por passo, filtro seletivo, drift, commit
- `references/heuristicas-validacao.md` — régua pequena/grande, direção do ajuste
- `references/estado-do-bundle.md` — máquina de estados e quem transiciona o quê
- `references/templates/` — SPEC, PLAN, TASKS, manifesto, nota de pausa, memória, relatório
