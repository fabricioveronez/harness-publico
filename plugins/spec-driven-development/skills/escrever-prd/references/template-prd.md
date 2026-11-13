# Template PRD

Estrutura padrão do PRD de feature. O documento cobre comportamento, regra de negócio e
razão específica da feature. Realização técnica e constraints globais vivem no TRD, ADRs e
PLAN/TASKS.

## Fronteira

| Conteúdo | Onde mora |
|---|---|
| Comportamento, regra, edge case e forma de produto | PRD |
| Limiar específico com razão de negócio | PRD (§5a) |
| Métrica de sucesso da feature | PRD (§5b) |
| Stack, modelo de dados e mecanismo técnico | PLAN/TRD |
| Decisão arquitetural durável | ADR |
| NFR global | TRD |
| Decomposição e ordem de implementação | PLAN/TASKS |

## Controle

- `rascunho` — em criação ou revisão.
- `pronto` — aprovado para planejamento.
- `em-progresso` — execução ativa.
- `concluido` — todos os critérios `ACxx` aprovados; documento imutável.
- `depends_on` lista apenas PRDs dos quais esta feature depende diretamente.
- `origin_epic` e `origin_capability` são proveniência opcional, nunca dependência.

```markdown
---
artifact_type: prd
prd_number: "NNN"
status: rascunho | pronto | em-progresso | concluido
priority: baixa | média | alta | crítica
created: YYYY-MM-DD
issue: "#número (opcional)"
depends_on: []
references: []
# Incluir os dois campos seguintes somente quando a origem for explícita:
# origin_epic: "E001"
# origin_capability: "C01"
---

# PRD NNN: [Título descritivo da feature]

## 1. Contexto

- **Produto/área:** [onde a feature se insere]
- **Estado atual:** [o que é possível hoje]
- **Problema:** [dor, público afetado e impacto]

[Contexto técnico fica no TRD; aqui cabe apenas referência quando relevante.]

## 2. Solução proposta

### Visão de produto

- [comportamento e valor, não mecanismo técnico]

### Decisões de produto

1. [decisão com justificativa]

### Fora do escopo

- [exclusão e motivo]

## 3. Funcionalidades

### US01: [Título]

Como [persona], quero [ação], para [benefício].

**Rules:**
- [regra de negócio ou comportamento]

**Edge cases:**
- [situação anômala] → [comportamento esperado]

[Repetir para cada funcionalidade. IDs são estáveis; detalhe técnico pertence ao PLAN.]

## 4. Fluxo de negócio

[Diagrama de jornada ou processo somente quando decisões e ramificações de negócio não
ficarem claras no texto. Omitir a seção quando não for necessária.]

```text
Solicitação
   │
   ▼
Regra satisfeita?
   ├── sim ──▶ Resultado esperado
   └── não ──▶ Tratamento de negócio
```

## 5. Critérios de aceite

### 5a. Critérios da feature

- [ ] **AC01 — [critério observável ou limiar específico]**
  - **Razão de negócio:** [por que importa, ou —]
  - **Como verificar:** [verificação externa]

[IDs `ACxx` são estáveis. Marcar o item somente após aprovação. Todos precisam estar
marcados para `status: concluido`.]

### 5b. Métricas de sucesso

| Métrica | Baseline (fonte) | Meta | Prazo | Mín. aceitável | Responsável |
|---|---|---|---|---|---|
| [nome] | [valor e origem, ou A levantar] | [alvo] | [data/período] | [limiar] | [papel/pessoa] |

## 6. Riscos e dependências

| Risco | Impacto | Mitigação | Status |
|---|---|---|---|
| [risco de negócio, produto ou adoção] | Alto/Médio/Baixo | [mitigação] | Pendente/Monitorando/Mitigado |

**Dependências:**

| Dependência | Tipo | Status | Impacto se bloqueada |
|---|---|---|---|
| [PRD, equipe ou decisão de produto] | Interna/Externa | [estado] | [critérios afetados] |

[Dependência técnica global pertence ao TRD.]

## 7. Referências

- [Recurso](link) — [relevância]

## 8. Registro de decisões

- **YYYY-MM-DD:** [decisão de produto]. Motivo: [justificativa].
```

## Compatibilidade com PRDs legados

Um PRD existente que contenha `## 6. Milestones` permanece no formato anterior. Ao editá-lo,
preserve a seção, os IDs, checklists, aprovadores e a regra de conclusão histórica; não aplique
retroativamente a renumeração deste template sem pedido explícito de migração.
