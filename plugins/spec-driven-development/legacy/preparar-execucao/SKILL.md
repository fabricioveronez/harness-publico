---
name: preparar-execucao
description: >
  Gera e mantém o bundle de execução SPEC+PLAN+TASKS de uma feature —
  `SPEC.md` (contrato comportamental orientado à IA: US Rules, Edge cases e
  critérios de aceite), `PLAN.md` (abordagem técnica) e `TASKS.md` (checklist
  de execução), salvos num diretório `./.aidev/{slug}/` que forma um bundle
  Open Knowledge Format (OKF). Decompõe o escopo em 1..N fatias — cada fatia é
  uma feature independente e testável com seu próprio bundle
  `./.aidev/{slug}-{fatia}/`; quando gera 2+ fatias, emite também um manifesto
  `./.aidev/{slug}-manifest.md` com o grafo de dependência e as ondas de
  paralelismo (feature pequena degenera em 1 fatia, bundle único, sem
  manifesto). Tem dois modos de entrada: projeta o SPEC a partir de um PRD
  pronto (projeto grande) ou, quando não há PRD, entrevista o usuário e autora o
  SPEC direto (projeto pequeno) — nos dois casos emite os arquivos em lote.
  Cobre ainda edição (reabre o bundle preservando IDs de task e marcações
  `[X]`) e reconciliação sob demanda (relê o SPEC/PRD para absorver mudanças sem
  perder progresso). A skill não marca `[X]` em tasks (papel de
  `implementar-task`), não edita o PRD (papel de `escrever-prd`) nem orquestra a
  execução paralela (papel de `orquestrar-execucao`).
  Use quando o usuário quiser preparar a execução de uma feature, gerar o
  SPEC/PLAN/TASKS, projetar a spec a partir de um PRD, escrever a spec de uma
  feature sem PRD, quebrar uma feature em tarefas técnicas, reabrir um bundle
  existente, atualizar porque o PRD/SPEC mudou, reconciliar plano, reorganizar
  tasks, ou qualquer variação disso — mesmo que não use esses termos
  explicitamente. Também quando mencionar "preparar execução", "gerar spec",
  "criar plano", "quebrar em tasks", "decompor em fatias/bundles", "preparar
  bundles em paralelo", "gerar o manifesto", "plano de implementação", "plano
  técnico", ".aidev", "refinar plano", "ajustar plano", "editar plano",
  "atualizar tasks" ou "reconciliar plano".
---

# Preparar Execução (SPEC+PLAN+TASKS)

Gera e mantém o **bundle de execução** de uma feature — `SPEC.md` + `PLAN.md` +
`TASKS.md` — gravado em `./.aidev/{slug}/`, um diretório no projeto alvo que
forma um bundle **Open Knowledge Format (OKF)** (markdown com YAML frontmatter;
só `type` é obrigatório, o resto é convenção).

- **`SPEC.md`** — o contrato comportamental **orientado à IA**: US Rules, Edge
  cases e critérios de aceite. É o que `implementar-task` e
  `validar-implementacao` carregam como contexto primário. Quando há PRD, o SPEC
  é uma **projeção** dele (o PRD é a fonte de verdade e vence em conflito; a IA
  abre o PRD sob demanda só para o *porquê*). Sem PRD, o SPEC é autorado direto e
  é a própria fonte de verdade.
- **`PLAN.md`** — a abordagem técnica (o "como").
- **`TASKS.md`** — o checklist de execução por task verticalizada.

**Decomposição em fatias.** O escopo pode render **mais de um bundle**. A skill
decompõe em **fatias** — unidades de *feature independente e testável* — e gera
um bundle por fatia em `./.aidev/{slug}-{fatia}/`. Quando há 2+ fatias, emite
também o **manifesto** `./.aidev/{slug}-manifest.md` (índice + grafo de
dependência + ondas de paralelismo), que o `orquestrar-execucao` consome para
rodar as fatias independentes em paralelo. O gatilho é o **tamanho do escopo**,
não a presença de PRD: feature pequena degenera em **1 fatia** — bundle único
`./.aidev/{slug}/`, sem manifesto, idêntico ao comportamento anterior.

A skill cobre **criação** (decompõe e gera em lote), **edição** e
**reconciliação sob demanda**. Não executa as tasks, não marca `[X]` (papel de
`implementar-task`), não edita o PRD (papel de `escrever-prd`) e não orquestra a
execução paralela (papel de `orquestrar-execucao`).

## Papel no fluxo spec-driven

O fluxo é: `escrever-prd` (opcional) → **`preparar-execucao`** →
`implementar-task` → `validar-implementacao`. Esta skill é a peça que traduz a
intenção (PRD, quando existe) no contrato executável e no scaffolding técnico.

Princípios:

- **PRD opcional; SPEC sempre** — em projeto grande, existe PRD e o SPEC o
  projeta; em projeto pequeno, não há PRD e o SPEC é autorado direto. O bundle
  SPEC+PLAN+TASKS existe nos dois casos.
- **Fatia = feature independente e testável** — a unidade de decomposição é a
  fatia, não o marco nem a US. Um PRD (ou um marco) pode render **1..N** fatias;
  marco/US viram rastreabilidade (rollup no manifesto), não a régua do corte. A
  independência (arquivos afetados disjuntos) é o que habilita a execução
  paralela. Fatia ⊆ um marco, para manter o rollup do checklist de aceite limpo.
- **Dimensionamento é responsabilidade desta skill** — o PRD referencia mas não
  dirige nem dimensiona o artefato técnico; a decisão de quantas fatias e como
  cortá-las mora aqui (PLAN/TASKS/manifesto).
- **Imutabilidade do PRD em `concluido`** — PRD com `status: concluido` não
  gera nem reconcilia bundle. Mudanças de comportamento abrem um novo PRD.
- **IDs estáveis** — IDs de US (`US01`...) e de task (`T01`...) não mudam depois
  de atribuídos. Artefatos futuros (logs, commits, validação) apontam para eles.
- **Estado externo à skill** — a marcação `[X]` em tasks é feita por quem executa
  (humano ou `implementar-task`), nunca por esta skill. A skill lê `[X]` para
  preservar em edição/reconciliação; não escreve.
- **Rastreabilidade** — SPEC/PLAN/TASKS carregam `prd: <slug|none>` no
  frontmatter e cross-links markdown entre si (PLAN→SPEC, TASKS→PLAN) e para
  PRD/TRD/ADR quando existem.

## Entrada

O usuário fornece uma referência à feature alvo, podendo incluir:

- Uma referência a um **PRD** (número "PRD 003"/"003", slug/nome parcial, ou
  caminho do arquivo) → **modo com PRD** (projeta o SPEC dele).
- Uma descrição direta da feature **sem PRD** ("prepara a execução do login por
  magic link", "gera o spec e as tasks disso") → **modo sem PRD** (autora o SPEC).
- Ou algo genérico ("prepara a execução da feature de pagamentos").

`$ARGUMENTS` — se fornecido, tratar como referência/descrição inicial.

Argumentos opcionais que alteram o modo:

- "reconciliar", "atualizar com o PRD/SPEC", "o PRD mudou" → **modo reconciliação**
- Ausência de bundle existente para a feature → **modo criação**
- Presença de bundle existente, sem pedido explícito de reconciliar → **modo edição**

## Fluxo de Execução

### 1. Determinar a origem: com PRD ou sem PRD

A skill primeiro decide se vai **projetar o SPEC de um PRD** ou **autorá-lo
direto**. Isso define o `slug` do bundle e a fonte de verdade.

**1a. Há PRD referenciado?** Se o usuário citou um PRD (número, slug, arquivo)
ou o projeto claramente usa PRDs:

1. **Na primeira invocação neste projeto**, perguntar o diretório de PRDs,
   sugerindo `./docs/prds/` como default (convenção do `escrever-prd`).
2. Localizar o PRD pelo número, slug ou arquivo. Ambiguidade → listar e pedir
   desambiguação.
3. **Se o usuário citou um PRD que não existe**, oferecer: criar o PRD antes
   (via `escrever-prd`) **ou** seguir sem PRD, autorando o SPEC direto (1b).
   Não abortar — o fluxo suporta os dois caminhos.
4. Ler o PRD e verificar o `status`:
   - `concluido` → **abortar** (PRD concluído é imutável; feature que evolui
     abre novo PRD).
   - `rascunho` → alertar e perguntar se prossegue mesmo assim.
   - `pronto` ou `em-progresso` → prosseguir.
5. Verificar se o PRD tem USs com `Rules` e `Edge cases` preenchidos. US vazia
   → alertar; o SPEC teria que inferir comportamento e ficar frágil. Oferecer
   voltar ao PRD antes.

**1b. Não há PRD (projeto pequeno / feature direta).** Não abortar. A skill
**autora o SPEC** a partir da descrição do usuário, entrevistando o mínimo
necessário para montar o contrato:

- Confirmar com o usuário que seguirá sem PRD (o SPEC será a própria fonte de
  verdade).
- Coletar, em poucas perguntas enxutas (agrupar até 2 por mensagem), o que falta
  para o contrato: quem é a persona, o comportamento esperado (que vira Rules),
  as situações anômalas relevantes (Edge cases) e como se verifica que está certo
  (critérios de aceite). Inferir o que der e marcar como premissa no SPEC.
- O `resource`/`prd` do bundle ficam `none`.

### 2. Identificação do modo e do slug base

Definir o `slug` **base** da decomposição:

- **Com PRD** → combina número e nome do arquivo do PRD (ex.:
  `003-autenticacao-oauth`).
- **Sem PRD** → derivar um slug kebab-case curto da feature (ex.:
  `login-magic-link`) e confirmar com o usuário.

O slug base nomeia o conjunto. Cada fatia gerada no passo 3b/4 recebe um slug
**`{base}-{fatia}`** e vira o diretório `./.aidev/{base}-{fatia}/`; o manifesto
(quando há 2+ fatias) é `./.aidev/{base}-manifest.md`. Com **1 fatia**, o bundle
é `./.aidev/{base}/` (sem sufixo, sem manifesto) — idêntico ao esquema anterior.

Detectar o modo varrendo `./.aidev/` (relativo à raiz do projeto alvo):

- **Nenhum bundle nem manifesto do slug base** → modo **criação**.
- **Existe bundle(s) do slug base** (`./.aidev/{base}/` ou `./.aidev/{base}-*/`,
  eventualmente com manifesto) e o usuário não pediu reconciliação → modo
  **edição**.
- **Usuário pediu explicitamente reconciliação** ("reconcilia", "o PRD/SPEC
  mudou, atualiza") → modo **reconciliação**.
- **Estado parcial/quebrado** (bundle sem os três arquivos, ou manifesto
  apontando fatia inexistente e vice-versa) → reportar incoerência e pedir
  decisão (recomeçar apagando, ou recuperar).

### 3. Carregamento de contexto técnico

O plano técnico depende de saber a stack, convenções e restrições do
projeto. A skill busca esse contexto num **TRD** (Technical Requirements
Document). Se não existir, entra em **mini-modo de coleta**.

Procurar TRD nesta ordem de paths convencionais:

1. `./docs/trd.md`
2. `./TRD.md`
3. `./docs/TRD.md`

Se encontrar, carregar e registrar no PLAN a origem (`Contexto técnico global:
carregado de ./docs/trd.md`). Extrair também o **comando de teste**
(seção dedicada do TRD ou bloco de scripts/CI) e registrar no campo
`Comando de teste:` do PLAN. Se o TRD não documenta o comando, perguntar
inline ao usuário antes de gerar o PLAN — a `implementar-task` consome esse
campo e quebra sem ele.

Se não encontrar, entrar em **mini-modo de coleta** — uma entrevista curta e
direta. Perguntar, em até 6 perguntas enxutas:

- Stack principal (linguagem, framework, banco, runtime)
- Padrões de teste e ferramentas (framework de testes, se há linter/type
  checker)
- **Comando de teste do projeto** (ex.: `npm test`, `pytest`, `cargo test`).
  Se o projeto não tem suíte de testes, anotar literalmente
  `Sem suíte de testes detectada`.
- Estrutura de pastas dominante (onde mora código, onde moram testes)
- Convenções específicas que você gostaria de refletir (ex.: error handling,
  log format)
- Restrições de ambiente (CI, deploy, features flags)

Agrupar até 2 perguntas relacionadas por mensagem. Registrar as respostas
no PLAN como "Contexto técnico global (coletado em mini-modo)".

### 3b. Decomposição em fatias

Com origem e contexto técnico em mãos, decidir **em quantas fatias** o escopo se
divide, **antes** de gerar qualquer arquivo. A fatia é a unidade de *feature
independente e testável*.

1. **Cortar por independência + testabilidade.** Agrupar as USs em fatias onde
   cada fatia (a) entrega algo observável/testável de ponta a ponta, (b)
   minimiza acoplamento com as irmãs — idealmente **Arquivos Afetados
   disjuntos** — e (c) fica contida em **um** marco (quando há PRD), para o
   rollup do checklist de aceite. Marco e US são rastreabilidade, não a régua: um
   marco grande pode virar várias fatias; uma fatia nunca cruza dois marcos.
2. **N=1 é válido e é o default de feature pequena.** Não forçar split — se o
   escopo não tem fatias independentes de verdade, gerar **uma** fatia (bundle
   único `./.aidev/{base}/`, sem manifesto). Split artificial é o mesmo
   anti-padrão da task horizontal. Vale com ou sem PRD.
3. **Inferir o grafo de dependência entre fatias** (ver "Inferência de
   dependência entre fatias" nas regras transversais): fatias com arquivos
   disjuntos e sem dependência entram na **mesma onda** (`[P]`); fatia que
   consome saída de outra recebe `needs:`.
4. **Apresentar o corte para aprovação** antes de gerar: listar as fatias
   propostas (slug, USs cobertas, marco, `needs`/`[P]`, o que roda em paralelo).
   Ajustar conforme feedback. Só depois seguir ao passo 4 (geração em lote).

### 4. Modo Criação (geração em lote)

Com a decomposição aprovada (passo 3b), gerar **para cada fatia** o seu bundle
SPEC+PLAN+TASKS e, quando há 2+ fatias, o **manifesto**. Consultar sempre os
templates — `references/template-spec.md`, `references/template-plan.md`,
`references/template-tasks.md`, `references/template-manifest.md` — que são a
forma autoritativa.

Repetir os passos 1–5 abaixo **por fatia** (cada fatia projeta só as suas USs e
escopa só os seus arquivos); depois gerar o manifesto (passo 5b) e gravar tudo
em lote atômico (passo 6).

1. **Analisar todas as informações disponíveis** — PRD (quando existe) ou a
   coleta do passo 1b + TRD/mini-coleta + observação direta do projeto
   (estrutura de pastas, package.json, Cargo.toml, etc.).

2. **Gerar SPEC.md em memória** (`references/template-spec.md`) — o contrato:
   - Frontmatter OKF: `type: spec`, `title`, `description`, `resource`
     (`<slug-do-prd|none>`), `tags: [sdd, spec]`, `created`, `status`, `prd`.
   - **Escopo da fatia** — o SPEC projeta/autora **apenas as USs desta fatia**
     (as demais moram nos SPECs das outras fatias). `title` e slug do bundle
     usam `{base}-{fatia}`.
   - **Com PRD** — projetar: copiar as US da fatia (IDs estáveis, iguais aos do
     PRD) com Rules e Edge cases, e os critérios de aceite §5a. Não inventar
     Rule/Edge case fora do PRD; lacuna vira premissa e sinaliza voltar ao
     `escrever-prd`.
   - **Sem PRD** — autorar a partir da coleta do passo 1b: US com Rules/Edge
     cases e critérios de aceite testáveis, marcando premissas.
   - Referências (cross-links): PRD (quando existe), TRD, ADRs.
   - **Não** incluir contexto narrativo, visão, métricas §5b, riscos de negócio,
     decisões de produto ou milestones — isso é PRD.

3. **Detectar lacunas técnicas críticas** — o que impeça decidir a abordagem
   (biblioteca a usar, onde persistir estado, SSR vs SPA). Se houver, entrevistar
   **uma pergunta por vez**, agrupando no máximo 2 relacionadas.

4. **Gerar PLAN.md em memória** (`references/template-plan.md`):
   - Frontmatter OKF: `type: plan` + `prd`, `created`, `status`.
   - Referências: cross-link para `SPEC.md` (irmão) e PRD (quando existe).
   - Abordagem técnica (decisões de alto nível), Arquivos afetados **escopados à
     fatia** (a disjunção entre fatias é o que habilita o paralelismo), Diagrama
     de implementação, Dependências novas, Premissas assumidas.
   - Contexto técnico global (TRD ou mini-coleta), incluindo **`Comando de
     teste:`** (obrigatório — `Sem suíte de testes detectada` quando não há
     suíte). Consumido pela `implementar-task`.
   - **Marco coberto** (quando há PRD, a fatia atende um marco) e Riscos técnicos.

5. **Gerar TASKS.md em memória** (`references/template-tasks.md`). Cada task:
   - `## [ ] TNN: título` (`[P]` é adicionado pela inferência de paralelismo).
   - **USs cobertas**: IDs de US (do SPEC).
   - **Nível**: usuário | API | componente (verticalização — ver abaixo).
   - **needs**: IDs de outras tasks (ou `—`).
   - **Passos** e **Validação**: checklists `- [ ]` (validação adaptada ao tipo).

5b. **Gerar o MANIFESTO em memória** (`references/template-manifest.md`), quando
   há **2+ fatias**:
   - Frontmatter OKF: `type: manifest`, `prd` (`<slug>`/`none`), `created`.
   - Tabela `Fatia | USs | Marco | needs | [P]` com uma linha por fatia.
   - Seção **Ondas** — ordenamento topológico resolvido a partir de `needs`.
   - Seção **Rollup de marcos** (só com PRD) — mapeia marco → USs → fatias.
   - Com **1 fatia**, não gerar manifesto.

6. **Gravação atômica do lote** — escrever **todos** os bundles (os três
   arquivos de cada fatia) e o manifesto em sequência. Se qualquer arquivo
   falhar, apagar todo o conjunto já gravado para não deixar decomposição
   parcial. Antes de gravar, apresentar um resumo (nº de fatias, USs e tasks por
   fatia, ondas de paralelismo, principais decisões) e pedir confirmação.

7. **Apresentar ao usuário** — depois de gravar, abrir o manifesto (quando há) e
   os bundles gerados para revisão rápida. Pedir feedback antes de considerar a
   geração concluída.

### 5. Modo Edição

Quando o bundle já existe e o usuário quer ajustar algo (adicionar uma task,
revisar abordagem, trocar decisão técnica, refinar o contrato), a skill entra
neste modo automaticamente.

1. Ler o **manifesto** (quando existe) e os `SPEC.md`/`PLAN.md`/`TASKS.md` de
   cada fatia existente.
2. **Extrair o que está preservado**:
   - IDs de US (`US01`...) e de task (`T01`...) já atribuídos, e os slugs de
     fatia existentes (não mudam).
   - Tasks com `[X]` no título ou em qualquer passo/validação.
   - Decisões registradas nos PLANs.
3. Conversar com o usuário sobre o que ele quer ajustar.
4. Aplicar as mudanças:
   - **Mudança de comportamento (Rule/Edge case/critério de aceite)** → quando
     **há PRD**, o contrato vem do PRD: sinalizar que o ajuste deve ir ao
     `escrever-prd` e depois reconciliar. Quando **não há PRD**, editar o `SPEC.md`
     direto (ele é a fonte de verdade).
   - **Mudança na narrativa/escopo do PLAN** que não afeta tasks → edita só o PLAN.
   - **Mudança que afeta tasks** (nova abordagem que invalida passos) → atualiza
     PLAN e dispara revisão do TASKS.
   - **Novas tasks** → próximo ID sequencial, anexadas ao final (dentro da fatia).
   - **Nova fatia** (o ajuste abre uma feature independente nova) → gerar o
     bundle `./.aidev/{base}-{fatia}/` e **atualizar o manifesto** (linha na
     tabela + recomputar ondas). Se o conjunto tinha 1 fatia sem manifesto,
     criar o manifesto e renomear o bundle único para o esquema `{base}-{fatia}`
     — **avisar o usuário**, pois muda o slug que as consumidoras enxergam.
   - **Tasks com `[X]`** → **preservadas integralmente**.
5. **Edge case: edição invalida uma task `[X]`** → alertar e pedir decisão
   (manter como histórico com nota, ou adicionar subtask de reverificação).
   Nunca apagar o `[X]` silenciosamente.
6. **Apresentar diff** antes de gravar — o que mudou em SPEC/PLAN/TASKS e o que
   foi preservado. Aguardar confirmação.
7. Gravar em modo atômico (mesma regra do modo criação).

### 6. Modo Reconciliação

Este modo só roda sob **pedido explícito** — nunca automático. Gatilho: "o
PRD/SPEC mudou, atualiza" ou "reconcilia o plano".

1. Comparar a fonte de verdade com o que o bundle reflete. A fonte é o **PRD**
   quando existe, senão o **SPEC** editado:
   - USs novas que não têm task associada.
   - USs removidas que ainda têm tasks.
   - Mudanças em `Rules`/`Edge cases`/critérios que invalidam tasks existentes.
   - Quando há PRD: reprojetar o `SPEC.md` a partir do PRD atualizado.
2. **Se o PRD virou `concluido`** entre a criação e a reconciliação → abortar.
3. **Se a divergência é grande demais** (reconciliar custa mais que recomeçar),
   sinalizar e sugerir apagar `./.aidev/{slug}/` e recriar.
4. Caso contrário, planejar os ajustes **em nível de fatia e de task**:
   - **Todas as tasks com `[X]`** são **preservadas**. Nunca deletar progresso.
   - **USs novas** → cabem numa fatia existente (nova task, ID continuando) ou
     abrem uma **fatia nova** (novo bundle + linha no manifesto + recomputar
     ondas). Fatias novas entram **abaixo** das existentes; slugs das fatias
     existentes não mudam.
   - **US removida da fonte mas já entregue por uma task `[X]`** → registrar como
     "órfã concluída" (histórico) no PLAN da fatia e nota no manifesto, sem
     deletar a task nem a fatia.
   - **Fatia inteira esvaziada** (todas as USs removidas e nenhuma `[X]`) →
     remover o bundle e a linha do manifesto; se havia `[X]`, vira fatia órfã
     concluída (mantida).
   - **Recomputar o manifesto** — tabela, ondas e rollup refletem o novo estado.
5. **Apresentar ao usuário um resumo das mudanças detectadas e dos ajustes
   planejados** antes de gravar. Resumo inclui:
   - Mudanças no PRD que motivaram a reconciliação.
   - Fatias novas a criar e tasks novas a adicionar (com IDs e títulos).
   - Fatias/tasks preservadas intocadas.
   - Fatias/tasks a marcar como órfãs.
6. Gravar em modo atômico (todo o lote: bundles afetados + manifesto).

## Regras de geração transversais

Aplicam em criação, edição e reconciliação.

### Verticalização de tasks

Tasks devem entregar valor em algum nível consumível. Hierarquia de
preferência, da mais valiosa para a menos:

1. **Usuário final** — task entrega uma interação completa para o usuário
   (ex.: "usuário consegue cadastrar conta e receber e-mail de confirmação").
2. **Interface externa (API/CLI)** — task entrega um endpoint ou comando
   testável de fora (ex.: "POST /api/users cria usuário válido").
3. **Componente interno** — task entrega um módulo/função usável por outras
   tasks mas não diretamente por usuário/API.

A skill escolhe o **nível mais alto viável** dado o escopo da US. Task
horizontal (ex.: "criar todo o schema do banco") só é aceitável quando o
slice vertical seria artificial — refatoração grande, bootstrap de stack,
setup de infra. É decisão interna da skill; não há campo declarativo.

### Inferência de paralelismo `[P]`

Após gerar todas as tasks em memória, a skill executa uma passagem de
inferência antes de gravar:

1. **Candidatas a `[P]`**: toda task com `needs: —` (sem dependências).
2. **Detecção de conflito**: cruzar os `Arquivos Afetados` do `PLAN.md`
   contra o escopo inferido de cada task (a partir dos passos e do
   contexto técnico). Se duas candidatas tocam o mesmo arquivo:
   - A task que aparece primeiro no TASKS não recebe `[P]`.
   - A segunda recebe `needs: TNN` apontando para a primeira.
3. **Aplicação**: tasks sem conflito recebem `[P]` no título
   (`## [ ] T01 [P]: título`). Tasks com conflito ficam sem `[P]` e
   ganham o `needs:` apropriado.
4. **Transparência**: ao apresentar o resumo antes de gravar, listar
   quais tasks receberam `[P]` e quais receberam `needs:` por conflito
   detectado, para revisão do usuário.

Nunca aplicar `[P]` em tasks com `needs:` preenchido — a dependência
explícita prevalece.

### Inferência de dependência entre fatias

A mesma lógica do `[P]` de task, aplicada um nível acima, entre **fatias**,
para montar o manifesto:

1. **Candidatas a `[P]` de fatia**: toda fatia que não consome saída de outra.
2. **Detecção de conflito**: cruzar os `Arquivos Afetados` do `PLAN.md` de cada
   fatia. Duas fatias que tocam o mesmo arquivo **não** são paralelas — a
   segunda recebe `needs:` apontando a primeira. Isso também é sinal de corte
   ruim: fatias deveriam ter arquivos disjuntos; se houver muito conflito,
   reavaliar a decomposição (passo 3b).
3. **Ondas**: fatias sem conflito e sem `needs` formam a onda 1; a onda de uma
   fatia com `needs` é `1 + max(onda das dependências)`.
4. **Transparência**: apresentar as ondas no resumo do corte (passo 3b) e
   gravá-las no manifesto.

Nunca marcar `[P]` numa fatia com `needs:` — a dependência explícita prevalece.

### Cadeia linear longa dispara alerta

Se a skill gerar uma sequência linear de **mais de 3 tasks dependentes
entre si** (T02 precisa de T01, T03 de T02, T04 de T03...), alertar o
usuário. Cadeia linear longa costuma ser sinal de horizontalização
disfarçada. Não bloquear — só sinalizar para revisão.

### Validação adaptativa ao tipo da task

Cada task traz um campo `Validação:` com critérios checáveis. O método de
validação muda conforme o tipo:

- **Código novo** → teste unit + integração, comando para rodar.
- **Refatoração** → suíte existente verde, nenhuma regressão detectável.
- **Infra/config** → smoke test ou health check, endpoint/comando que
  prova que está no ar.
- **Documento/schema** → revisão visual + lint, se aplicável.

Evitar validação genérica do tipo "verificar que funciona". O critério
deve ser executável e objetivo.

### Atomicidade

A gravação é sempre atômica **no nível do lote**: ou todos os bundles da
decomposição (SPEC+PLAN+TASKS de cada fatia) **e** o manifesto são gravados com
sucesso, ou nenhum. Nunca deixar `./.aidev/` com decomposição parcial (bundle
sem os três arquivos, ou manifesto dessincronizado das fatias). Apresentar
preview antes de gravar sempre que possível.

### Rastreabilidade

SPEC, PLAN e TASKS carregam `prd: <slug|none>` no frontmatter e cross-links
markdown entre si (PLAN→SPEC, TASKS→PLAN) e para PRD/TRD/ADR quando existem. O
slug base vem do nome do arquivo do PRD sem extensão (ex.:
`003-autenticacao-oauth`) ou, sem PRD, da feature; cada fatia usa
`{base}-{fatia}`. Quando há 2+ fatias, o **manifesto** é o índice que amarra o
conjunto e faz o rollup fatia→US→marco. Isso permite voltar à fonte de verdade a
qualquer momento e viabiliza auditoria.

## Fora do escopo

Esta skill **não**:

- Executa tasks (papel de `implementar-task`).
- Marca `[X]` em tasks concluídas (papel de `implementar-task` ou humano).
- Edita o PRD (papel de `escrever-prd`).
- Cria ou edita o TRD (papel de `escrever-trd`).
- Valida a implementação contra o SPEC/código nem fecha o ciclo (papel de
  `validar-implementacao`).
- Orquestra a execução paralela das fatias — worktrees, fan-out, merge (papel de
  `orquestrar-execucao`). Esta skill **prepara** o paralelismo (decompõe + grafo
  + manifesto); não o executa.
- Gera bundle para PRDs com `status: concluido`.

## Templates de referência

- `references/template-spec.md` — estrutura canônica do `SPEC.md` (contrato
  comportamental OKF).
- `references/template-plan.md` — estrutura canônica do `PLAN.md`.
- `references/template-tasks.md` — estrutura canônica de cada task dentro
  do `TASKS.md`.
- `references/template-manifest.md` — estrutura canônica do manifesto de
  execução (índice de fatias + grafo de dependência + ondas), gerado quando há
  2+ fatias.

Consultar sempre que for gerar ou editar os arquivos — o template é a
forma autoritativa.
