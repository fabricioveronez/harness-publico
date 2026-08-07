# Template SPEC.md

O **contrato de comportamento**, orientado à IA: o que a implementação precisa
cumprir e o que a validação precisa checar. É o contexto primário de todos os
modos.

Quando há PRD, o SPEC é uma **projeção** dele — o PRD continua a fonte de verdade
e vence em conflito. Sem PRD, o SPEC é a própria fonte.

## Fronteira

| Conteúdo | Onde mora |
|---|---|
| US Rules, Edge cases, critérios de aceite, premissas | **SPEC** |
| contexto narrativo, visão, decisões de produto, métricas, riscos de negócio | PRD |
| stack, arquitetura, "como", estratégia de teste | PLAN / TRD / ADR |

Se um item não é Rule, Edge case, critério ou premissa, ele não pertence ao SPEC.

## Campos do frontmatter

`type` é o único obrigatório (OKF); o resto é convenção desta skill.
`status` é promovido **apenas** por `scripts/transicao.py`.

---

```markdown
---
type: spec
title: [Título da feature]
description: [uma frase resumindo o contrato desta fatia]
resource: [slug-do-prd | none]
tags: [sdd, spec]
created: YYYY-MM-DD
status: rascunho | pronto | em-execucao | concluido
prd: [slug-do-prd | none]
---

# SPEC: [Título da feature]

## Contrato

### US01: [Título objetivo]

Como [persona], quero [ação], para [benefício].

**Rules:**
- [regra de negócio ou comportamento esperado]
- [limite, restrição ou condição]

**Edge cases:**
- [situação anômala] → [comportamento esperado]

### US02: [Título objetivo]

[...]

## Critérios de Aceite

Cada critério é um limiar observável, com **como se prova** declarado — não em
prosa. É o que permite ao gate final e ao modo Validar executarem o mesmo
conjunto, em vez de cada um reinterpretar o texto por conta própria.

| ID   | Critério                          | Nível        | Automatizável | Alvo                        |
|------|-----------------------------------|--------------|---------------|-----------------------------|
| CA01 | [limiar observável]               | unit         | sim           | `tests/unit/x.spec.ts`      |
| CA02 | [limiar observável]               | integração   | sim           | `npm test -- --grep "sync"` |
| CA03 | [limiar observável]               | e2e          | sim           | `tests/e2e/painel.spec.ts`  |
| CA04 | [limiar observável]               | manual       | não           | verificação visual do board |

- **ID** — `CA01`, `CA02`... estáveis. As tasks referenciam por este ID.
- **Nível** — `unit` | `integração` | `e2e` | `contrato` | `manual`.
- **Automatizável** — `sim` quando existe alvo executável; `não` quando depende de
  julgamento humano, ambiente de produção ou inspeção visual.
- **Alvo** — arquivo de teste ou comando. Obrigatório quando automatizável.

## Premissas

O que foi presumido ao projetar (do PRD) ou autorar (sem PRD). Premissa errada
volta ao modo Preparar para ajuste.

- [premissa 1]

## Referências

- PRD: [`../../docs/prds/NNN-slug.md`](caminho) — fonte de verdade (quando existe)
- TRD: [`../../docs/trd.md`](caminho) — contexto técnico global
- ADRs: [`../../docs/adrs/NNN-slug.md`](caminho) — decisões que embasam o contrato
```

---

## Regras de preenchimento

- **Testável, não vago.** "Deve funcionar bem" não é critério. Reformule até virar
  limiar observável — se não dá para escrever o `Alvo`, o critério ainda está vago.
- **Todo critério automatizável precisa de `Alvo`.** `scripts/cobertura.py` acusa
  quando falta, porque um critério automatizável sem alvo é um teste que ninguém
  vai rodar.
- **Projeção fiel.** Com PRD, não invente Rule ou Edge case fora dele. Lacuna vira
  premissa marcada e um aviso para voltar ao `escrever-prd`.
- **IDs estáveis.** `US01`, `CA01` não mudam depois de atribuídos — tasks, commits
  e relatórios apontam para eles.
- **Cross-links, não cópia.** Referencie PRD/TRD/ADR por link; colar o conteúdo
  reintroduz o peso de contexto que o SPEC existe para resolver.
- **Escopo da fatia.** O SPEC projeta **apenas as USs desta fatia**; as demais
  moram nos SPECs das irmãs.
