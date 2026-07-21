---
name: validar-implementacao
description: >
  Fecha o ciclo spec-driven validando a implementação contra os documentos e
  ajustando o drift. Carrega o `SPEC.md` do bundle `./.aidev/{slug}/` (o
  contrato: US Rules, Edge cases, critérios de aceite §5a) e, quando existe, o
  PRD como fonte de verdade; confere se o código entregue é coerente com o
  contrato — cada US coberta, cada Rule/Edge case honrada, cada critério de
  aceite verificável passando. Ao encontrar divergência, **avalia primeiro o
  impacto e o tamanho**: divergência pequena (textual/local) ela ajusta
  automaticamente no documento, com o PRD como autoridade quando existe;
  divergência grande (comportamento que contradiz o contrato, US não entregue,
  mudança que alteraria o PRD) ela **pausa e pergunta ao usuário** antes de
  qualquer ajuste. Rework estrutural de PLAN/TASKS é delegado à
  `preparar-execucao`; gap de código é reportado (e pode voltar à
  `implementar-task`). Ao concluir sem divergência aberta, promove o `status`
  para `concluido` no frontmatter do bundle (e o PRD para `concluido` quando
  existe). Use quando o usuário quiser validar a implementação, fechar o ciclo,
  verificar se o código bate com a spec/PRD, detectar e ajustar drift entre
  documento e código, auditar a coerência da entrega, ou mencionar "validar
  implementação", "fechar a feature", "checar drift", "conferir o que foi feito
  contra a spec", "finalizar o ciclo spec-driven".
---

# Validar Implementação

Última peça do fluxo spec-driven. Confere se o que foi **construído** é coerente
com o que foi **especificado**, ajusta o drift entre documento e código, e fecha
o ciclo promovendo o `status` para `concluido`.

A skill parte do bundle `./.aidev/{slug}/` gerado por `preparar-execucao` e
implementado por `implementar-task`. O `SPEC.md` é o contrato; o PRD, quando
existe, é a fonte de verdade — em conflito, **o PRD vence**.

## Papel no fluxo spec-driven

O fluxo é: `escrever-prd` (opcional) → `preparar-execucao` → `implementar-task`
→ **`validar-implementacao`**. Esta é a peça de fechamento. Assume que
`implementar-task` já rodou a cadeia de tasks (idealmente todas `[X]`) e que o
bundle está no disco.

Diferença em relação ao gate final do `implementar-task`: aquele reporta o
estado das tasks e dos critérios; **esta** julga a coerência da entrega contra o
contrato, ajusta drift e promove o status. Nenhuma outra skill promove para
`concluido`.

## Princípios

1. **Autoridade: PRD > SPEC > código.** Quando há PRD, ele é a fonte de verdade;
   o SPEC é a projeção dele; o código realiza o SPEC. Um conflito se resolve
   sempre a favor do documento de maior autoridade — nunca "consertando" o
   contrato para bater com um código que se desviou.
2. **Avaliar antes de agir.** Toda divergência é primeiro **classificada** por
   impacto e tamanho. Só depois se decide entre ajustar automaticamente (pequena)
   ou perguntar ao usuário (grande). Nunca ajustar um documento sem antes medir o
   que aquele ajuste significa.
3. **Cada skill é dona do seu artefato.** Esta skill ajusta a **coerência
   textual** do SPEC (e reporta o resto). **Não** reestrutura PLAN/TASKS — isso é
   da `preparar-execucao`. **Não** edita o PRD — isso é do `escrever-prd`. **Não**
   reimplementa código — isso é da `implementar-task`. Quando o ajuste certo mora
   noutro artefato, ela **delega**.
4. **Fechar é terminal.** Promover para `concluido` só acontece sem divergência
   grande em aberto. Fechamento com pendência é proibido.

## Entrada

`$ARGUMENTS` — se fornecido, referência ao slug do bundle (número/slug do PRD,
slug da feature, ou caminho em `./.aidev/`). Se ausente:

- **Único diretório em `./.aidev/`** → autodetecta.
- **Múltiplos** → listar e pedir qual.
- **Nenhum** → abortar sugerindo `preparar-execucao`/`implementar-task`.

## Fluxo de Execução

### 1. Carregar contrato e contexto

1. Resolver o slug e ler o bundle `./.aidev/{slug}/` — `SPEC.md` (contrato),
   `PLAN.md` (arquivos afetados, comando de teste), `TASKS.md` (estado `[X]`).
2. Ler o campo `prd:` do `SPEC.md`. Quando aponta um slug, carregar o PRD
   (`./docs/prds/{prd}.md`) como fonte de verdade. Quando `none`, o SPEC é a
   fonte de verdade.
3. Carregar o TRD (`./docs/trd.md`) quando o PLAN o referencia — contexto de
   convenções para julgar coerência técnica.

### 2. Pré-condições

1. **Tasks pendentes** — se há tasks `[ ]` não bloqueadas, avisar que a
   implementação não terminou e sugerir `implementar-task` antes. O usuário pode
   pedir validação parcial mesmo assim (registra-se como validação parcial).
2. **Linha de base verde** — rodar o `Comando de teste:` do PLAN. Vermelho
   pré-existente contamina o julgamento: reportar e parar antes de validar
   coerência.

### 3. Validar coerência código ↔ contrato

Para cada **US** do `SPEC.md`:

- **Cobertura** — existe código que entrega a US? (cruzar com "Arquivos
  Afetados" do PLAN e "USs cobertas" das tasks).
- **Rules** — cada Rule está honrada no comportamento implementado?
- **Edge cases** — cada Edge case tem tratamento correspondente no código?
- **Critérios de aceite (§5a)** — executar os verificáveis (heurística da
  `implementar-task`, seção 3 do `heuristicas-execucao.md`); listar os manuais.

Registrar cada desvio encontrado como um item de divergência (US/Rule/critério,
o que o contrato diz, o que o código faz).

### 4. Validar coerência SPEC ↔ PRD (só quando há PRD)

O SPEC é projeção do PRD. Conferir que a projeção continua fiel: US, Rules, Edge
cases e critérios do SPEC refletem o PRD atual. Divergência aqui significa que o
SPEC envelheceu em relação à fonte de verdade — candidato a reprojeção via
`preparar-execucao`.

### 5. Classificar e tratar cada divergência

**Primeiro avaliar impacto e tamanho** (ver
`references/heuristicas-validacao.md`), depois agir:

- **Pequena** (textual/local, não muda o contrato): ex.: o SPEC nomeia um
  detalhe que o código chama diferente; um critério redigido de forma ambígua
  mas satisfeito; nota faltando. → **Ajustar automaticamente** o documento para
  refletir a realidade, respeitando a autoridade (se o texto veio do PRD, ver
  regra abaixo). Registrar o ajuste no relatório.
- **Grande** (semântica/estrutural): comportamento implementado contradiz uma
  Rule/Edge case; US não entregue; critério de aceite falhando; ajuste que
  mudaria o PRD; SPEC muito defasado do PRD. → **Pausar e perguntar ao usuário**
  antes de qualquer alteração, apresentando a divergência, o impacto e as opções
  (abaixo). Nunca ajustar silenciosamente uma divergência grande.

**Direção do ajuste, pela autoridade:**

- Código desviou do contrato (contrato tem razão) → **gap de código**: reportar;
  a correção é reimplementar via `implementar-task` (esta skill não edita código).
- Contrato (SPEC) desviou da realidade e a realidade está correta, e **não há
  PRD** ou o ponto não vem do PRD → ajustar o `SPEC.md` (pequena) ou pedir aval
  (grande).
- Divergência envolve algo que o **PRD** define → o PRD é autoridade: o ajuste
  correto é no PRD (via `escrever-prd`) e depois reprojetar o SPEC via
  `preparar-execucao`. Sempre **grande** → perguntar.
- Divergência é **estrutural em PLAN/TASKS** (nova task, task obsoleta) →
  **delegar** à `preparar-execucao` (modo reconciliação). Esta skill não
  reestrutura o bundle.

### 6. Fechamento

Só quando **não há divergência grande em aberto** (as pequenas foram ajustadas,
as grandes foram resolvidas pelo usuário ou delegadas e sanadas):

1. Promover `status: concluido` no frontmatter de `SPEC.md`, `PLAN.md`
   (`status`) e `TASKS.md` (`plan_status`). Editar **apenas o frontmatter**.
2. Quando há PRD, promover o PRD para `status: concluido` (via edição de
   frontmatter — a única transição de status do PRD que esta skill faz).
3. O bundle **permanece no lugar** (`./.aidev/{slug}/`), congelado pelo status
   como registro do que foi construído.

### 7. Relatório

Emitir o relatório de validação conforme `references/template-relatorio.md`:
cobertura de US, resultado dos critérios, divergências (com classificação e
tratamento dado), e o veredito de fechamento (`concluido` ou pendências).

## Saída ao usuário (formato curto e fixo)

```
Estado: <coerente e fechado | divergências tratadas | pausado por divergência grande | validação parcial>
Cobertura: <N/M USs cobertas>
Divergências: <pequenas ajustadas: N | grandes em aberto: N>
Próxima ação sugerida: <1 linha>
```

Sem narração extensa, sem emoji.

## Fora do escopo

Esta skill **não**:

- Edita código para sanar gap de implementação (papel de `implementar-task`).
- Reestrutura PLAN/TASKS (papel de `preparar-execucao`).
- Edita o corpo do PRD (papel de `escrever-prd`) — só promove o `status` do PRD
  para `concluido` no fechamento.
- Ajusta divergência **grande** sem confirmação explícita do usuário.
- Move ou apaga o bundle — o fechamento é por `status`, no lugar.

## Templates e referências

- `references/heuristicas-validacao.md` — como classificar divergência por
  impacto e tamanho (pequena vs grande) e a regra de direção do ajuste pela
  autoridade PRD > SPEC > código.
- `references/template-relatorio.md` — estrutura canônica do relatório de
  validação.
