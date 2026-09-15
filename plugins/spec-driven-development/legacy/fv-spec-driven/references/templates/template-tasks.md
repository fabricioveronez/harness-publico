# Template TASKS.md

O checklist de execução. Cada task entrega valor em algum nível consumível e
**referencia por ID os critérios de aceite que ela prova**.

---

```markdown
---
type: tasks
title: [Título da feature, espelhando o SPEC]
description: [uma frase resumindo o checklist]
resource: [slug-do-prd | none]
tags: [sdd, tasks]
created: YYYY-MM-DD
plan_status: rascunho | pronto | em-execucao | concluido
prd: [slug-do-prd | none]
---

# TASKS: [Título da feature]

Ver [`PLAN.md`](PLAN.md) para a abordagem e [`SPEC.md`](SPEC.md) para o contrato.

## [ ] T01 [P]: [título objetivo, verbo + substantivo]
- **USs cobertas:** US01, US02
- **Nível:** usuário | API | componente
- **needs:** —
- **Passos:**
  - [ ] [ação concreta: arquivo a editar, comando a rodar]
  - [ ] [ação concreta]
- **Validação:**
  - [ ] CA01 — `npm test -- tests/sync.spec.ts`
  - [ ] CA02

## [ ] T02: [título]
- **USs cobertas:** US03
- **Nível:** API
- **needs:** T01
- **Passos:**
  - [ ] [ação]
- **Validação:**
  - [ ] CA03
```

---

## Anatomia

### `[ ] TNN: título`

O marcador do título é a **conclusão geral**: fecha só quando todos os passos e
todas as validações estão `[X]`. IDs são sequenciais e **estáveis** — task
removida deixa o ID vago; nunca reutilize.

### `USs cobertas`

IDs de US que esta task entrega. Pelo menos uma. Task sem US é sinal de
desalinhamento com o contrato.

### `Nível`

Valor entregue, do maior para o menor: **usuário** (interação completa) > **API**
(endpoint/comando testável de fora) > **componente** (módulo interno). Prefira
sempre o mais alto viável. `componente` só quando o slice vertical seria
artificial — refatoração, bootstrap, infra.

O valor também define o tipo do commit semantic (tabela na seção 5 de
`heuristicas-execucao.md`).

### `needs`

IDs de tasks que precisam estar `[X]` antes desta. `—` quando não há.

Cadeia linear de mais de 3 (`T04`←`T03`←`T02`←`T01`) costuma ser horizontalização
disfarçada — sinalize ao usuário para revisar se cabe verticalizar.

### `[P]`

Inferido pelo modo Preparar, nunca escrito à mão: task sem `needs` é candidata;
se duas candidatas tocam o mesmo arquivo, a segunda perde o `[P]` e ganha `needs`
apontando a primeira. `[P]` e `needs` preenchido são mutuamente exclusivos.

### `Passos`

Ações concretas, executáveis "em uma sentada", sem pausa para decisão. Se um passo
exige decidir regra de negócio, o contrato está incompleto — isso vira pausa
`lacuna-spec`, não um passo.

### `Validação`

**Referencia os critérios do SPEC pelo ID**, não reescreve o critério em prosa. O
nível e o alvo já estão declarados na tabela §5a; repetir aqui cria duas fontes
para a mesma verdade e elas divergem na primeira edição.

Quando ajuda, anote o comando ao lado do ID (`- [ ] CA01 — npm test -- x.spec.ts`).

Toda task precisa referenciar **pelo menos um** `CA`. Task sem critério é task sem
prova — `scripts/cobertura.py` acusa.

---

## Regras de preenchimento

- **Título em verbo + substantivo** — "Implementar endpoint de cards", não "Cards".
- **Toda task tem ≥1 passo e ≥1 validação.** Sem passos é vaga; sem validação é fé.
- **Preserve `[X]` em edição e reconciliação.** Se uma mudança invalida uma
  conclusão, pergunte — não sobrescreva.
- **Novas tasks vão para o fim**, com ID continuando do maior existente.
- **Notas de pausa são acumulativas** e ficam no fim do bloco da task.
