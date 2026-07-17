---
name: implementar-task
description: >
  Executa as tasks de um bundle SPEC+PLAN+TASKS em cadeia automática a
  partir de `./.aidev/{slug}/`, marcando `[X]` em passos, validações e
  títulos conforme avança. Carrega o `SPEC.md` como **contexto primário**
  (o contrato de comportamento: US Rules, Edge cases, critérios de aceite)
  e abre o PRD em `./docs/prds/` **sob demanda** apenas quando o SPEC o
  referencia e é preciso o *porquê* de uma regra; valida o `status` do PRD
  quando ele existe (`concluído` aborta, `rascunho` confirma, `pronto`
  transiciona para `em-progresso`, `em-progresso` prossegue). Respeita
  `needs:` entre tasks, executa grupos `[P]` em paralelo quando possível,
  e roda o bloco Validação de cada task. Em falha, entra em loop de
  correção de até 5 ciclos com execução seletiva de testes; ao esgotar
  ciclos ou detectar lacuna no SPEC, pausa, registra um bloco
  `> Pausa em ...` no `TASKS.md` e devolve controle. Trata o SPEC (com
  PRD/TRD sob demanda), o PLAN e o TASKS como fonte de verdade — nunca
  inventa informação; quando falta dado, consulta a documentação ou pausa
  como lacuna. Retomada é automática quando o bundle já existe, preservando
  todo progresso `[X]`. Ao concluir uma task com validação verde, cria
  **commit automático** em semantic commit de uma linha (sem assinatura IA),
  incluindo só os arquivos tocados pela task mais o `TASKS.md`. Nunca edita
  o SPEC/PRD nem a estrutura do PLAN/TASKS. No início de cada invocação
  avalia o catálogo de skills atual e carrega as relevantes ao domínio do
  bundle (execução-time, nada persistido).
  Use quando o usuário quiser implementar tarefa, executar tasks,
  rodar o plano, tocar a implementação de uma feature, retomar de
  onde parou, continuar implementando, executar a próxima task,
  processar `TASKS.md`, ou mencionar `.aidev`, "loop de correção",
  "implementar a feature", "executar plano", "rodar tasks", "seguir
  o plano", "implementar PRD", "tocar a implementação".
---

# Implementar Task

Executa o `TASKS.md` de uma feature em cadeia automática, partindo do bundle
`./.aidev/{slug}/` (`SPEC.md` + `PLAN.md` + `TASKS.md`). O `SPEC.md` é o
**contexto primário** — o contrato de comportamento contra o qual a
implementação corre; o PRD só é aberto sob demanda quando o SPEC o referencia.
Para cada task elegível: roda os passos, executa o bloco Validação, e marca
`[X]` se tudo passar. Em falha, tenta corrigir em até 5 ciclos com execução
seletiva de testes; se esgotar ou bater em lacuna no SPEC, pausa, registra
nota no `TASKS.md` e devolve controle.

A skill **cria commit automático** ao fim de cada task aprovada (semantic
commit, uma linha, sem assinatura IA), mas **não edita o SPEC/PRD** (papel de
`escrever-prd`/`preparar-execucao`) e **não muda a estrutura do PLAN ou
TASKS** (papel de `preparar-execucao`). Marca `[X]` em passos, validações e
títulos e adiciona blocos de pausa quando necessário.

## Papel no fluxo spec-driven

O fluxo é: `escrever-prd` (opcional) → `preparar-execucao` →
**`implementar-task`** → `validar-implementacao`. Esta é a terceira peça —
assume que `preparar-execucao` já gerou o bundle `SPEC.md` + `PLAN.md` +
`TASKS.md` em `./.aidev/{slug}/`. O PRD é **opcional**: quando existe
(`prd:` no frontmatter do bundle aponta um slug), é a fonte de verdade e é
lido sob demanda; quando `prd: none` (projeto pequeno), o `SPEC.md` é a
própria fonte de verdade.

Princípios herdados:

- **Imutabilidade do PRD em `concluído`** — PRD com `status: concluído`
  não roda. Mudanças de comportamento abrem novo PRD.
- **IDs estáveis** — IDs de task (`T01`, `T02`...) e de US (`US01`...)
  não mudam. A skill referencia esses IDs em notas de pausa e relatórios.
- **`TASKS.md` + commit por task formam o checkpoint de progresso** —
  marcação `[X]` granular permite retomada fina dentro de uma task;
  o commit consolida a task inteira quando verde e marca o limite
  entre tasks no histórico do git.
- **Transição limitada do PRD** — só promove `pronto → em-progresso`.
  A promoção para `concluído` é da `validar-implementacao`.
- **Commit só sob task verde, escopo fechado** — nunca commita com
  passo ou validação falhando, nunca em pausa, e nunca inclui arquivos
  fora de "Arquivos Afetados" do PLAN. Sem `git add -A`.

## Entrada

`$ARGUMENTS` — se fornecido, tratar como referência ao slug do bundle
(número/slug do PRD, slug da feature, ou caminho em `./.aidev/`). Se ausente:

- **Único diretório em `./.aidev/`** → autodetecta esse slug.
- **Múltiplos diretórios** → listar e pedir ao usuário qual usar.
- **Nenhum diretório** → abortar sugerindo invocar `preparar-execucao`.

A skill não declara modo "primeira execução" vs "retomada" — detecta
automaticamente pela presença de notas de pausa e de marcações `[X]`
no `TASKS.md`. Em qualquer invocação, sempre reavalia as skills relevantes
ao bundle (passo 2b) e re-executa a linha de base verde (otimização A)
antes de iniciar a próxima task elegível.

## Fluxo de Execução

### 1. Localização do slug e validação do bundle/PRD

1. Resolver o slug a partir de `$ARGUMENTS` ou autodetecção em
   `./.aidev/`.
2. Ler o `SPEC.md` do bundle e o campo `prd:` do frontmatter.
3. **PRD é opcional.** Só validar o PRD quando `prd:` aponta um slug (não
   `none`):
   - Localizar o PRD em `./docs/prds/{prd}.md` (ou caminho convencional). Se
     o SPEC referencia um PRD que sumiu, **pausar** com `lacuna-spec` e pedir
     que o usuário reconcilie (via `preparar-execucao`) ou ajuste o SPEC.
   - Ler o `status` do PRD:
     - `concluído` → **abortar**. PRDs concluídos são imutáveis.
     - `rascunho` → **pedir confirmação explícita** ("PRD ainda em rascunho.
       Executar mesmo assim? Recomendo finalizar via `escrever-prd` antes.").
       Sem confirmação, abortar.
     - `pronto` → **promover para `em-progresso`** antes da primeira task
       (editar apenas o frontmatter; não tocar no corpo).
     - `em-progresso` → prosseguir.
   - Quando `prd: none` (projeto pequeno), **pular** a validação de PRD — o
     `SPEC.md` é a fonte de verdade.

### 2. Carregamento de contexto e checagem de coerência estrutural

1. Ler `./.aidev/{slug}/SPEC.md`, `./.aidev/{slug}/PLAN.md` e
   `./.aidev/{slug}/TASKS.md` integralmente — o `SPEC.md` é o **contexto
   primário** de comportamento. Se algum estiver ausente, abortar sugerindo
   `preparar-execucao`. O PRD **não** é carregado aqui; só sob demanda (passo 8
   e tratamento de lacuna).
2. Validar coerência estrutural:
   - Frontmatter de `SPEC.md`/`PLAN.md`/`TASKS.md` tem `prd:` consistente
     entre si.
   - IDs de task seguem padrão `T01`, `T02`, sequencial.
   - Toda `needs:` referencia ID existente no próprio TASKS.
   - Toda task tem bloco `Passos:` e `Validação:` não-vazios.
   - Toda `US` citada em "USs cobertas" existe no `SPEC.md`.
3. **Incoerência estrutural** → registrar nota de pausa com motivo
   `incoerencia-estrutural` na primeira task afetada e abortar
   sugerindo reconciliação via `preparar-execucao`.
4. Localizar o campo `Comando de teste:` em "Contexto Técnico Global"
   do `PLAN.md`. Esse campo é obrigatório (a `preparar-execucao` garante).
   Se vier `Sem suíte de testes detectada`, marcar internamente
   `sem_suite = true` e pular as otimizações A, B e C ao longo do fluxo.
   O commit por task continua saindo — a Validação intrínseca é o gate.
5. Verificar estado do working tree via `git status --porcelain`.
   - **Limpo** → seguir.
   - **Sujo com mudanças fora do escopo da próxima task elegível** →
     registrar pausa com motivo `working-tree-sujo` e abortar. Motivo:
     commits automáticos dependem de escopo limpo para não arrastar
     mudanças alheias. O usuário decide (commit manual à parte, stash
     ou descarte) e reinvoca a skill.
   - **Sujo apenas com arquivos dentro do escopo** (ex.: retomada após
     pausa que deixou edições parciais) → seguir; essas edições serão
     consolidadas pelo commit da task quando ela ficar verde.

### 2b. Avaliação e carga de skills relevantes (pré-execução)

Antes de rodar a primeira task, avaliar quais skills do catálogo atual se
aplicam a este bundle e carregá-las. A avaliação é **em execução-time** —
resolvida contra o catálogo vivo a cada invocação, **nunca** a partir de uma
lista gravada (uma lista no PLAN/bundle envelheceria contra o catálogo de
skills, que muda por conta própria).

1. **Inferir os domínios/concerns** do trabalho deste bundle a partir do que
   já foi carregado no passo 2: níveis das tasks (usuário/API/componente),
   passos, "USs cobertas", e principalmente "Arquivos Afetados" e "Contexto
   Técnico Global" do `PLAN.md` (stack, framework, ferramentas de teste).
   Ex.: "Python + pytest + API REST", "TypeScript + React + Playwright".
2. **Casar contra o catálogo de skills disponível na sessão** — comparar os
   domínios inferidos com as descrições das skills disponíveis e selecionar as
   que claramente cobrem o trabalho (boas práticas da linguagem, padrão de
   testes, um framework/serviço citado).
3. **Carregar** as skills selecionadas (invocá-las) antes de iniciar as tasks.
   A carga é **sugestão, não trava**: se durante a execução surgir necessidade
   de outra skill, invocá-la na hora.
4. **Nada é persistido** — não gravar a lista escolhida no PLAN, TASKS, SPEC
   nem em qualquer arquivo do bundle. A cada invocação (inclusive retomada) o
   passo roda de novo e resolve fresco; é idempotente com a re-execução da
   linha de base.

Racional do execução-time: nada gravado → nada envelhece contra o catálogo. E
como cada subagente do orquestrador paralelo (`orquestrar-execucao`) roda esta
skill no seu bundle, cada um executa este passo e carrega as skills certas do
**seu** escopo, sem depender de o auto-trigger acordar no contexto fresco do
subagente. Trade-off aceito: menos determinismo entre runs, em troca de sempre
usar a skill vigente.

Se nenhuma skill do catálogo casar com os domínios, seguir sem carga
adicional — não bloquear.

### 3. Linha de base verde (otimização A)

Se `sem_suite = false`:

1. Executar a suíte completa via `Comando de teste` antes da próxima
   task elegível.
2. Resultado verde → seguir.
3. Resultado vermelho → registrar nota de pausa com motivo
   `falha-pre-existente` na primeira task elegível e abortar.
   Falha pré-existente fora do escopo da task contamina o diagnóstico
   dos ciclos de correção.

Se `sem_suite = true`, pular este passo silenciosamente (o aviso já
foi dado na primeira invocação que detectou ausência de suíte).

### 4. Seleção da próxima task elegível

Task elegível = task `[ ]` no `TASKS.md` cujas dependências (`needs:`)
estão todas com `[X]` no título, ou cujo `needs:` é `—`.

- **Nenhuma elegível** (todas `[X]` ou todas bloqueadas por
  dependência aberta) → ir direto ao passo 8 (gate final).
- **Grupo de tasks `[P]` elegíveis** → seguir para passo 4a.
- **Task sem `[P]` elegível** → seguir para passo 5.

### 4a. Execução de grupo paralelo `[P]`

Quando uma ou mais tasks `[P]` estão elegíveis simultaneamente,
executá-las como grupo antes de prosseguir para tasks dependentes.

1. **Coletar o grupo**: todas as tasks `[ ]` com `[P]` cujo `needs:`
   está satisfeito neste momento.
2. **Executar o grupo**: para cada task do grupo, executar o ciclo
   completo de passos (passo 5) + validação (passo 6) + loop de
   correção se necessário (passo 7) + commit por task. A ordem de
   execução dentro do grupo segue a sequência do TASKS.md.
3. **Commit por task do grupo**: cada task do grupo gera seu próprio
   commit atômico ao ser concluída, seguindo as mesmas regras do
   passo 5 (semantic commit, apenas arquivos da task + TASKS.md).
4. **Após o grupo**: quando todas as tasks `[P]` do grupo estiverem
   `[X]` ou pausadas, reavalia elegibilidade — tasks que tinham
   `needs:` apontando para tasks do grupo agora podem estar elegíveis.
5. **Pausa dentro do grupo**: se qualquer task do grupo pausar, toda a
   cadeia pausa — não iniciar tasks dependentes do grupo incompleto.
   Registrar nota de pausa na task pausada conforme o protocolo do
   passo 9.

### 5. Execução de passos com feedback granular (otimização C)

Para cada passo `[ ]` da task selecionada, na ordem definida:

1. Executar a ação descrita no passo. Se o passo cita arquivo, editar
   o arquivo. Se cita comando, rodar.
2. Marcar `[X]` no checkbox do passo após conclusão.
3. **Feedback granular (C)**: se `sem_suite = false`, aplicar a
   cascata da seção 1 do `references/heuristicas-execucao.md` para
   inferir teste associado ao passo. Se inferiu, executar esse teste
   isoladamente:
   - Verde → seguir para o próximo passo.
   - Vermelho → vai direto para o passo 7 (loop de correção).
   - Sem teste inferido → seguir sem rodar nada.

**Pausa por lacuna durante os passos** — se a execução exige decisão
de negócio que o SPEC não cobre (ver critério operacional na seção
"Tratamento de pausa por lacuna no SPEC" abaixo), parar imediatamente
nesse passo (sem marcá-lo `[X]`) e seguir para o passo 9 sem passar
pela Validação.

### 6. Bloco Validação da task

Após todos os passos `[X]`:

1. Para cada item do bloco `Validação:`, executar conforme o tipo da
   task (código novo: testes citados; refatoração: suíte verde;
   infra: smoke/health check; documento: lint/revisão).
2. Marcar `[X]` em cada item da Validação que passar.
3. Todos os itens da Validação `[X]` → **marcar `[X]` no título da
   task**, **criar commit da task** (ver seção "Commit por task"
   abaixo e seção 5 de `references/heuristicas-execucao.md`), e voltar
   ao passo 4 (próxima elegível).
4. Algum item falha → ir para o passo 7 (loop de correção). **Não**
   marcar a task como concluída nem commitar.

### 7. Loop de correção (5 ciclos, otimização B)

Disparado quando o feedback granular (passo 5) ou a Validação (passo
6) falham.

Um **ciclo** = `{analisar erro → aplicar correção no código →
re-executar validação que falhou}`. Limite: 5 ciclos por task.

Para cada ciclo:

1. **Analisar** a mensagem de erro e o diff das tentativas anteriores
   nesta task. Não repetir correção já tentada.
2. **Aplicar** a correção no código (working tree, sem commit).
3. **Re-executar a validação que falhou usando o filtro seletivo (B)**.
   Construir o filtro conforme seção 2 do
   `references/heuristicas-execucao.md`. Sem casamento → aviso e
   fallback para suíte completa.
4. **Verde no filtro seletivo** → executar **uma vez** a suíte
   completa como gate final do ciclo:
   - Verde → marcar item da Validação `[X]` e voltar ao passo 6
     (continuar com os próximos itens da Validação) ou ao passo 4
     se todos itens passaram.
   - Vermelho → tratar como `regressao-fora-escopo`: registrar nota
     de pausa, **não consumir ciclo da task atual**, abortar a cadeia.
5. **Vermelho no filtro seletivo** → consumir 1 ciclo. Se ainda há
   ciclos disponíveis, voltar ao passo 1. Se esgotou os 5, ir para o
   passo 9 com motivo `esgotamento-ciclos`.

**Detecções especiais durante o loop:**

- **Erro fatal de infra** (comando não existe, timeout do test
  runner, falta de permissão, etc.): ir para o passo 9 com motivo
  `infra-erro-fatal`. **Não consumir ciclo** — não é problema do
  código.
- **Flaky detectado** (alternância passa/falha em ≥2 ciclos
  consecutivos com mesma input): ir para o passo 9 com motivo
  `flaky-detectado`. Pedir confirmação explícita do usuário antes
  de marcar `[X]` na próxima invocação.
- **Correção exigiria editar PLAN ou TASKS estruturalmente** (não
  só marcar `[X]`): ir para o passo 9 com motivo
  `incoerencia-estrutural` — `preparar-execucao` precisa reconciliar.

### 8. Gate final de critérios de aceite do SPEC

Disparado quando não há mais tasks elegíveis (todas `[X]` ou todas
bloqueadas).

1. Ler a tabela "Critérios de Aceite" (§5a) do `SPEC.md`.
2. Para cada critério, aplicar a heurística da seção 3 do
   `references/heuristicas-execucao.md` para classificar como
   **executável** ou **manual**.
3. Executar os critérios executáveis e reportar `OK | FALHA |
   ERRO_DE_EXECUÇÃO`. Listar os manuais como `verificação manual
   sugerida`.
4. **Gerar tabela de cobertura de USs**: cruzar todas as USs do `SPEC.md`
   contra o campo `USs cobertas:` de cada task do TASKS.md.

   ```
   | US    | Tasks     | Status          |
   |-------|-----------|-----------------|
   | US01  | T01, T02  | ✓ coberta       |
   | US02  | T03       | ✓ coberta       |
   | US03  | T04       | ✗ não entregue  |
   ```

   US sem tasks associadas → sinal de lacuna de planejamento. Reportar
   ao usuário antes de considerar a cadeia concluída.

5. **Atualizar `docs/MEMORY.md`** (criar se não existir a partir de
   `references/template-memory.md`):
   - Mover o conteúdo de `## Sessão atual` para `## Decisões` ou
     `## Lições`, conforme o tipo de informação registrada.
   - Limpar `## Sessão atual`.
   - Registrar em `## Decisões` as escolhas de abordagem técnica do
     PLAN que forem relevantes para features futuras.

6. Devolver controle ao usuário com:
   - Resumo do estado da cadeia (quantas tasks `[X]`, quantas
     pausadas, quantas bloqueadas).
   - Tabela de cobertura de USs.
   - Resultado dos critérios técnicos.
   - Lembrete de que a transição para `concluído` é responsabilidade
     da `validar-implementacao`.

### 9. Pausa: registro e devolução de controle

Toda pausa segue o mesmo protocolo:

1. **Preservar todos os `[X]` já marcados** em passos e validações.
   Não reverter trabalho.
2. **Não marcar `[X]` no título da task** — task fica `[ ]`.
3. **Aplicar detecção de drift** (seção 4 do `heuristicas-execucao.md`)
   para capturar `mtime` atuais do `SPEC.md`, do `TASKS.md` e do PRD
   (quando `prd:` aponta um slug) no `Snapshot` da nota.
4. **Registrar bloco de pausa** no `TASKS.md` ao final da task em
   pausa, conforme `references/template-nota-pausa.md`. Notas são
   **acumulativas** — nunca sobrescrever pausa anterior.
5. **Atualizar `docs/MEMORY.md`** (criar se não existir a partir de
   `references/template-memory.md`): registrar em `## Sessão atual`
   a feature em andamento, a última task concluída e o motivo da pausa.
6. **Pausar a cadeia inteira** — não pular para próxima task.
7. **Devolver controle** com:
   - Identificação do problema (motivo + descrição).
   - Sugestões de próxima ação adequadas ao motivo (ver seção
     "Tratamento de pausa por lacuna no SPEC" para o caso `lacuna-spec`).
   - Estado preservado para retomada.

### 10. Retomada (segunda invocação em diante)

Acionada automaticamente quando `PLAN.md`/`TASKS.md` já existem.

1. Aplicar detecção de drift (seção 4 do `heuristicas-execucao.md`).
   Se houver drift no `SPEC.md` (ou no PRD, quando existe), **interromper
   antes de tudo** e sugerir `preparar-execucao` em modo reconciliação.
2. Carregar `docs/MEMORY.md` se existir — a seção `## Sessão atual`
   fornece contexto da pausa anterior sem necessidade de reler todo
   o TASKS.md.
3. Localizar e exibir as notas de pausa anteriores como contexto
   ("Última pausa em T03 em 2026-04-17 14:30, motivo
   `esgotamento-ciclos`. Detalhes: ..."). Notas antigas **nunca** são
   apagadas — ficam como histórico.
4. Perguntar se o usuário quer retomar do ponto exato ou revisar
   SPEC/PLAN antes (sugerindo a skill apropriada).
5. Confirmação de retomada → re-executar linha de base verde (passo 3),
   selecionar próxima task elegível (passo 4), seguir o fluxo normal.
6. Caso especial: **todas as tasks já estão `[X]`** → pular direto ao
   gate final (passo 8).

## Regras transversais

### Fonte de verdade: SPEC (primário), PLAN, TASKS — PRD/TRD sob demanda

**Regra zero da skill, acima de qualquer otimização.**

O `SPEC.md` é o contrato de comportamento e o **contexto primário**; PLAN e
TASKS completam o roteiro técnico. A skill **nunca** inventa informação que não
esteja explícita nesses documentos. O **PRD** (quando existe) e o **TRD**
(quando o PLAN o referencia) são carregados **sob demanda** — o PRD para o
*porquê* de uma regra, o TRD para contexto técnico global.

Quando precisa de informação que não está clara:

1. **Releia primeiro** — SPEC, PLAN, TASKS, e qualquer arquivo citado em
   "Arquivos Afetados" do PLAN. Se o *porquê* de uma regra for necessário e
   houver PRD, abrir o PRD referenciado. A resposta normalmente está num
   documento que ainda não foi lido na sessão atual.
2. **Use as heurísticas documentadas** em
   `references/heuristicas-execucao.md` quando o sinal é técnico
   (path de teste, filtro seletivo, classificação de critério). As
   heurísticas têm fallback explícito quando o sinal não aparece —
   nunca chutar quando o fallback se aplica.
3. **Trate como lacuna** quando, mesmo após releitura e aplicação
   das heurísticas, a informação necessária para uma decisão de
   negócio está faltando ou ambígua no SPEC. Disparar a pausa de US03
   (motivo `lacuna-spec`) e devolver controle ao usuário com as opções:
   quando **há PRD**, editar o PRD via `escrever-prd` e reconciliar via
   `preparar-execucao`; quando **não há PRD**, ajustar o SPEC via
   `preparar-execucao`; ou decidir inline registrando a premissa.

Não preencher silenciosamente. Não assumir intenção do usuário.
Não inferir regra de negócio a partir do código existente — código
é implementação de uma decisão; a decisão mora no SPEC (e, quando existe,
no PRD que o embasa).

### Marcação `[X]` (granularidade e ordem)

A skill marca `[X]` em três níveis:

1. **Passo** — após executar o passo com sucesso (ou após o teste
   associado passar, quando C está ativo).
2. **Item da Validação** — após o critério ser verificado verde.
3. **Título da task** — apenas quando todos os passos e todas as
   validações estão `[X]`.

Nunca marcar nível superior antes do inferior. Nunca desmarcar `[X]`
existente, com **uma única exceção**: o `[X]` do **título** da task é
revertido quando o commit automático da task falha (pausa
`falha-commit`), porque o título sinaliza consolidação que não
aconteceu. `[X]` de passos e itens de Validação permanecem mesmo
nesse caso — o trabalho está feito, só não entrou em commit.

### Commit por task (consolidação do progresso)

Toda task com todos os passos `[X]`, todas as validações `[X]` e
título `[X]` gera **um commit automático** consolidando o trabalho
daquela task. O commit:

- Usa **semantic commit** em uma linha, sem corpo, sem assinatura IA
  (segue o `CLAUDE.md` do usuário).
- Inclui **só os arquivos do escopo da task** — a interseção entre
  "Arquivos Afetados" do `PLAN.md` e o que foi efetivamente modificado
  no working tree — mais o `./.aidev/{slug}/TASKS.md` (para registrar
  o avanço da marcação no próprio commit).
- Nunca usa `git add -A` — arrasta arquivos não relacionados.
- Nunca passa `--no-verify`, `--no-gpg-sign` ou flags equivalentes:
  um hook falhando é sinal de problema real no código, não obstáculo
  a burlar.

Formato da mensagem, tabela **Nível → tipo semantic**, regras de
escopo de arquivos e exemplos estão na seção 5 de
`references/heuristicas-execucao.md`.

**Quando `sem_suite = true`**: o commit continua saindo normalmente —
as otimizações por testes são puladas, mas o bloco Validação da task
é executado e serve como gate.

**Falha no commit** (pre-commit hook rejeita, signing falha,
permissão negada, caminho ausente, etc.) → tratar como pausa
`falha-commit`:

1. **Reverter o `[X]` do título** da task para `[ ]`. Passos e
   validações `[X]` permanecem.
2. Registrar bloco de pausa com motivo `falha-commit` conforme
   `references/template-nota-pausa.md`. `Erro final` captura stderr
   relevante; a variante do motivo inclui o comando que falhou.
3. **Não** consumir ciclo do loop de correção — é pausa informativa,
   não falha de código da task.
4. **Não** tentar recommitar automaticamente — se o hook rejeitou, o
   autor precisa investigar.
5. Devolver controle ao usuário.

### Bloco de nota de pausa

Formato canônico em `references/template-nota-pausa.md`. Vocabulário
controlado de motivos: `esgotamento-ciclos`, `lacuna-spec`,
`interrupcao-manual`, `regressao-fora-escopo`, `infra-erro-fatal`,
`flaky-detectado`, `incoerencia-estrutural`, `falha-pre-existente`.
Nunca usar texto livre como motivo.

### Análise entre ciclos

Cada ciclo do loop de correção começa lendo o erro atual e os diffs
das correções anteriores **na mesma task**. Não repetir correção já
tentada. Se o agente percebe que está repetindo a mesma estratégia
com pequenas variações estéticas (renomeação, reorganização sem
mudança lógica), é sinal de loop estéril — pular direto para o passo
9 com motivo `esgotamento-ciclos`, mesmo antes do 5º ciclo.

### Detecção de drift entre invocações

Aplicar regra da seção 4 do `references/heuristicas-execucao.md`.
Comparação por `mtime` capturado no `Snapshot` da última nota de
pausa. Drift no `SPEC.md` (ou no PRD, quando existe) interrompe antes de
qualquer execução; drift no TASKS exige confirmação do usuário; drift em
ambos exige reconciliação.

### Saída ao usuário (formato curto e fixo)

Toda devolução de controle (sucesso, pausa, gate final) usa o mesmo
formato compacto:

```
Estado: <task atual TNN | cadeia concluída | pausa em TNN>
Motivo: <quando aplicável, vocabulário controlado>
Próxima ação sugerida: <1 linha>
Notas relevantes: <últimas 2 notas de pausa, se houver, ou "nenhuma">
```

Sem narração extensa, sem emoji.

### Tratamento de pausa por lacuna no SPEC (US03)

Lacuna = (a) Rule citada na task referencia comportamento ausente do
`SPEC.md`, (b) Edge case da task contradiz o estado atual do código, ou
(c) Validação requer decisão de negócio não documentada no SPEC. **Não**
pausar por preferência estilística ou dúvida técnica menor — só
quando continuar exigiria inventar regra de negócio.

Ao detectar:

1. Registrar pausa com motivo `lacuna-spec` (sem consumir ciclo).
2. Apresentar ao usuário as opções, conforme haja ou não PRD:
   - **Com PRD** — editar o PRD via `escrever-prd` para sanar a lacuna e
     reconciliar o bundle via `preparar-execucao`.
   - **Sem PRD** — ajustar o `SPEC.md` via `preparar-execucao` (o SPEC é a
     fonte de verdade).
   - Reconciliar PLAN+TASKS via `preparar-execucao` quando a lacuna afeta
     escopo ou estrutura, não só uma task.
   - Decidir inline informando a premissa — a skill registra a premissa na
     nota de pausa (linha extra `> Premissa registrada inline: ...`) e retoma
     na próxima invocação.

A skill **não edita** o SPEC nem o PRD para suprir a lacuna em nenhuma hipótese.

## Fora do escopo

Esta skill **não**:

- Cria commits fora do ciclo "task verde" — nada de commits
  intermediários, commits de progresso parcial, commits de pausa ou
  squash retroativo. O usuário pode fazer commits manuais entre
  invocações (a skill detecta via working tree limpo e prossegue).
- Edita o SPEC ou o PRD (nem para suprir lacuna; papel de
  `preparar-execucao`/`escrever-prd`).
- Edita estruturalmente o PLAN ou o TASKS (papel de `preparar-execucao`).
  Só marca `[X]` em passos/validações/títulos e adiciona blocos de
  pausa no `TASKS.md`.
- Promove o status do PRD/SPEC para `concluído` (papel de
  `validar-implementacao`).
- Executa em PRD com `status: concluído` (imutável) ou em `rascunho`
  sem confirmação explícita.
- Impõe TDD ou ordem "teste antes do código" — usa testes como sinal
  quando existem, sem ditar estilo.
- Faz validação global de coerência código↔SPEC/PRD ou auditoria de
  qualidade ampla no fechamento (papel de `validar-implementacao`).
- Gera ou atualiza TRD.

## Templates e heurísticas de referência

Consultar sempre que o fluxo invocar:

- `references/template-nota-pausa.md` — formato canônico do bloco
  de pausa, vocabulário controlado de motivos, variantes por motivo.
- `references/heuristicas-execucao.md` — regras operacionais para
  inferir teste por passo (C), construir filtro seletivo (B),
  interpretar critérios de aceite do SPEC no gate final, e detectar
  drift entre invocações.
- `references/template-memory.md` — estrutura canônica do
  `docs/MEMORY.md`. Usar ao criar o arquivo pela primeira vez.
