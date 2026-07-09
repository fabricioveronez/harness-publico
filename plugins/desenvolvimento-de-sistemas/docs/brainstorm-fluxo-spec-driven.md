# Brainstorm — Fluxo de desenvolvimento spec-driven

Documento de registro do brainstorm realizado para definir um fluxo próprio de desenvolvimento spec-driven, integrado ao marketplace de plugins. Nenhuma skill será criada a partir deste documento — ele serve como referência para quando a implementação for iniciada.

---

## 1. Contexto

### 1.1 Objetivo do brainstorm
Definir um fluxo de desenvolvimento spec-driven próprio que integre as skills já existentes no marketplace (`plugins/desenvolvimento-de-sistemas/`) com as novas fases necessárias (PLAN, TASKS, IMPLEMENT, VALIDATE) para cobrir o ciclo completo de uma entrega, do requisito à validação.

### 1.2 Ponto de partida
Antes do brainstorm já existiam:

- `escrever-prd` — cria/edita PRDs autocontidos com foco em regras de negócio, usando `status` e `depends_on` no frontmatter; PRD é imutável quando marcado como `concluido`.
- `revisao-documento-tecnico` — valida specs, PRDs e RFCs antes da implementação.
- `guia-de-testes` — orienta escrita e auditoria de testes (unit/integração/E2E).
- `teste-e2e-navegacao` — gera e executa casos de teste E2E para apps web.
- `typescript-practices` — convenções prescritivas de qualidade TypeScript.
- `nextjs-bootstrap` — scaffolding greenfield Next.js.
- `brainstorm` — skill de maturação de ideias, usada nesta sessão.

O que estava faltando: as fases entre o PRD e a validação final da implementação.

### 1.3 Referências consultadas
- **OpenSpec** (`/home/fabricioveronez/projetos/OpenSpec`) — fluxo baseado em changes/deltas, com proposals, specs aninhadas, tasks atômicas e archival. Customizável via YAML e templates editáveis.
- **agent-skills** (addyosmani) — 7 slash commands lineares (`/spec` → `/plan` → `/build` → `/test` → `/review` → `/code-simplify` → `/ship`), com gates entre fases (SPECIFY → PLAN → TASKS → IMPLEMENT).
- **Marketplace próprio** — PRD autocontido, `status` + `depends_on`, skills modulares por domínio.

### 1.4 Postura adotada
**Inspirar, não copiar.** As referências servem para destilar princípios; nenhuma foi adotada na íntegra. O fluxo final precisa ter identidade própria, coerente com o marketplace já existente e com o uso solo do autor.

---

## 2. Problema identificado

### 2.1 Falta de orquestração entre skills existentes
As skills existentes cobrem pontas isoladas do ciclo (PRD de um lado, testes do outro), mas não há uma sequência definida. Após `escrever-prd` terminar, o próximo passo fica implícito.

### 2.2 Risco de fluxo sem identidade
Se o fluxo for apenas "pegue um pedaço do OpenSpec e outro do agent-skills", o resultado fica inconsistente — filosofias diferentes entram em choque (OpenSpec é iterativo baseado em deltas, agent-skills é linear com gates).

### 2.3 Reframing do problema
A pergunta inicial do usuário era "quais skills/agents/commands eu crio?". A pergunta certa é **"qual é a filosofia do meu fluxo?"** — sem isso, o conjunto de skills se contradiz. Outro ponto: o gap real não é quantidade de skills, é **orquestração** (quando usar qual, em que ordem, como uma alimenta a outra).

---

## 3. Filosofia do fluxo

### 3.1 Princípios do OpenSpec considerados
- **Changes como unidade de trabalho** — cada mudança isolada, com proposal/spec/tasks.
- **Archival** — mudanças concluídas viram histórico consultável.
- **Templates editáveis** — fluxo customizável, não hardcoded.
- **Fluxo iterativo** — fases acessíveis a qualquer momento, não waterfall.

### 3.2 Princípios do agent-skills considerados
- **Fases nomeadas com gate** — SPECIFY, PLAN, TASKS, IMPLEMENT em sequência.
- **Surfacing assumptions** — obrigar a explicitar pressupostos antes de codar.
- **Comandos curtos e objetivos** — uma skill por fase, nomes diretos.

### 3.3 Princípios do marketplace atual
- **PRD autocontido** — cada PRD carrega todo o contexto necessário (regras, referências).
- **Status + `depends_on`** — rastreamento explícito do ciclo de vida no frontmatter.
- **Imutabilidade em `concluido`** — PRDs concluídos não são editados.

### 3.4 O que foi descartado e por quê
- **Fluxo iterativo puro (OpenSpec)** — solo e sem disciplina coletiva, iteração livre vira bagunça.
- **Gate rígido obrigatório (agent-skills)** — em trabalho solo, gates duros são ignorados ou viram burocracia.
- **Change/delta como átomo** — decidiu-se manter o PRD como átomo, coerente com o que já existe no marketplace.
- **E2E plan como fase separada** — reclassificado como comportamento transversal (ver 5.7).

---

## 4. Fluxo consolidado

### 4.1 Sequência
```
[brainstorm opcional]
       ↓
  SPEC (= PRD)          →  escrever-prd (existe)
       ↓
  PLAN + TASKS          →  criar-plan (a criar) — plano narrativo + checklist [ ]/[X]
       ↓
  IMPLEMENT             →  implementar-task (a criar) — executa tasks e marca [X]
       ↓
  VALIDATE              →  validar-implementacao (a criar)
```

### 4.2 Entradas e saídas de cada fase

| Fase | Entrada | Saída |
|------|---------|-------|
| brainstorm | Ideia solta do usuário | Decisões maturadas, trade-offs explicitados |
| SPEC (PRD) | Contexto de negócio | PRD com regras, critérios de aceite, referências |
| PLAN + TASKS | PRD aprovado + TRD (se existir) | Plano narrativo com lista de tasks em checkbox |
| IMPLEMENT | Uma ou mais tasks abertas | Código + tasks marcadas `[X]` |
| VALIDATE | PRD + código implementado | Relatório de coerência + qualidade |

### 4.3 Diagrama textual
- **Eixo principal (obrigatório):** PRD → PLAN → IMPLEMENT → VALIDATE.
- **Entrada opcional:** `brainstorm` antes do PRD, para maturar a ideia.
- **Referências técnicas globais (opcionais):** TRD e ADR alimentam o contexto do PLAN e da IMPLEMENT.
- **Comportamentos transversais:** E2E plan, revisão de documentos, guia de testes, etc. podem ser acionados em qualquer fase, sob demanda.

---

## 5. Decisões-chave

### 5.1 SPEC = PRD
SPEC e PRD são a mesma coisa neste fluxo. A skill `escrever-prd` já cobre essa fase. Não será criada uma skill separada de "spec".

### 5.2 PLAN + TASKS unificados
Ficam em uma única skill (`criar-plan`). Motivo: quando o PLAN é editado ou revisitado, as tasks precisam mudar junto — separar as duas geraria dessincronia. Coesão é maior que granularidade nesse caso.

### 5.3 TASKS como checklist dentro do PLAN
Formato: `[ ]` para pendente, `[X]` para concluído. Tasks e subtasks ficam no próprio documento do PLAN, em Markdown puro. Sem estruturas separadas ou bancos de dados — tudo versionado no repositório do projeto.

### 5.4 VALIDATE = coerência + qualidade
A fase de validação executa dois tipos de verificação:
- **Coerência código ↔ PRD** — a implementação cobre os critérios de aceite do PRD.
- **Qualidade de código** — boas práticas, convenções do projeto.

### 5.5 TRD — referência técnica global
O TRD é um **documento global do projeto**, não por-feature. Contém stack, padrões, arquitetura. É opcional (principalmente em projetos pequenos). Quando existe, é carregado automaticamente como contexto pelas skills de fluxo.

### 5.6 ADR — decisões pontuais
O ADR registra decisões arquiteturais irreversíveis ou com trade-off relevante. É opcional. Quando aceito, pode alimentar o TRD.

### 5.7 E2E — comportamento, não fase
`teste-e2e-navegacao` é uma skill de comportamento transversal. O plano de testes E2E não é fase separada entre PLAN e TASKS — é acionado manualmente pelo usuário ou pelo próprio Claude Code quando fizer sentido (feature toca UI, fluxo multi-tela, etc.).

### 5.8 Rastreabilidade
PLAN e TASKS referenciam o PRD via frontmatter (por exemplo, `prd: <slug>`). Isso permite rastreabilidade bidirecional: a partir do PRD é possível listar PLANs e TASKS relacionados, e vice-versa.

### 5.9 Estados (status)
- **PRD:** `rascunho | aprovado | em-implementacao | concluido` (padrão existente).
- **PLAN:** espelha o PRD — `rascunho | aprovado | em-execucao | concluido`.
- **TASKS:** via checkbox no próprio documento (`[ ]` / `[X]`), sem status separado.

### 5.10 Verificação de TRD antes do PLAN
A skill `criar-plan` deve sempre verificar se existe TRD antes de gerar plano e tasks. Se existir, carrega como contexto; se não existir, segue sem — mas a checagem é obrigatória.

---

## 6. Mapa de skills do ecossistema

### 6.1 Skills de fluxo (sequenciais)
Executadas em ordem, formam o eixo principal do fluxo.

| Skill | Estado | Responsabilidade |
|-------|--------|------------------|
| `escrever-prd` | Existe | Cria/edita PRDs (fase SPEC) |
| `criar-plan` | A criar | Lê PRD + TRD (se existir) e gera PLAN narrativo com TASKS em checkbox |
| `implementar-task` | A criar | Executa task(s) do PLAN, respeita TRD, marca `[X]` ao concluir |
| `validar-implementacao` | A criar | Verifica coerência código ↔ PRD + qualidade |

### 6.2 Skills de artefatos globais
Criam/atualizam documentos técnicos transversais. Opcionais.

| Skill | Estado | Responsabilidade |
|-------|--------|------------------|
| `criar-trd` | A criar | Cria/atualiza TRD global do projeto |
| `criar-adr` | A criar | Adiciona ADR, opcionalmente atualiza TRD |

### 6.3 Skills de comportamento (transversais, já existem)
Acionadas sob demanda em qualquer fase. Não fazem parte da sequência do fluxo.

- `brainstorm` — maturação de ideias antes do PRD.
- `teste-e2e-navegacao` — geração/execução de casos E2E.
- `guia-de-testes` — orientação de testes em qualquer camada.
- `revisao-documento-tecnico` — revisão de PRD, PLAN, TRD antes da implementação.
- `typescript-practices` — convenções TypeScript.
- `nextjs-bootstrap` — scaffolding Next.js.

### 6.4 Skills de verificação
Categoria reservada. Ainda não definida. Escopo provisório: checagens específicas acionáveis durante ou após o fluxo (tipo lint de domínio, verificação de invariantes, auditoria de padrões).

### 6.5 Fluxos auxiliares
Categoria reservada. Ainda não definida. Escopo provisório: sub-fluxos ou ramificações do fluxo principal (por exemplo, hotfix, refatoração guiada, migração).

---

## 7. Trade-offs avaliados

| # | Decisão | Alternativas | Escolha | Justificativa |
|---|---------|--------------|---------|---------------|
| 7.1 | Base filosófica | (A) adotar OpenSpec direto — (B) criar próprio inspirado | **B** | Quer controle e coesão com marketplace próprio |
| 7.2 | Átomo do fluxo | (A) PRD (feature grande) — (B) change/delta | **A (PRD)** | Mantém o que já existe; change/delta exigiria refazer `escrever-prd` |
| 7.3 | Linearidade | (A) linear com gates — (B) iterativo livre | **Linear** (brainstorm é ponto de entrada opcional) | Disciplina solo requer sequência clara |
| 7.4 | Rigidez dos gates | (A) rígidos obrigatórios — (B) opcionais com escape hatch | **Aberto** | Decisão postergada (ver 10) |
| 7.5 | PLAN e TASKS | (A) skills separadas — (B) unificadas | **Unificadas** | Edição síncrona; tasks seguem o plan |
| 7.6 | Opcionalidade TRD/ADR | (A) sempre obrigatórios — (B) opcionais por discrição | **Opcionais** | Projetos pequenos não precisam |
| 7.7 | E2E no fluxo | (A) fase própria entre PLAN e TASKS — (B) comportamento transversal | **Comportamento** | Acionamento sob demanda, não como gate |
| 7.8 | VALIDATE | (A) checklist + testes — (B) comparação automática PRD↔código — (C) cenários executáveis Given/When/Then | **A** | Começar simples, evoluir depois |
| 7.9 | TRD como contexto | (A) carregado automaticamente — (B) referência manual | **Automático** | Referência manual cai no esquecimento |
| 7.10 | Ativação do E2E | (A) flag manual — (B) critério automático (toca UI?) — (C) sempre pergunta | **A (manual)** | Critério automático é frágil solo |

---

## 8. Riscos identificados

### 8.1 Duplicar OpenSpec sem valor agregado
Se o fluxo virar "OpenSpec pior", seria mais honesto adotar OpenSpec diretamente. O valor do fluxo próprio precisa estar na integração com o marketplace já existente (PRD, skills atuais) — não em reinventar o que OpenSpec já faz bem.

### 8.2 Sobreposição entre skills
Hoje `escrever-prd` e `revisao-documento-tecnico` já tangenciam em função. Adicionar `criar-plan`, `criar-trd`, `criar-adr`, `implementar-task`, `validar-implementacao` aumenta o risco de responsabilidades sobrepostas. Cada skill nova precisa ter escopo claro para não virar 8 skills onde 3 resolviam.

### 8.3 Specs que envelhecem e viram ficção
O maior risco de qualquer fluxo spec-driven: o spec envelhece, o código evolui, e ninguém atualiza. Sem mecanismo de reconciliação, o PRD e o PLAN deixam de refletir a realidade.

### 8.4 Burocracia em features simples
Passar por 5 fases para renomear um botão é absurdo. O fluxo precisa ter escape hatch explícito, ou vai ser ignorado em qualquer tarefa pequena.

### 8.5 Fluxo desenhado para a teoria, não para o uso real
Risco de projetar o fluxo ideal em vez do fluxo que o autor de fato vai seguir sozinho. O desenho deve partir de casos reais, não do modelo abstrato.

### 8.6 Gate rígido em trabalho solo tende a ser ignorado
Em time, gate serve para alinhar pessoas. Solo, vira atrito. Gates precisam ser opcionais ou muito baratos de cumprir.

---

## 9. Oportunidades

### 9.1 Skill "mapa" (`fluxo-dev`) orquestradora
Uma skill que não executa nada, só orienta qual próximo passo chamar em cada fase do fluxo. Resolve o problema de orquestração sem criar mais burocracia. Ainda em aberto (ver 10.4).

### 9.2 Tracking unificado
Estender o padrão do PRD (`status` + `depends_on`) para PLAN e TASKS. Permite rastreabilidade do negócio até o código, via frontmatter em todos os artefatos.

### 9.3 Reconciliação automática spec ↔ código
Skill que compara PRD/PLAN com o código atual e reporta divergências. Ataca diretamente o risco de spec que vira ficção (8.3).

### 9.4 Escape hatch (gates opcionais)
Gates com flag `simples` que permite pular direto para implementação em tarefas triviais. Evita o risco 8.4 (burocracia em features pequenas) sem abandonar disciplina nos casos que pedem.

---

## 10. Pontos em aberto

Registros de decisões que foram deixadas para o momento da criação de cada skill.

### 10.1 Estrutura de pastas dos artefatos
Onde PRD, PLAN, TRD e ADR ficam no projeto alvo? Opções iniciais: `docs/specs/`, `.spec/`, ou outra convenção. A decidir ao criar a primeira skill que grava artefato em projeto alvo.

### 10.2 Granularidade do `implementar-task`
A skill executa uma task por vez (com aprovação entre elas) ou varre todas até o fim? Impacta UX e segurança.

### 10.3 Nomes finais das skills
Manter consistência de verbo: `escrever-prd` já existe. As novas seguem `escrever-*` ou `criar-*`? Decidir nomenclatura antes de criar a primeira.

### 10.4 Skill "mapa" (`fluxo-dev`) orientadora
Criar ou não? Pode ser overhead, mas resolve orquestração. Decisão adiada.

### 10.5 Skills de verificação
Categoria reservada (6.4). Escopo, gatilhos e relação com `validar-implementacao` precisam ser definidos. Há risco de sobreposição.

### 10.6 Fluxos auxiliares
Categoria reservada (6.5). Escopo, gatilhos e relação com o fluxo principal precisam ser definidos.

### 10.7 Gate rígido vs opcional
Trade-off 7.4 deixou em aberto. A decidir quando o fluxo for exercitado em uso real.

---

## 11. Próximos passos

### 11.1 Status deste documento
É **registro**, não plano de execução. Serve como referência histórica e base para decisões futuras. Não existe obrigação de implementar nada a partir dele.

### 11.2 Implementação adiada
Nenhuma skill, agent ou command será criado a partir deste brainstorm sem decisão explícita do autor.

### 11.3 Sugestão de ordem quando a implementação começar
- **Começar por `criar-plan`** — é a próxima peça após o PRD que já existe; fecha o primeiro gap crítico do fluxo.
- **Alternativa: `criar-trd`** — se o autor quiser estabelecer a referência global antes de gerar planos que a consomem automaticamente.

As demais skills (`implementar-task`, `validar-implementacao`, `criar-adr`) vêm depois, conforme o fluxo for exercitado em casos reais.
