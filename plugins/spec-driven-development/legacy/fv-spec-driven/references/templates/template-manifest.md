# Template MANIFEST

O **plano de execução no nível do bundle**: para as fatias, é o que `[P]`/`needs`
do TASKS é para as tasks. Concentra o que nenhum bundle sabe sozinho — o índice do
conjunto, o grafo de dependência, as ondas já resolvidas e o rollup fatia→US→marco.

Gravado como **arquivo** (`./.aidev/{base}-manifest.md`), não diretório, para que
quem varre `./.aidev/` procurando bundles o ignore naturalmente.

## Quando existe

Sempre que a decomposição gera **2+ fatias**. Com 1 fatia, o bundle único se
resolve sozinho e não há manifesto.

## Quem consome

O modo Orquestrar, para computar as ondas. O modo Validar, para a **guarda de
fechamento** — é aqui que ele descobre se ainda há fatia irmã aberta antes de
fechar PRD e conjunto.

---

```markdown
---
type: manifest
title: [Título do escopo decomposto]
description: [uma frase: quantas fatias e o que a decomposição cobre]
resource: [slug-do-prd | none]
tags: [sdd, manifest]
created: YYYY-MM-DD
status: aberto | concluido
prd: [slug-do-prd | none]
---

# MANIFESTO: [Título do escopo decomposto]

## Referências

- **PRD:** [`../docs/prds/NNN-slug.md`](caminho) — quando existe
- **Fatias:** cada linha da tabela aponta um bundle `./.aidev/{base}-{fatia}/`

## Fatias

`[P]` = fatia sem dependência, elegível para a onda paralela. `needs` = fatias que
precisam estar concluídas antes.

| Fatia (bundle)          | USs        | Marco | needs              | [P] |
|-------------------------|------------|-------|--------------------|-----|
| `003-toil-sync`         | US01, US02 | M1    | —                  | [P] |
| `003-toil-painel`       | US03       | M1    | —                  | [P] |
| `003-toil-runner`       | US04, US05 | M2    | `003-toil-sync`    |     |

## Ondas

Ordenamento topológico já resolvido a partir de `needs`. Fatias na mesma onda não
se cruzam em "Arquivos Afetados".

- **Onda 1** (paralelo): `003-toil-sync`, `003-toil-painel`
- **Onda 2**: `003-toil-runner` (precisa de `003-toil-sync`)

## Critérios de aceite do conjunto

Critérios que **só fazem sentido com todas as fatias prontas** — integração ponta
a ponta. Colocados no SPEC de uma fatia isolada, falhariam no gate dela, porque as
irmãs ainda não existem. Ficam aqui e são executados no fechamento do conjunto.

| ID    | Critério                                   | Nível | Automatizável | Alvo                       |
|-------|--------------------------------------------|-------|---------------|----------------------------|
| CAX01 | card disparado no painel chega ao runner   | e2e   | sim           | `tests/e2e/fluxo.spec.ts`  |

[Omitir a seção quando não houver critério de conjunto.]

## Rollup de marcos

Um marco fecha quando todas as suas USs foram entregues. Sem PRD, omitir.

| Marco | USs        | Fatias                                    |
|-------|------------|-------------------------------------------|
| M1    | US01–US03  | `003-toil-sync`, `003-toil-painel`        |
| M2    | US04, US05 | `003-toil-runner`                         |

## Fechamento

Preenchido pelo modo Validar, via `scripts/transicao.py`, conforme cada fatia
fecha. O conjunto (e o PRD) só fecham quando a última linha fecha.

| Fatia               | Fechada em |
|---------------------|------------|
| `003-toil-sync`     | —          |
| `003-toil-painel`   | —          |
| `003-toil-runner`   | —          |
```

---

## Regras de preenchimento

- **Uma linha por fatia**, com nome idêntico ao diretório em `./.aidev/`.
- **`[P]` e `needs` são mutuamente exclusivos.**
- **Ondas derivam de `needs`** — não invente ordem: a onda de uma fatia é
  `1 + max(onda das dependências)`.
- **Fatia ⊆ marco.** Um marco pode ter várias fatias; uma fatia não cruza dois.
- **Reconciliação atualiza o manifesto** — fatias novas entram na tabela e nas
  ondas; fatias órfãs concluídas viram nota, nunca são apagadas.
- **`status` só muda pelo `transicao.py`.** Editar à mão contorna a guarda que
  impede o PRD de fechar com fatia aberta.
