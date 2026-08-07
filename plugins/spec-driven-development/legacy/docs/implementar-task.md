# implementar-task

Executa as tasks de um `TASKS.md` em cadeia automática a partir do bundle `./.aidev/{slug}/`,
marcando `[X]` em passos, validações e títulos conforme avança. Carrega o `SPEC.md` como
**contexto primário** (o contrato: US Rules, Edge cases, critérios de aceite) e abre o PRD
**sob demanda**, só quando o SPEC o referencia e é preciso o porquê de uma regra. Respeita o
grafo `needs:` entre tasks e executa **grupos `[P]` em paralelo** quando elegíveis. Roda o bloco
Validação de cada task, entra em loop de correção de até 5 ciclos em falha, pausa em lacuna no
SPEC e, ao final de cada task verde, cria um commit semantic em uma linha (sem assinatura IA)
com os arquivos do escopo da task mais o `TASKS.md`.

No início de cada invocação avalia o catálogo de skills atual e carrega as relevantes ao domínio
do bundle (execução-time, nada persistido) — o que garante que cada instância paralela disparada
pela `orquestrar-execucao` use as skills certas do seu próprio bundle. SPEC, PLAN e TASKS são a
fonte de verdade (PRD/TRD sob demanda) — a skill nunca inventa informação.

## Pré-requisitos e configuração

- Um bundle `SPEC.md` + `PLAN.md` + `TASKS.md` gerado pela skill `preparar-execucao` em
  `./.aidev/{slug}/`.
- **Working tree limpo** (ou só com edições dentro do escopo da próxima task elegível) no início
  da cadeia. Mudanças alheias disparam pausa `working-tree-sujo`.
- **Linha de base verde.** A suíte de testes é executada antes da primeira task; resultado
  vermelho vira pausa `falha-pre-existente` e a cadeia aborta — falha pré-existente contaminaria
  o julgamento de cada task.
- **PRD é opcional.** Quando o `SPEC.md` tem `prd:` apontando um slug, a skill valida o `status`
  do PRD em `./docs/prds/` (`rascunho` exige confirmação; `concluido` é imutável e não roda;
  `pronto` → promove a `em-progresso`). Quando `prd: none` (projeto pequeno), o `SPEC.md` é a
  fonte de verdade e a validação de PRD é pulada.
- O `PLAN.md` deve conter o campo `Comando de teste:` em "Contexto Técnico Global" (preenchido
  pela `preparar-execucao`). Sem suíte de testes, registrar `Sem suíte de testes detectada` — a
  skill detecta e pula as otimizações por testes.

### `docs/MEMORY.md`

A skill **cria e mantém `docs/MEMORY.md`** — um arquivo **fora do bundle**, na árvore do
projeto, a partir de `references/template-memory.md`. Ele carrega a memória de execução entre
invocações:

- `## Sessão atual` é escrita a cada pausa (feature em andamento, última task concluída, motivo)
  e é o que a skill lê ao retomar, sem precisar reler o `TASKS.md` inteiro.
- No gate final, o conteúdo de `## Sessão atual` é promovido para `## Decisões` (escolhas de
  abordagem técnica do PLAN relevantes para features futuras) ou `## Lições`, e a seção é limpa.

## Dependências externas

- Test runner do projeto (opcional — se ausente, a skill detecta via `Comando de teste: Sem
  suíte de testes detectada` no PLAN e pula as otimizações por testes).
- `git` instalado e configurado (`user.name`, `user.email` e, quando o projeto exigir, chave de
  assinatura). A skill cria um commit por task verde e não passa `--no-verify` nem
  `--no-gpg-sign`.

## Skills relacionadas

- **preparar-execucao** — gera o bundle `SPEC.md`+`PLAN.md`+`TASKS.md` consumido por esta skill;
  é também quem reconcilia estrutura em caso de lacuna ou drift.
- **orquestrar-execucao** — dispara esta skill em paralelo, uma instância por fatia, cada uma
  isolada num git worktree, quando a decomposição tem 2+ fatias.
- **escrever-prd** — opcional; gera o PRD que embasa o SPEC (projeto grande).
- **validar-implementacao** — valida coerência código↔contrato ao fim, ajusta drift e promove o
  status para `concluido`. Fora do escopo desta skill.

## Exemplos de uso

```
Implementa as tasks do PRD 002

Roda o plano da feature de autenticação

Executa o TASKS.md em .aidev/003-pagamentos

Continua de onde parou

Tocar a implementação da feature que acabamos de preparar

Retoma a execução — pausamos ontem por uma lacuna no SPEC
```

### Retomada e detecção de drift

Ao ser reinvocada com `PLAN.md`/`TASKS.md` já existentes, a skill **primeiro checa drift**: se o
`SPEC.md` (ou o PRD, quando existe) mudou desde a última pausa, ela **interrompe antes de
qualquer coisa** e sugere `preparar-execucao` em modo reconciliação. Só então carrega o
`docs/MEMORY.md`, exibe as notas de pausa anteriores como contexto (nunca apagadas — ficam como
histórico), pergunta se o usuário quer retomar do ponto exato ou revisar SPEC/PLAN antes, e
segue o fluxo normal. Com todas as tasks já `[X]`, pula direto para o gate final.

### Gate final

Ao terminar a cadeia, além de rodar os critérios de aceite do SPEC, a skill monta uma **tabela
de cobertura de USs** (`US | Tasks | Status`). US sem task associada é reportada como **lacuna
de planejamento** antes de a cadeia ser considerada concluída.

## Limitações conhecidas

- Cria **um commit por task verde** (semantic commit, uma linha, sem assinatura IA), com os
  arquivos da interseção "Arquivos Afetados" do PLAN ∩ working tree + `TASKS.md`. Commits
  intermediários, de pausa ou de progresso parcial não acontecem — o `TASKS.md` marca progresso
  granular com `[X]` dentro da task.
- Falha no commit (pre-commit hook, signing, permissão) vira pausa `falha-commit`, reverte o
  `[X]` do título da task (passos e validações permanecem `[X]`) e devolve controle. A skill
  nunca passa `--no-verify`/`--no-gpg-sign`.
- **Vocabulário controlado de motivos de pausa** — nunca texto livre: `esgotamento-ciclos`,
  `lacuna-spec`, `interrupcao-manual`, `regressao-fora-escopo`, `infra-erro-fatal`,
  `flaky-detectado`, `incoerencia-estrutural`, `falha-pre-existente` (além de
  `working-tree-sujo` e `falha-commit` no fluxo de entrada e de commit).
- Não edita o SPEC nem o PRD, nem para suprir lacuna — em `lacuna-spec`, pausa e oferece os
  caminhos: com PRD, editar via `escrever-prd` + reconciliar via `preparar-execucao`; sem PRD,
  ajustar o `SPEC.md` via `preparar-execucao`; ou decidir inline registrando a premissa.
- Não muda a estrutura do PLAN ou TASKS — só marca `[X]` em passos/validações/títulos e
  adiciona blocos de pausa. Reordenar tasks, criar novas ou reescrever passos é responsabilidade
  da `preparar-execucao` (incoerência estrutural vira pausa `incoerencia-estrutural`).
- **Pausa dentro de um grupo `[P]` para a cadeia inteira** — o paralelismo de tasks acontece
  dentro do bundle, mas o grupo só é considerado fechado quando todas as suas tasks estão `[X]`.
- Não promove o status para `concluido` — só transiciona o PRD `pronto → em-progresso` (quando
  há PRD). A promoção final é responsabilidade da `validar-implementacao`, que também é quem faz
  a validação **global** de coerência código↔SPEC/PRD — o gate final aqui é por task e por
  critério, não uma auditoria ampla.
- O gate final de "Critérios de Aceite do SPEC" (§5a) só executa critérios programaticamente
  verificáveis (com comando entre crase, verbo de execução ou path plausível). Critérios manuais
  (ex.: "verificação visual", "p99 em prod") são listados como `verificação manual sugerida`,
  não rodados.
- Em projeto sem suíte de testes (`Comando de teste: Sem suíte de testes detectada` no PLAN), as
  três otimizações baseadas em testes (linha de base verde, execução seletiva, feedback
  granular) são puladas; a Validação intrínseca de cada task continua sendo o gate.
- A avaliação de skills é **execução-time e não persistida** — resolve contra o catálogo vigente
  a cada invocação. Nada é gravado no bundle (nem hint, que envelheceria). O trade-off é menos
  determinismo entre runs em troca de sempre usar a skill atual; se nenhuma skill do catálogo
  casar com o domínio, a skill segue sem carga adicional.

### Referências da skill

- `references/heuristicas-execucao.md` — loop de correção, detecção de drift e otimizações por
  testes.
- `references/template-nota-pausa.md` — formato da nota de pausa e variantes por motivo.
- `references/template-memory.md` — estrutura do `docs/MEMORY.md`.
