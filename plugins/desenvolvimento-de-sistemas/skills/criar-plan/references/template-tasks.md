# Template TASKS.md

Estrutura canônica do `TASKS.md` gerado pela skill `criar-plan`. TASKS é o
checklist de execução — cada task é uma unidade de trabalho que entrega
valor em algum nível consumível (usuário, API ou componente). Pareado com
`PLAN.md` no mesmo diretório `./.aidev/{slug}/`.

## Semântica dos campos de controle

**`prd`** — slug do PRD, igual ao usado no `PLAN.md` pareado. Cola entre
tasks e fonte de verdade.

**`plan_status`** — espelha o `status` do `PLAN.md` pareado para facilitar
consulta sem abrir os dois arquivos.

---

## Estrutura geral do arquivo

```markdown
---
prd: <slug-do-prd>
plan_status: rascunho | pronto | em-execucao | concluido
created: YYYY-MM-DD
---

# TASKS: [Título da feature, espelhando o PRD]

## [ ] T01 [P]: [título objetivo da task]
- **USs cobertas:** US01, US02
- **Nível:** usuário | API | componente
- **needs:** —
- **Passos:**
  - [ ] passo 1
  - [ ] passo 2
  - [ ] passo 3
- **Validação:**
  - [ ] critério 1 (método adaptado ao tipo da task)
  - [ ] critério 2

## [ ] T02: [título]
- **USs cobertas:** US03
- **Nível:** API
- **needs:** T01
- **Passos:**
  - [ ] passo 1
  - [ ] passo 2
- **Validação:**
  - [ ] critério 1

[... demais tasks ...]
```

---

## Anatomia de uma task

### `[ ] TNN: título`

O marcador `[ ]` no título representa **conclusão geral da task**. Fecha
(`[X]`) quando todos os passos e todas as validações também estão com
`[X]`. Enquanto qualquer passo ou validação estiver aberto, o marcador
geral permanece `[ ]`.

IDs são sequenciais (`T01`, `T02`, `T03`...) e **estáveis** — uma vez
atribuídos, nunca mudam em edição ou reconciliação. Se uma task é removida,
seu ID **fica vago**; nunca reutilizar.

### `USs cobertas`

Lista dos IDs de User Story do PRD que esta task entrega (total ou
parcialmente). Pelo menos uma US deve ser coberta — task sem US associada
é sinal de desalinhamento com o PRD.

### `Nível`

Nível de valor entregue. Opções em ordem de preferência (maior → menor):

- **usuário** — entrega interação completa para o usuário final. Ex.:
  "usuário consegue fazer login e cair no dashboard".
- **API** — entrega endpoint, comando CLI ou outra interface externa
  testável de fora. Ex.: "POST /api/login aceita credenciais válidas e
  retorna token".
- **componente** — entrega módulo ou função interno, usável por outras
  tasks mas não diretamente por usuário/API. Ex.: "função `hashPassword()`
  com algoritmo X e teste unitário".

Preferir sempre o nível mais alto viável. Task de nível `componente` só é
aceitável quando o slice vertical seria artificial (refatoração, bootstrap,
infra).

### `needs`

IDs de outras tasks que precisam estar com `[X]` antes desta começar. Ex.:
`T03, T05`. Usar `—` quando a task não tem dependências.

**Sinalizar cadeia linear longa**: se `T04` precisa de `T03`, que precisa
de `T02`, que precisa de `T01`, a skill alerta o usuário para revisar se
cabe verticalizar. Cadeia linear > 3 costuma ser sinal de horizontalização
disfarçada.

### `[P]` — marcador de paralelismo

Tasks marcadas com `[P]` no título podem ser executadas em paralelo com
outras tasks `[P]` sem `needs:` conflitantes. O marcador é inferido
automaticamente pelo `criar-plan`:

- Task sem `needs:` → candidata a `[P]`
- `criar-plan` cruza os `Arquivos Afetados` do PLAN para detectar sobreposição entre candidatas
- Sobreposição detectada → `needs:` automático aponta para a task conflitante; `[P]` não é aplicado
- Sem sobreposição → `[P]` aplicado no título

Nunca adicionar ou remover `[P]` manualmente sem revisar dependências.

### `Passos`

Checklist dos sub-passos concretos da execução. Cada item é uma ação
específica — comando para rodar, arquivo para editar, teste para escrever.
Granularidade: passo deve ser executável em "uma sentada", sem pausa para
decisões.

Passos são marcados `[X]` conforme são executados (por quem executa, não
por esta skill).

### `Validação`

Checklist dos critérios que comprovam que a task foi entregue corretamente.
**Adaptar ao tipo da task**:

| Tipo da task | Como validar |
|--------------|--------------|
| **Código novo** | teste unitário + teste de integração, comando para rodar (ex.: `npm test -- --grep "login"`) |
| **Refatoração** | suíte existente verde, nenhuma regressão no comportamento observável |
| **Infra/config** | smoke test ou health check (ex.: `curl /health` retorna 200) |
| **Documento/schema** | revisão visual + lint (`npm run lint`) |

Evitar validação genérica tipo "verificar que funciona" — cada critério
deve ser **executável e objetivo**.

Validações também são marcadas `[X]` conforme verificadas (externamente à
skill).

---

## Regras de preenchimento

- **Título em verbo + substantivo** — "Implementar endpoint de login", não
  "Login". Descreve ação, não coisa.
- **Toda task tem pelo menos 1 passo e 1 validação** — task sem passos é
  vaga; task sem validação é "confia no Jeová".
- **Nunca inventar US** — se a task não bate com nenhuma US do PRD, é
  sinal de que o PRD está incompleto ou a task está fora do escopo. Ajustar
  um dos dois antes de gravar.
- **Preservar `[X]` em edição e reconciliação** — nunca apagar conclusões.
  Se uma mudança invalida uma conclusão, pedir decisão ao usuário, não
  sobrescrever silenciosamente.
- **Novas tasks vão para o fim** — em modo edição e reconciliação, IDs
  sequenciais continuam do maior já existente. Não inserir no meio.
