# Template PLAN.md

Estrutura canônica do `PLAN.md` gerado pela skill `preparar-execucao`. O PLAN
captura a abordagem técnica que guia a implementação — é o "como" para o "o quê"
do `SPEC.md`. Pareado com `SPEC.md` e `TASKS.md` no mesmo diretório
`./.aidev/{slug}/`, que forma um bundle **Open Knowledge Format (OKF)**.

## Semântica dos campos de controle

O bundle segue OKF: o único campo **obrigatório** é `type`; os demais são
convenção desta skill.

**`type`** (OKF, obrigatório) — `plan`. Roteia/filtra o concept.

**`prd`** — slug do PRD que este plano atende, ou `none` (projeto sem PRD). Igual
ao nome do arquivo do PRD sem extensão (ex.: `003-autenticacao-oauth`) e ao usado
no `SPEC.md`/`TASKS.md` pareados. Cola de rastreabilidade; nunca omitir.

**`status`** — ciclo de vida do plano, espelhando o PRD mas com semântica
própria:

- `rascunho` — em geração, revisão ou edição ativa
- `pronto` — revisado, aguardando a primeira execução
- `em-execucao` — ao menos uma task já iniciou ou foi marcada
- `concluido` — todas as tasks com `[X]`; plano congelado como histórico

**`created`** — data (YYYY-MM-DD) da primeira geração. Não muda em edições
subsequentes.

---

```markdown
---
type: plan
title: [Título da feature, espelhando o SPEC]
description: [uma frase resumindo a abordagem técnica]
resource: [slug-do-prd | none]
tags: [sdd, plan]
created: YYYY-MM-DD
status: rascunho | pronto | em-execucao | concluido
prd: [slug-do-prd | none]
---

# PLAN: [Título da feature, espelhando o SPEC]

## Referências

- **SPEC:** [`SPEC.md`](SPEC.md) — o contrato que este plano realiza (irmão no bundle)
- **PRD:** [`../../docs/prds/NNN-slug.md`](caminho) — fonte de verdade (quando existe)
- **Manifesto:** [`../{base}-manifest.md`](caminho) — índice das fatias e ondas de paralelismo (quando a decomposição tem 2+ fatias)
- **Resumo:** [2-3 linhas sintetizando a feature — o leitor que cair aqui deve
  entender do que se trata sem abrir o SPEC/PRD, mas o SPEC é o contrato e o PRD
  (quando existe) é a fonte autoritativa.]

## Abordagem Técnica

[Decisões de alto nível que guiam a implementação. Cada decisão em 1-2
linhas, com justificativa curta. Não é um romance — é um mapa.]

- [Decisão 1 — ex.: "Autenticação via JWT emitido pelo backend; refresh
  token guardado em HttpOnly cookie. Motivo: evita lidar com OAuth server
  neste MVP."]
- [Decisão 2]
- [Decisão 3]

## Arquivos Afetados

Lista dos arquivos que serão criados ou alterados durante a implementação,
com propósito breve. Marcar `[NOVO]` para criação.

- `src/path/para/arquivo.ts` — [propósito]
- `src/outra/area/modulo.ts` — [propósito] `[NOVO]`
- `tests/feature.spec.ts` — [propósito] `[NOVO]`

## Diagrama de Implementação

[Bloco de código texto mostrando fluxo entre componentes, estrutura de
pastas proposta, ou modelo de dados simplificado. O formato depende do
que for mais útil para esta feature — não há obrigação de tipo específico.]

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ [Componente] │────▶│ [Componente] │────▶│ [Componente] │
│              │     │              │     │   [NOVO]     │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Dependências Novas

Bibliotecas externas que precisam ser adicionadas ao projeto. Incluir
versão quando aplicável.

- `biblioteca-x` (^1.2.0) — [para quê]
- `outra-lib` (^0.5.0) — [para quê]

[Se não há dependências novas, escrever: "Nenhuma dependência nova."]

## Premissas Assumidas

O que a skill presumiu na ausência de informação explícita. O usuário
deve revisar — se uma premissa estiver errada, voltar à skill e ajustar.

- [Premissa 1 — ex.: "Assumido que usuários autenticados têm session
  válida via middleware global."]
- [Premissa 2]

## Contexto Técnico Global

[Origem e resumo do contexto técnico do projeto. Uma das duas formas:]

- **Carregado de:** `./docs/trd.md`
  - Stack: [resumo relevante]
  - Padrões: [resumo relevante]
  - Comando de teste: `[ex.: npm test, pytest, cargo test]` (ou `Sem suíte de testes detectada`)

**OU**, se o TRD não existia:

- **Coletado em mini-modo** (sem TRD no projeto):
  - Stack: [resposta da coleta]
  - Padrões de teste: [resposta]
  - Comando de teste: `[ex.: npm test, pytest, cargo test]` (ou `Sem suíte de testes detectada`)
  - Estrutura dominante: [resposta]
  - Convenções específicas: [resposta]
  - Restrições de ambiente: [resposta]

## Marco Coberto

O marco (milestone) do PRD que **esta fatia** atende. Uma fatia fica contida em
um marco (fatia ⊆ marco); um marco pode ter várias fatias. Sem PRD, escrever
`—` (não há milestones; o rollup cai para as USs/critérios de aceite do SPEC).

- **Marco**: [ID + título do marco no PRD], coberto pela fatia via US[s] [IDs].
- **Outras fatias do mesmo marco** (quando houver): `{base}-{outra-fatia}` — ver
  o manifesto `./.aidev/{base}-manifest.md` para o rollup completo.

## Riscos Técnicos

Pontos de atenção que não justificam abrir um PRD novo mas merecem
registro — impactam execução.

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| [descrição] | Alto/Médio/Baixo | [plano] |
| [descrição] | Alto/Médio/Baixo | [plano] |
```

---

## Regras de preenchimento

- **Autocontido dentro do escopo técnico** — o PLAN é o roteiro da
  implementação, não precisa repetir o PRD. Mas qualquer decisão que altere
  o comportamento descrito no PRD é sinal de que deve voltar ao PRD primeiro.
- **Conciso, não exaustivo** — decisões em 1-2 linhas, não parágrafos.
  Exaustividade mora nas tasks.
- **Seção `Arquivos Afetados` é lista, não narrativa** — uma linha por
  arquivo, com propósito de uma frase.
- **Diagrama é opcional mas útil** — se a feature envolve múltiplos
  componentes, vale 1000 palavras.
- **Premissas existem para serem desafiadas** — não as esconda; a skill
  deve listar tudo que assumiu, e o usuário tem o dever de revisar.
- **Comando de teste é obrigatório quando há suíte** — esse campo é
  consumido pela skill `implementar-task` para rodar linha de base, gate
  de validação e execução seletiva durante o loop de correção. Se o
  projeto não tem suíte de testes, registrar literalmente
  `Sem suíte de testes detectada` (não omitir o campo). A skill `preparar-execucao`
  extrai esse comando do TRD quando existe ou pergunta no mini-modo.
