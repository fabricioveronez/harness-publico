# Template PLAN.md

A abordagem técnica — o "como" para o "o quê" do SPEC. Inclui a **estratégia de
teste**, porque testar é parte de como se constrói, e um artefato separado só para
isso duplicaria a fronteira sem ganho.

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

# PLAN: [Título da feature]

## Referências

- **SPEC:** [`SPEC.md`](SPEC.md) — o contrato que este plano realiza
- **PRD:** [`../../docs/prds/NNN-slug.md`](caminho) — quando existe
- **Manifesto:** [`../{base}-manifest.md`](caminho) — quando há 2+ fatias
- **Resumo:** [2-3 linhas: quem cair aqui entende do que se trata sem abrir o SPEC]

## Abordagem Técnica

Decisões de alto nível, 1-2 linhas cada, com justificativa curta. É um mapa, não
um romance.

- [decisão 1 — o quê e por quê]
- [decisão 2]

## Arquivos Afetados

A disjunção desta lista entre fatias irmãs é o que habilita o paralelismo — se
duas fatias aparecem aqui com o mesmo arquivo, elas não rodam na mesma onda.

- `src/caminho/arquivo.ts` — [propósito]
- `src/outro/modulo.ts` — [propósito] `[NOVO]`
- `tests/feature.spec.ts` — [propósito] `[NOVO]`

## Estratégia de Teste

Como o contrato do SPEC vira prova. Os critérios (`CA01`...) declaram o alvo
individual; esta seção declara o desenho em volta deles.

- **Níveis em uso:** [ex.: unit para regras puras, integração para o poller, e2e
  só para o fluxo de aprovação]
- **Fixtures / seeds:** [o que precisa existir para os testes rodarem — mock de
  API, banco semeado, servidor de teste]
- **Fora da automação, e por quê:** [ex.: CA04 é inspeção visual do board; o custo
  de automatizar não se paga nesta fatia]
- **Dependências de teste novas:** [libs, containers, serviços fake]

## Diagrama de Implementação

[Fluxo entre componentes, estrutura de pastas, ou modelo de dados. Opcional —
mas se a feature cruza vários componentes, vale mil palavras.]

## Dependências Novas

- `biblioteca-x` (^1.2.0) — [para quê]

[Se não houver: "Nenhuma dependência nova."]

## Premissas Assumidas

- [premissa 1 — existe para ser desafiada; não esconda nenhuma]

## Contexto Técnico Global

- **Carregado de:** `./docs/trd.md`  **ou**  **Coletado em mini-modo** (sem TRD)
  - Stack: [resumo]
  - Padrões de teste: [resumo]
  - **Comando de teste:** `[ex.: npm test]` (ou `Sem suíte de testes detectada`)
  - Estrutura dominante: [onde mora código, onde moram testes]
  - Convenções específicas: [error handling, formato de log]
  - Restrições de ambiente: [CI, deploy, feature flags]

## Marco Coberto

- **Marco:** [ID + título do marco no PRD], via US[s] [IDs]. Sem PRD: `—`.
- **Outras fatias do mesmo marco:** `{base}-{outra}` — ver o manifesto.

## Riscos Técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| [descrição] | Alto/Médio/Baixo | [plano] |
```

---

## Regras de preenchimento

- **`Comando de teste` é obrigatório.** O modo Implementar o consome para a linha
  de base e para o filtro seletivo, e quebra sem ele. Sem suíte, escreva
  literalmente `Sem suíte de testes detectada` — ausência declarada é informação;
  campo faltando é bug.
- **`Arquivos Afetados` é lista, não narrativa.** Uma linha por arquivo. É insumo
  de três decisões automáticas: `[P]` de task, `needs` de fatia e escopo do commit.
- **Conciso.** Decisões em 1-2 linhas; exaustividade mora nas tasks.
- **Decisão que altera comportamento não mora aqui** — volta ao SPEC (ou ao PRD).
