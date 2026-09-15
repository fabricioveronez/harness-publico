# Skills legadas

## `fv-spec-driven` → fluxo `sdd` (2026-09)

A `fv-spec-driven` também virou legado. Ela foi substituída pelo fluxo **sdd**: quatro skills de
fase sobre a CLI agnóstica `sdd`, desenvolvidas em `~/projetos/meu-novo-sdd/novo-sdd`
(`plugins/sdd/`). O motivo: numa skill só, cada worker paralelo carregava o ciclo inteiro, a
memória misturava estado com conhecimento, e a própria skill empurrava para o paralelo.

| Modo da `fv-spec-driven` | Vira, no fluxo sdd |
|---|---|
| Preparar | `sdd-especificar` (sem manifesto: grafo no frontmatter do SPEC) |
| Implementar | `sdd-implementar` |
| Validar | `sdd-validar` (por fatia, com revisores independentes) + `sdd-arquivar` (por feature) |
| Orquestrar | futuro `sdd-orquestrar`, invocado só pelo usuário |
| `scripts/*.py` | CLI `sdd` (TypeScript): `estado`, `grafo`, `cobertura`, `transicao`, `commit`, `fechar`, `licoes` |

Não há migração de `.aidev/`: bundles em andamento terminam com a `fv-spec-driven` a partir daqui
(`legacy/fv-spec-driven/`) ou são reespecificados em `.sdd/`.

## As quatro skills anteriores

Estas quatro skills foram **substituídas** pela skill `fv-spec-driven`, que funde
as quatro num ciclo de quatro modos sobre o mesmo bundle.

Elas ficam aqui, fora de `skills/`, por três razões: preservar o histórico e o
raciocínio que produziram, permitir consulta durante uma migração, e — a razão
prática — **parar de competir por gatilho**. Enquanto viviam em `skills/`, as
descrições delas disputavam as mesmas frases que a skill nova ("implementa as
tasks", "valida a implementação", "prepara a execução"), e não havia como
controlar qual seria acionada.

Fora de `skills/`, elas não são carregadas como skill nem aparecem na vitrine do
site (o loader lê profundidade fixa em `plugins/<plugin>/skills/<skill>/`).

## Mapa de migração

| Skill legada | Vira, em `fv-spec-driven` |
|---|---|
| `preparar-execucao` | **Modo Preparar** — `references/modo-preparar.md` |
| `orquestrar-execucao` | **Modo Orquestrar** — `references/modo-orquestrar.md` |
| `implementar-task` | **Modo Implementar** — `references/modo-implementar.md` |
| `validar-implementacao` | **Modo Validar** — `references/modo-validar.md` |

O vocabulário sobreviveu inteiro: bundle `SPEC`+`PLAN`+`TASKS` em `./.aidev/`,
fatias, manifesto, ondas, `[P]`/`needs`, vocabulário controlado de pausa,
loop de correção de 5 ciclos, autoridade `PRD > SPEC > código`.

## Por que foram fundidas

O caminho paralelo nunca rodou de ponta a ponta, e a auditoria mostrou que os
defeitos que o impediam estavam **todos na costura entre as skills**, nenhum
dentro delas:

| Defeito | Costura |
|---|---|
| ninguém commitava o bundle — e o worktree nasce do HEAD, então não o enxergava | `preparar` → `orquestrar` |
| `docs/MEMORY.md` sem dono: único arquivo compartilhado entre fatias, conflitava em todo merge | `implementar` → `orquestrar` |
| o PRD fechava na primeira fatia validada e trancava as irmãs (PRD `concluido` é imutável) | `validar` → manifesto |
| `rascunho → pronto` do PRD e `pronto → em-execucao` do bundle não tinham dono | — |
| nenhum fechamento no nível da decomposição | — |

Fundir resolveu a fronteira; o que resolveu a mecânica foi tirá-la da prosa e
pô-la em `scripts/` — um passo determinístico escrito em parágrafo é pulável, e
quanto mais longo o documento, mais pulável fica.

## Migrar um projeto que já usa o fluxo antigo

O formato do bundle é compatível — `fv-spec-driven` lê `.aidev/` existente sem
conversão. Três ajustes valem a pena, nenhum obrigatório:

1. **Commite o `.aidev/`** se ainda não estiver versionado. Sem isso a
   orquestração aborta (e o `bundle_state.py` diz exatamente isso).
2. **Migre a tabela de critérios de aceite** do SPEC para o formato declarativo
   (`ID | Critério | Nível | Automatizável | Alvo`). O `cobertura.py` avisa quando
   encontra o formato antigo e o fluxo segue funcionando com a heurística textual
   como fallback — mas aí a classificação volta a ser regex sobre prosa.
3. **Confira o `status`** dos bundles: o fluxo antigo nunca escrevia `pronto` nem
   `em-execucao`, então bundles herdados costumam estar em `rascunho` mesmo com
   tasks feitas. `transicao.py` corrige.

## Não use estas skills

Se precisar do comportamento de uma delas, use o modo correspondente. Elas estão
aqui como registro, não como alternativa — e não recebem correção: os defeitos
encontrados depois da fusão (parsing do manifesto, `Nível: usuário` fora da tabela
de commit, alvo de teste fora de "Arquivos Afetados", alternativa descartada
reintroduzida como Edge case) foram corrigidos só em `fv-spec-driven`.
