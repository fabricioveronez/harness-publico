# Template SPEC.md

Estrutura canônica do `spec.md` gerado pela skill `preparar-execucao`. O SPEC é o
**contrato comportamental orientado à IA** — o que a implementação precisa cumprir e
a validação precisa checar, em forma enxuta e testável. É o documento que
`implementar-task` e `validar-implementacao` carregam como **contexto primário**.
Pareado com `PLAN.md` e `TASKS.md` no mesmo diretório `./.aidev/{slug}/`.

## Por que o SPEC existe (e o que ele NÃO é)

O PRD é um documento de **leitura humana**: contexto, visão de produto, métricas,
riscos, decisões. Carregá-lo inteiro na hora de codar/validar pesa o contexto com
material que não é contrato executável. O SPEC extrai só o **contrato**: as regras
de comportamento e os critérios de aceite. Quando existe PRD, o SPEC é uma
**projeção** dele — o PRD continua a fonte de verdade e vence em conflito; a IA abre
o PRD **sob demanda** apenas quando precisa do *porquê* de uma regra. Quando **não há
PRD** (projeto pequeno), o SPEC é escrito direto e é a própria fonte de verdade.

Fronteira — o que **não** entra no SPEC (vive no PRD, quando existe):

| Conteúdo | Onde mora |
|---|---|
| US Rules, Edge cases, critérios de aceite §5a | **SPEC** |
| Premissas assumidas ao projetar/autorar | **SPEC** |
| Contexto narrativo, visão/decisões de produto | PRD |
| Métricas de sucesso (§5b, baseline→meta) | PRD |
| Riscos de negócio, dependências de entrega | PRD |
| Registro de decisões de produto, milestones | PRD |
| Realização técnica (stack, arquitetura, "como") | PLAN / TRD / ADR |

## Formato: Open Knowledge Format (OKF)

O trio `spec`/`plan`/`tasks` segue o **OKF**: markdown com YAML frontmatter, onde o
único campo **obrigatório** é `type`. Todos os outros campos são **convenção desta
skill** — mantidos para rastreabilidade e ciclo de vida, não por exigência do
formato. Cross-links entre documentos são links markdown comuns.

## Semântica dos campos

**`type`** (OKF, obrigatório) — `spec`. Roteia/filtra o concept.

**`resource`** (OKF, recomendado) — asset de origem: o slug do PRD projetado
(ex.: `003-autenticacao-oauth`) ou `none` em projeto sem PRD.

**`prd`** (convenção) — slug do PRD que este SPEC projeta, ou `none`. Cola de
rastreabilidade; igual ao usado no `PLAN.md`/`TASKS.md` pareados.

**`status`** (convenção) — ciclo de vida, espelhando o PLAN:
`rascunho | pronto | em-execucao | concluido`. Vira `concluido` no fechamento
(via `validar-implementacao`), congelando o SPEC como registro do que foi construído.

**`created`** (convenção) — data (YYYY-MM-DD) da primeira geração. Não muda em edições.

---

```markdown
---
type: spec
title: [Título da feature, espelhando o PRD quando existe]
description: [uma frase resumindo o contrato desta feature]
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
- [Regra de negócio ou comportamento esperado]
- [Limite, restrição ou condição]

**Edge cases:**
- [Situação anômala] → [comportamento esperado]
- [Situação anômala] → [comportamento esperado]

### US02: [Título objetivo]

Como [persona], quero [ação], para [benefício].

**Rules:**
- [Regra de negócio ou comportamento esperado]

**Edge cases:**
- [Situação anômala] → [comportamento esperado]

[Repetir para cada US. Cada US tem pelo menos uma Rule e um Edge case. IDs de US
(US01, US02...) são estáveis e — quando há PRD — iguais aos do PRD, pois tasks e
validação referenciam por esses IDs.]

## Critérios de Aceite

Critérios funcionais e não-funcionais **específicos da feature**, cada um como
limiar observável e testável. NFR específico da feature (tempo de resposta,
disponibilidade) entra quando tem razão de negócio.

| Critério | Como verificar (observável) |
|----------|-----------------------------|
| [ex.: confirmação de pagamento responde < 2s] | [como testar de fora] |
| [ex.: fluxo X funciona para persona Y] | [como testar] |

## Premissas

O que a skill presumiu ao projetar (do PRD) ou autorar (sem PRD). O usuário revisa;
premissa errada volta à skill para ajuste.

- [Premissa 1]
- [Premissa 2]

## Referências

Cross-links para os documentos de contexto, carregados **sob demanda**:

- PRD: [`../../docs/prds/NNN-slug.md`](caminho) — fonte de verdade (quando existe)
- TRD: [`../../docs/trd.md`](caminho) — contexto técnico global (quando existe)
- ADRs: [`../../docs/adrs/NNN-slug.md`](caminho) — decisões que embasam o contrato
```

---

## Regras de preenchimento

- **Só contrato** — se um item não é Rule, Edge case, critério de aceite ou premissa,
  ele não pertence ao SPEC. Contexto e "porquê" ficam no PRD (referenciado).
- **Testável, não vago** — critério como "deve funcionar bem" não é aceitável;
  reformular até virar limiar observável. Igual ao rigor do PRD §5a.
- **Projeção fiel** — quando há PRD, não inventar Rule/Edge case que não esteja no
  PRD; se o PRD estiver incompleto, marcar a premissa e sinalizar para voltar ao
  `escrever-prd`. Em conflito, PRD vence.
- **IDs estáveis** — US01, US02... não mudam depois de atribuídos.
- **Cross-links, não cópia** — referenciar PRD/TRD/ADR por link; nunca colar o
  conteúdo deles no SPEC (isso reintroduz o peso de contexto que o SPEC resolve).
- **Autorado direto (sem PRD)** — em projeto pequeno, `resource: none` e `prd: none`;
  o SPEC é a fonte de verdade e o único registro do comportamento pretendido.
