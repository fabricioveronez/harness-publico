# Template MANIFEST

Estrutura canônica do **manifesto de execução** gerado pela skill
`preparar-execucao` quando um escopo é decomposto em **múltiplas fatias**
(bundles). É gravado como `./.aidev/{slug}-manifest.md` — um **arquivo**, não
um diretório, para que as consumidoras que localizam bundles varrendo os
diretórios de `./.aidev/` o ignorem naturalmente.

O manifesto é o **plano de execução no nível do bundle**: para os bundles, é o
que `[P]`/`needs` do `TASKS.md` é para as tasks. Concentra o que nenhum bundle
sabe sozinho — o índice do conjunto, o grafo de dependência entre fatias, as
ondas de paralelismo já resolvidas e o rollup fatia→US→marco.

## Quando existe

- **Sempre que a decomposição gera 2+ fatias.** Com **1 fatia** (N=1, típico de
  feature pequena / modo sem PRD), o manifesto é **opcional** — o bundle único
  se resolve sozinho.
- **Com PRD** — a coluna `Marco` referencia o milestone do PRD que a fatia
  atende (fatia ⊆ marco).
- **Sem PRD** — não há milestones; a coluna `Marco` fica `—` e o rollup cai
  para as USs/critérios de aceite do próprio SPEC de cada fatia. Nesse caso o
  manifesto é o **único** artefato que registra que os N SPECs foram uma
  decomposição só.

## Quem consome

O **orquestrador** (`orquestrar-execucao`) lê o manifesto para computar as ondas
e disparar as fatias independentes em paralelo. As skills que rodam um bundle
isolado (`implementar-task`, `validar-implementacao`) **não** precisam dele.

## Semântica dos campos de controle

O manifesto segue OKF: o único campo **obrigatório** é `type`; os demais são
convenção desta skill.

**`type`** (OKF, obrigatório) — `manifest`.

**`prd`** — slug do PRD decomposto, ou `none` (decomposição sem PRD). Igual ao
usado nos bundles-filhos.

**`created`** — data (YYYY-MM-DD) da primeira geração. Não muda em edições.

---

```markdown
---
type: manifest
title: [Título do escopo decomposto, espelhando o PRD/feature]
description: [uma frase: quantas fatias e o que a decomposição cobre]
resource: [slug-do-prd | none]
tags: [sdd, manifest]
created: YYYY-MM-DD
prd: [slug-do-prd | none]
---

# MANIFESTO: [Título do escopo decomposto]

## Referências

- **PRD:** [`../../docs/prds/NNN-slug.md`](caminho) — fonte de verdade (quando existe)
- **Fatias:** cada linha da tabela aponta um bundle `./.aidev/{prd}-{fatia}/`

## Fatias

Cada fatia é um bundle independente e testável (`SPEC`+`PLAN`+`TASKS`). `[P]` =
fatia sem dependência, elegível para a onda paralela. `needs` = fatias que
precisam estar concluídas antes.

| Fatia (bundle)              | USs        | Marco | needs                | [P] |
|-----------------------------|------------|-------|----------------------|-----|
| `003-auth-login`            | US01, US02 | M1    | —                    | [P] |
| `003-auth-recuperacao`      | US03       | M1    | —                    | [P] |
| `003-auth-2fa`              | US04       | M2    | `003-auth-login`     |     |

## Ondas

Ordenamento topológico já resolvido a partir de `needs`. Fatias na mesma onda
não se cruzam em "Arquivos Afetados" e podem rodar em paralelo.

- **Onda 1** (paralelo): `003-auth-login`, `003-auth-recuperacao`
- **Onda 2**: `003-auth-2fa` (precisa de `003-auth-login`)

## Rollup de marcos

Fecha o checklist de aceite do PRD por marco. Um marco fecha quando todas as
suas USs foram entregues (todas as tasks das fatias que cobrem essas USs com
`[X]`). Sem PRD, esta seção é omitida.

| Marco | USs        | Fatias                                    |
|-------|------------|-------------------------------------------|
| M1    | US01–US03  | `003-auth-login`, `003-auth-recuperacao`  |
| M2    | US04       | `003-auth-2fa`                            |
```

---

## Regras de preenchimento

- **Uma linha por fatia** na tabela `## Fatias`; o nome bate exatamente com o
  diretório do bundle em `./.aidev/`.
- **`[P]` e `needs` são mutuamente exclusivos** — fatia com `needs` preenchido
  nunca recebe `[P]`. A dependência explícita prevalece (mesma regra do `[P]`
  de task).
- **Ondas derivam de `needs`** — não inventar ordem; a onda de uma fatia é
  `1 + max(onda das suas dependências)`.
- **Fatia ⊆ marco** — cada fatia atende **um** marco (ou `—` sem PRD). Um marco
  pode ter várias fatias; uma fatia não cruza dois marcos (mantém o rollup
  limpo).
- **`## Rollup de marcos` só com PRD** — sem PRD, omitir a seção.
- **Manifesto reflete o estado da decomposição** — em reconciliação, fatias
  novas entram na tabela e nas ondas; fatias órfãs concluídas são anotadas como
  histórico, nunca apagadas.
