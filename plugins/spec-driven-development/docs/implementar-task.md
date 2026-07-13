# implementar-task

Executa as tasks de um `TASKS.md` em cadeia automática a partir de `./.aidev/{slug}/`, marcando `[X]` em passos, validações e títulos conforme avança. Roda o bloco Validação de cada task, entra em loop de correção de até 5 ciclos em falha, pausa em lacuna no PRD e, ao final de cada task verde, cria um commit semantic em uma linha (sem assinatura IA) com os arquivos do escopo da task mais o `TASKS.md`. PRD, PLAN e TASKS são tratados como fonte única de verdade — a skill nunca inventa informação.

## Pré-requisitos e configuração

- PRD existente em `./docs/prds/{slug}.md` com `status: pronto` ou `em-progresso` (PRDs em `rascunho` exigem confirmação explícita; PRDs `concluído` são imutáveis e não rodam).
- `PLAN.md` e `TASKS.md` gerados pela skill `criar-plan` em `./.aidev/{slug}/`.
- O `PLAN.md` deve conter o campo `Comando de teste:` em "Contexto Técnico Global" (preenchido automaticamente pela `criar-plan`). Sem suíte de testes no projeto, registrar `Sem suíte de testes detectada` — a skill detecta e pula as otimizações por testes.

## Dependências externas

- Test runner do projeto (opcional — se ausente, a skill detecta via `Comando de teste: Sem suíte de testes detectada` no PLAN e pula as otimizações por testes).
- `git` instalado e configurado (`user.name`, `user.email` e, quando o projeto exigir, chave de assinatura). A skill cria um commit por task verde e não passa `--no-verify` nem `--no-gpg-sign`.

## Skills relacionadas

- **escrever-prd** — gera o PRD que vira fonte de verdade da feature.
- **criar-plan** — gera o `PLAN.md`+`TASKS.md` consumidos por esta skill.
- **validar-implementacao** (futura) — valida coerência código↔PRD ao fim e promove o status do PRD para `concluído`. Fora do escopo desta skill.

## Exemplos de uso

```
Implementa as tasks do PRD 002

Roda o plano da feature de autenticação

Executa o TASKS.md em .aidev/003-pagamentos

Continua de onde parou

Tocar a implementação do PRD que acabamos de planejar

Retoma a execução — pausamos ontem por uma lacuna no PRD
```

## Limitações conhecidas

- Cria **um commit por task verde** (semantic commit, uma linha, sem assinatura IA), com os arquivos da interseção "Arquivos Afetados" do PLAN ∩ working tree + `TASKS.md`. Commits intermediários, de pausa ou de progresso parcial não acontecem — o `TASKS.md` marca progresso granular com `[X]` dentro da task.
- Exige working tree limpo (ou só com edições dentro do escopo da próxima task elegível) no início da cadeia. Mudanças alheias disparam pausa `working-tree-sujo` — usuário decide (commit manual, stash, descarte) e reinvoca.
- Falha no commit (pre-commit hook, signing, permissão) vira pausa `falha-commit`, reverte o `[X]` do título da task (passos e validações permanecem `[X]`) e devolve controle. A skill nunca passa `--no-verify`/`--no-gpg-sign`.
- Não edita o PRD nem para suprir lacuna — em lacuna, pausa e oferece três caminhos (editar PRD via `escrever-prd`, reconciliar via `criar-plan`, ou decidir inline registrando a premissa).
- Não muda a estrutura do PLAN ou TASKS — só marca `[X]` em passos/validações/títulos e adiciona blocos de pausa. Reordenar tasks, criar novas ou reescrever passos é responsabilidade da `criar-plan`.
- Não promove o status do PRD para `concluído` — só transiciona `pronto → em-progresso`. A promoção final é responsabilidade da `validar-implementacao`.
- O gate final de "Critérios técnicos do PRD" só executa critérios programaticamente verificáveis (com comando entre crase, verbo de execução ou path plausível). Critérios manuais (ex.: "verificação visual", "p99 em prod") são listados como `verificação manual sugerida`, não rodados.
- Em projeto sem suíte de testes (`Comando de teste: Sem suíte de testes detectada` no PLAN), as três otimizações baseadas em testes (linha de base verde, execução seletiva, feedback granular) são puladas; a Validação intrínseca de cada task continua sendo o gate.
