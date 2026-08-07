# Template — Relatório de validação

Estrutura canônica do relatório emitido pela `validar-implementacao` ao fim do
ciclo. O relatório é **inline** (não grava arquivo por padrão) — o registro
durável do fechamento é a promoção de `status` no frontmatter do bundle.

---

```markdown
# Validação — [Título da feature] ({slug})

**Fonte de verdade:** [PRD `NNN-slug` | SPEC (projeto sem PRD)]
**Estado da implementação:** [todas as tasks `[X]` | validação parcial (N tasks pendentes)]
**Linha de base de testes:** [verde | vermelha — parar antes de validar coerência]

## Cobertura de US

| US    | Coberta? | Rules honradas | Edge cases | Critérios §5a |
|-------|----------|----------------|------------|---------------|
| US01  | ✓        | 2/2            | 1/1        | OK            |
| US02  | ✓        | 1/1            | 2/2        | verificação manual sugerida |
| US03  | ✗        | —              | —          | —             |

## Critérios de aceite (§5a)

| Critério | Classe | Resultado |
|----------|--------|-----------|
| [ex.: confirmação responde < 2s] | executável | OK |
| [ex.: fluxo X para persona Y]     | manual     | verificação manual sugerida |

## Divergências

| # | Onde | Contrato diz | Código faz | Classe | Tratamento |
|---|------|--------------|------------|--------|------------|
| D1 | US01/Rule | campo `sobrenome` | campo `apelido` | pequena | SPEC ajustado (nominal) |
| D2 | US03 | entregar reset de senha | não implementado | grande | gap de código → `implementar-task` |
| D3 | US02/Rule | exige 2FA (código) | ausente no PRD | grande | perguntado ao usuário → `escrever-prd` + reprojetar |

## Veredito

- **Divergências pequenas ajustadas:** N
- **Divergências grandes em aberto:** N
- **Fechamento:** [`concluido` — status promovido em SPEC/PLAN/TASKS (e PRD) |
  bloqueado — pendências acima antes de fechar]
- **Próxima ação sugerida:** [1 linha]
```

---

## Regras de preenchimento

- **US não coberta é sempre divergência grande** — reportar, nunca fechar por
  cima.
- **Cada divergência traz classe e tratamento** — o leitor precisa saber por que
  foi ajustada automaticamente ou por que voltou ao usuário/outra skill.
- **Fechamento só com zero divergência grande em aberto** — o veredito
  `concluido` exige a coluna "grandes em aberto" zerada.
- **Não duplicar o contrato** — o relatório referencia US/Rule por ID; não copia
  o texto do SPEC/PRD.
