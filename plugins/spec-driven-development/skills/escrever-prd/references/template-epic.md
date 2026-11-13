# Template Epic

Estrutura canônica da visão de alto nível que coordena research e planejamento sem antecipar
PRDs. O documento descreve resultados e capacidades candidatas; comportamento detalhado de
feature pertence a PRDs posteriores.

```markdown
---
artifact_type: epic
epic_number: "E###"
status: explorando | planejada | em-progresso | concluida
priority: baixa | média | alta | crítica
created: YYYY-MM-DD
references: []
---

# Epic E###: [Resultado ou direção]

## 1. Direção

[Qual mudança ampla se pretende produzir e por que ela importa.]

## 2. Problema e público

- **Situação atual:** [o que acontece hoje]
- **Público afetado:** [quem enfrenta o problema]
- **Impacto:** [custo, limitação ou oportunidade]

## 3. Evidências

| Evidência | Fonte | Consultada em | Implicação |
|---|---|---|---|
| [fato, sinal ou ausência conhecida] | [link, documento ou origem] | [YYYY-MM-DD ou —] | [o que muda na direção] |

[Não inventar evidência. Uma premissa deve estar marcada; uma lacuna relevante vai para
Questões abertas.]

## 4. Resultados e sucesso

### Resultado esperado

[O que deverá ser verdadeiro quando a Epic produzir valor.]

### Métricas

| Métrica | Baseline (fonte) | Meta | Prazo | Mín. aceitável | Responsável |
|---|---|---|---|---|---|
| [nome] | [valor e origem, ou A levantar] | [alvo] | [data/período] | [limiar] | [papel/pessoa] |

## 5. Fronteira

### Dentro

- [resultado ou capacidade considerada]

### Fora

- [exclusão e motivo]

## 6. Capacidades candidatas

| ID | Capacidade | Valor esperado | Clareza | Próximo passo |
|---|---|---|---|---|
| C01 | [capacidade, não solução detalhada] | [contribuição ao resultado] | clara \| research \| spike \| design \| decisão \| aberta | [ação coerente com a clareza] |

[Capacidade candidata não é PRD. Não escrever User Stories, rules, edge cases ou critérios
de aceite de feature nesta seção.]

## 7. Milestones de resultado

### M01: [Resultado observável]

- [ ] **Alcançado**
- **Resultado:** [o que passa a ser verdadeiro]
- **Evidência:** [como se observará o alcance]
- **Capacidades relacionadas:** C01, C02

[Repetir apenas para resultados relevantes. Não usar fases técnicas, sprints, documentos ou
PRDs como milestones.]

## 8. Sequenciamento

| Antes | Depois | Motivo |
|---|---|---|
| [capacidade ou decisão] | [capacidade ou resultado] | [dependência de produto ou aprendizado] |

[Registrar apenas relações conhecidas. Não decompor em tarefas nem impor ordem técnica.]

## 9. Decisões

| Data | Decisão | Justificativa | Estado |
|---|---|---|---|
| YYYY-MM-DD | [decisão de produto ou direção] | [por que] | decidida \| premissa |

## 10. Questões abertas

| ID | Tipo | Questão | O que destrava |
|---|---|---|---|
| Q01 | research \| spike \| design \| decisão | [pergunta] | [capacidade, milestone ou transição afetada] |

## 11. Referências

- [Recurso](link) — [relevância]
```
