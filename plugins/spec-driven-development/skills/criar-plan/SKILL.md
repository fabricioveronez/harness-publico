---
name: criar-plan
description: >
  Gera e mantém PLAN+TASKS a partir de um PRD — PLAN.md com a abordagem técnica
  e TASKS.md com o checklist de execução, salvos num diretório efêmero
  `./.aidev/{nnn-slug-do-prd}/`. Cobre três modos: criação (do zero,
  a partir de um PRD pronto), edição (reabre PLAN/TASKS existentes preservando
  IDs de task e marcações `[X]` de conclusão) e reconciliação sob demanda
  (releitura do PRD para absorver mudanças sem perder progresso). PLAN e TASKS
  são scaffolding operacional — o PRD permanece a fonte de verdade histórica.
  A skill não marca `[X]` em tasks (papel de `implementar-task`) nem edita o PRD
  (papel de `escrever-prd`).
  Use quando o usuário quiser gerar um plano de execução, quebrar um PRD em
  tarefas técnicas, criar PLAN e TASKS, preparar a implementação de uma feature,
  reabrir um plano existente, atualizar um plano porque o PRD mudou,
  reconciliar PLAN com PRD, reorganizar tasks, ou qualquer variação disso —
  mesmo que não use o termo "plan" explicitamente. Também quando mencionar
  "gerar plano", "quebrar em tasks", "plano de implementação", "plano técnico",
  "criar tasks a partir do PRD", ".aidev", "refinar plano", "ajustar plano",
  "editar plano", "atualizar tasks" ou "reconciliar plano".
---

# Criar PLAN+TASKS

Gera e mantém o scaffolding de execução (`PLAN.md` + `TASKS.md`) de um PRD. A
skill cobre três modos — **criação**, **edição** e **reconciliação sob demanda** —
e grava tudo em `./.aidev/{nnn-slug-do-prd}/`, um diretório efêmero no
projeto alvo.

A skill não executa as tasks, não marca `[X]` em tasks (papel de
`implementar-task`) e não edita o PRD (papel de `escrever-prd`). Ela gera o
plano e mantém ele coerente com o PRD ao longo do tempo.

## Papel no fluxo spec-driven

O fluxo é: `escrever-prd` → **`criar-plan`** → `implementar-task` →
`validar-implementacao`. Esta skill é a segunda peça — assume que existe um
PRD com `status: pronto` (ou `em-progresso`) e produz o plano técnico que
guia a execução.

Princípios herdados do padrão de PRDs:

- **Imutabilidade do PRD em `concluido`** — PRD com `status: concluido` não
  gera nem reconcilia plano. Mudanças de comportamento abrem um novo PRD.
- **IDs estáveis** — IDs de task (`T01`, `T02`...) não mudam depois de
  atribuídos. Artefatos futuros (logs de execução, referências em commits)
  apontam para esses IDs.
- **Estado externo à skill** — a marcação `[X]` em tasks é feita por quem
  executa (humano ou `implementar-task`), nunca por esta skill. A skill lê
  `[X]` para preservar no modo edição/reconciliação; não escreve.
- **Rastreabilidade ao PRD** — PLAN e TASKS carregam `prd: <slug>` no
  frontmatter, permitindo voltar à fonte de verdade a qualquer momento.

## Entrada

O usuário fornece uma referência ao PRD alvo, podendo incluir:

- O número (ex.: "PRD 003", "003")
- O slug ou nome parcial (ex.: "autenticação OAuth")
- O caminho completo do arquivo
- Ou pedindo algo genérico ("gera o plano da feature de pagamentos")

`$ARGUMENTS` — se fornecido, tratar como referência inicial ao PRD.

Argumentos opcionais que alteram o modo:

- "reconciliar", "atualizar com o PRD", "PRD mudou" → **modo reconciliação**
- Ausência de qualquer PLAN/TASKS existente para o PRD → **modo criação**
- Presença de PLAN/TASKS existentes, sem pedido explícito de reconciliar →
  **modo edição**

## Fluxo de Execução

### 1. Localização e validação do PRD

Antes de qualquer coisa, a skill precisa saber onde ficam os PRDs no projeto
alvo. Não assumir diretório fixo — projetos diferentes podem usar caminhos
diferentes.

1. **Na primeira invocação da skill neste projeto**, perguntar ao usuário o
   diretório de PRDs, sugerindo `./docs/prds/` como default (convenção da
   skill `escrever-prd`). Aceitar a sugestão, outro caminho informado, ou
   confirmar que é esse mesmo.
2. Localizar o PRD pelo número, slug ou arquivo informado. Se houver
   ambiguidade, listar os candidatos e pedir desambiguação.
3. **Se o PRD não existir**, interromper com mensagem sugerindo invocar
   `escrever-prd` para criá-lo antes.
4. Ler o PRD e verificar o `status` no frontmatter:
   - `concluido` → **abortar** explicando que PRDs concluídos são imutáveis
     e não geram plano. Se a feature precisa evoluir, abrir um novo PRD.
   - `rascunho` → alertar que o PRD ainda está em rascunho e perguntar se o
     usuário quer prosseguir mesmo assim (caso típico: PRD em refinamento
     mas o autor quer um rascunho de plano em paralelo).
   - `pronto` ou `em-progresso` → prosseguir.
5. Verificar se o PRD tem USs com `Rules` e `Edge cases` preenchidos. Se
   alguma US estiver vazia, alertar o usuário — o plano terá que inferir
   comportamento e pode ficar frágil. Oferecer a opção de voltar ao PRD
   antes de prosseguir.

### 2. Identificação do modo

Com o PRD carregado, verificar `./.aidev/{nnn-slug-do-prd}/` (relativo à raiz
do projeto alvo). O slug combina o número do PRD e o nome do arquivo — ex.:
PRD `003-autenticacao-oauth.md` → diretório `./.aidev/003-autenticacao-oauth/`.

- **Diretório não existe ou está vazio** → modo **criação**.
- **Diretório contém `PLAN.md` e `TASKS.md`** e o usuário não pediu
  reconciliação → modo **edição**.
- **Usuário pediu explicitamente reconciliação** (ex.: "reconcilia o plano",
  "o PRD mudou, atualiza", "releia o PRD") → modo **reconciliação**.
- **Diretório contém arquivos parciais** (só um dos dois, ou versão quebrada)
  → reportar incoerência ao usuário e pedir decisão (recomeçar apagando, ou
  tentar recuperar).

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

### 4. Modo Criação

Com PRD validado e contexto técnico em mãos, gerar os dois arquivos.

1. **Analisar todas as informações disponíveis** — PRD + TRD/mini-coleta +
   observação direta do projeto (estrutura de pastas, package.json,
   Cargo.toml, etc., conforme o caso).
2. **Detectar lacunas críticas** — qualquer coisa que impeça decidir a
   abordagem (ex.: qual biblioteca de auth usar, onde persistir estado, se
   é SSR ou SPA). Se houver lacunas, entrevistar o usuário **uma pergunta
   por vez**, agrupando no máximo 2 relacionadas.
3. **Gerar PLAN.md em memória**, seguindo o template em
   `references/template-plan.md`. Seções obrigatórias:
   - Frontmatter com `prd: <slug>`, `created`, e status do plano.
   - Referência ao PRD (link no corpo e resumo de 2-3 linhas).
   - Abordagem técnica (decisões de alto nível).
   - Arquivos afetados (lista com propósito breve).
   - Diagrama de implementação (bloco de código texto).
   - Dependências novas (bibliotecas + versão, quando aplicável).
   - Premissas assumidas (o que presumiu na ausência de info explícita).
   - Contexto técnico global (TRD ou mini-coleta), incluindo
     **`Comando de teste:`** (obrigatório — `Sem suíte de testes detectada`
     quando não há suíte). Esse campo é consumido pela `implementar-task`.
   - Milestones cobertos (IDs do PRD endereçados).
   - Riscos técnicos.
4. **Gerar TASKS.md em memória**, seguindo o template em
   `references/template-tasks.md`. Cada task traz:
   - `## [ ] TNN: título` (marcador de conclusão geral; `[P]` é adicionado
     ao título pela inferência de paralelismo — ver regra abaixo).
   - **USs cobertas**: IDs do PRD.
   - **Nível**: usuário | API | componente (ver heurística de verticalização
     abaixo).
   - **needs**: IDs de outras tasks (ou `—` quando independente).
   - **Passos**: checklist de sub-passos, cada um com `- [ ]`.
   - **Validação**: checklist adaptado ao tipo da task (ver regra abaixo).
5. **Gravação atômica** — escrever os dois arquivos no disco em sequência.
   Se um deles falhar, apagar o outro para não deixar estado parcial. Antes
   de gravar, apresentar um resumo ao usuário (quantas tasks, principais
   decisões, lista de arquivos afetados) e pedir confirmação.
6. **Apresentar ao usuário** — depois de gravar, abrir os dois arquivos para
   revisão rápida. Pedir feedback antes de considerar a geração concluída.

### 5. Modo Edição

Quando o PLAN e TASKS já existem e o usuário quer ajustar algo (adicionar
uma task, revisar abordagem, trocar decisão técnica), a skill entra neste
modo automaticamente.

1. Ler `PLAN.md` e `TASKS.md` existentes.
2. **Extrair o que está preservado**:
   - IDs de task já atribuídos (`T01`, `T02`...).
   - Tasks com `[X]` no título ou em qualquer passo/validação.
   - Decisões registradas no PLAN.
3. Conversar com o usuário sobre o que ele quer ajustar.
4. Aplicar as mudanças:
   - **Mudanças na narrativa/escopo do PLAN** que não afetem tasks
     existentes → edita só o PLAN, não toca em TASKS.
   - **Mudanças que afetam tasks** (nova abordagem, decisão técnica diferente
     que invalida passos) → atualiza PLAN e dispara revisão do TASKS.
   - **Novas tasks** → recebem o próximo ID sequencial disponível, anexadas
     ao final.
   - **Tasks com `[X]`** → **preservadas integralmente**; nunca sobrescrever
     passos ou validações já marcadas.
5. **Edge case: edição invalida uma task `[X]`** → alertar o usuário e pedir
   decisão. Opções: manter como registro histórico com nota, ou marcar como
   revisada adicionando uma subtask de reverificação. Nunca apagar o `[X]`
   silenciosamente.
6. **Apresentar diff** ao usuário antes de gravar — o que mudou no PLAN, o
   que mudou no TASKS, o que foi preservado. Aguardar confirmação.
7. Gravar em modo atômico (mesma regra do modo criação).

### 6. Modo Reconciliação

Este modo só roda sob **pedido explícito** do usuário — nunca automático. O
gatilho é o usuário dizer algo como "o PRD mudou, atualiza o plano" ou
"reconcilia o plano com o PRD".

1. Ler o PRD atual e comparar com o que o PLAN reflete:
   - USs novas no PRD que não têm task associada.
   - USs removidas do PRD que ainda têm tasks no PLAN.
   - Mudanças em `Rules` ou `Edge cases` que invalidam tasks existentes.
   - Novas decisões de produto ou mudanças em "Fora do escopo".
2. **Se o PRD virou `concluido`** entre a criação do PLAN e a reconciliação
   → abortar. Imutabilidade impede reconciliação adicional.
3. **Se a divergência é tão grande que reconciliar é mais caro que
   recomeçar**, sinalizar ao usuário e sugerir apagar `./.aidev/{slug}/` e
   invocar a skill em modo criação.
4. Caso contrário, planejar os ajustes:
   - **Todas as tasks com `[X]`** (inteiras, passos ou validações) são
     **preservadas**. Nunca deletar progresso validado.
   - **Novas tasks necessárias** são adicionadas **abaixo das existentes**,
     com IDs sequenciais continuando.
   - **US removida do PRD mas já entregue por uma task `[X]`** →
     registrar no PLAN como "órfã concluída" (seção de histórico), sem
     deletar a task. É histórico, não lixo.
5. **Apresentar ao usuário um resumo das mudanças detectadas e dos ajustes
   planejados** antes de gravar. Resumo inclui:
   - Mudanças no PRD que motivaram a reconciliação.
   - Tasks novas a adicionar (com IDs e títulos).
   - Tasks preservadas intocadas.
   - Tasks a marcar como órfãs.
6. Gravar em modo atômico.

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

Gravação de PLAN.md + TASKS.md é sempre atômica: ou ambos são gravados com
sucesso, ou nenhum. Nunca deixar o diretório `./.aidev/{slug}/` em estado
inconsistente. Apresentar preview antes de gravar sempre que possível.

### Rastreabilidade

PLAN e TASKS carregam `prd: <slug>` no frontmatter. O slug é exatamente o
nome do arquivo do PRD sem extensão (ex.: `003-autenticacao-oauth`). Isso
permite voltar à fonte de verdade a qualquer momento e viabiliza
ferramentas futuras de auditoria.

## Fora do escopo

Esta skill **não**:

- Executa tasks (papel de `implementar-task`).
- Marca `[X]` em tasks concluídas (papel de `implementar-task` ou humano).
- Edita o PRD (papel de `escrever-prd`).
- Cria ou edita o TRD (papel de `escrever-trd`).
- Valida a implementação contra o PRD (papel de `validar-implementacao`).
- Gera plano para PRDs com `status: concluido`.

## Templates de referência

- `references/template-plan.md` — estrutura canônica do `PLAN.md`.
- `references/template-tasks.md` — estrutura canônica de cada task dentro
  do `TASKS.md`.

Consultar sempre que for gerar ou editar os arquivos — o template é a
forma autoritativa.
