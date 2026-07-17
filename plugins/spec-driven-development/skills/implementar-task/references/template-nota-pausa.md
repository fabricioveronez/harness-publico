# Template Nota de Pausa

Estrutura canônica do bloco que a skill `implementar-task` registra ao
final de uma task no `TASKS.md` quando precisa devolver controle ao
usuário antes de marcar a task como `[X]`.

## Onde inserir

A nota é um **blockquote markdown anexado ao final do bloco da task**,
depois da Validação e antes da próxima `## [ ] T...` (ou do fim do
arquivo, se for a última task).

```markdown
## [ ] T03: implementar handler /api/users
- **USs cobertas:** US02
- **Nível:** API
- **needs:** T02
- **Passos:**
  - [X] criar arquivo do handler
  - [X] registrar rota no router
  - [ ] adicionar middleware de auth
- **Validação:**
  - [ ] teste de integração `users.spec.ts`

> Pausa em 2026-04-19 14:30: esgotamento-ciclos — handler retorna 500 quando body vem vazio.
> Ciclos consumidos: 5. Última ação: passo T03.3.
> Erro final: TypeError: Cannot read property 'email' of undefined.
> Snapshot: SPEC mtime 2026-04-18 09:12, TASKS mtime 2026-04-19 14:25.

## [ ] T04: ...
```

## Princípios

- **Acumulativa, nunca sobrescrita.** Cada nova pausa na mesma task
  vira um novo blockquote abaixo do anterior. Histórico auditável é o
  ponto — nunca apagar pausa antiga ao registrar nova.
- **Inserida só dentro do escopo da task em pausa.** A skill não
  reescreve outras tasks ao registrar uma nota.
- **Preserva os `[X]` já marcados nos passos e validações.** A pausa
  diz "parei aqui", não "desfiz o que foi feito".
- **Nunca aparece no título da task.** O `[ ]` no título permanece
  enquanto a task não foi totalmente concluída — a nota substitui o
  `[X]` como sinal de "houve atividade aqui que parou no meio".

## Formato canônico

```
> Pausa em YYYY-MM-DD HH:MM: <motivo> — <descrição curta ≤120 chars>.
> Ciclos consumidos: N. Última ação: <passo TNN.M ou "Validação item K">.
> Erro final: <resumo ≤2 linhas, ou "—" quando não houver erro técnico>.
> Snapshot: SPEC mtime YYYY-MM-DD HH:MM, TASKS mtime YYYY-MM-DD HH:MM, PRD mtime YYYY-MM-DD HH:MM.
```

> O campo `PRD mtime` só entra quando `prd:` aponta um slug; em projeto sem PRD
> (`prd: none`), o `Snapshot` registra só `SPEC` e `TASKS`.

Regras de escrita:

- **Timestamp** em horário local do agente, formato `YYYY-MM-DD HH:MM`.
- **`<motivo>`** é um valor do vocabulário controlado abaixo — nunca
  texto livre.
- **`<descrição curta>`** ≤ 120 caracteres. Resumo em 1 frase do que
  estava acontecendo.
- **`Última ação`** identifica o ponto exato — `Tnn.M` para passos
  (T03.3 = 3º passo da T03), `Validação item K` para itens da Validação
  (`Validação item 1`).
- **`Erro final`** é a 1ª linha relevante do erro original, ou um
  resumo de até 2 linhas. Quando a pausa não tem erro técnico
  (ex.: lacuna, interrupção manual), registrar `—`.
- **`Snapshot`** captura `mtime` (timestamp de modificação) do `SPEC.md`
  (contrato primário), do `TASKS.md` e do PRD (quando há PRD) no momento da
  pausa. Usado pela retomada para detectar drift — sem `Snapshot`, a skill não
  consegue distinguir retomada limpa de retomada após edição manual.

## Vocabulário controlado de `<motivo>`

| Motivo | Quando usar |
|---|---|
| `esgotamento-ciclos` | Loop de correção rodou as 5 tentativas e a validação seletiva ainda falha. |
| `lacuna-spec` | Detectada ambiguidade, contradição ou regra ausente no PRD que bloqueia decisão. |
| `interrupcao-manual` | Usuário cancelou (Ctrl+C, `/stop` etc.) no meio de uma task. Anotada na próxima invocação se possível. |
| `regressao-fora-escopo` | Validação seletiva ficou verde mas a suíte completa pegou regressão em outra área. |
| `infra-erro-fatal` | Comando de teste não existe, timeout, falta de permissão, etc. Não consome ciclo. |
| `flaky-detectado` | Validação alternou passa/falha em ≥2 ciclos consecutivos com mesmo input. |
| `incoerencia-estrutural` | TASKS.md ou PLAN.md em formato incoerente com PRD 001 (ex.: `needs:` aponta para ID inexistente). |
| `falha-pre-existente` | Linha de base verde (otimização A) detectou falha de teste fora do escopo da task antes de iniciar. |
| `falha-commit` | O commit automático da task falhou (pre-commit hook, signing, permissão, etc.). O `[X]` do título é revertido; passos e validações permanecem. |
| `working-tree-sujo` | Working tree continha mudanças fora do escopo da próxima task elegível na invocação. A skill não commita para não arrastar — usuário decide (commit manual, stash, descarte) e reinvoca. |

## Variantes por motivo

### `lacuna-spec` — adiciona linha de premissa quando o usuário decide inline

Quando o usuário, ao retomar, escolhe a opção "decidir inline" em vez de
editar o PRD ou reconciliar o PLAN, a skill registra a premissa
assumida em uma linha extra antes da `Snapshot`:

```
> Pausa em 2026-04-19 10:05: lacuna-spec — Rule "rate limit por IP" não define janela de tempo.
> Ciclos consumidos: 0. Última ação: passo T05.2.
> Erro final: —.
> Premissa registrada inline: assumida janela de 60 segundos por IP.
> Snapshot: SPEC mtime 2026-04-18 09:12, TASKS mtime 2026-04-19 10:00.
```

### `esgotamento-ciclos` — adiciona resumo de tentativas

Quando a pausa vem de 5 ciclos consumidos, adicionar uma linha
resumindo as correções tentadas para evitar repetição em retomadas
manuais:

```
> Pausa em 2026-04-19 14:30: esgotamento-ciclos — handler retorna 500 com body vazio.
> Ciclos consumidos: 5. Última ação: passo T03.3.
> Erro final: TypeError: Cannot read property 'email' of undefined.
> Tentativas: (1) early return; (2) optional chaining; (3) defaults; (4) zod schema; (5) middleware de validação.
> Snapshot: SPEC mtime 2026-04-18 09:12, TASKS mtime 2026-04-19 14:25.
```

### `falha-commit` — registra comando e stderr do hook

Adicionar uma linha com o comando de commit tentado e uma linha com
um resumo do stderr do hook (se houver). Nunca registrar saída
completa — apenas o trecho que identifica a causa.

```
> Pausa em 2026-04-20 15:10: falha-commit — pre-commit hook recusou commit da T04.
> Ciclos consumidos: 0. Última ação: commit final da task.
> Erro final: eslint: 3 erros em src/api/users/create.ts (no-unused-vars).
> Comando: git commit -m "feat(implementar-task): mapear payloads de erro [T04]"
> Snapshot: SPEC mtime 2026-04-20 10:00, TASKS mtime 2026-04-20 15:08.
```

O `[X]` do título da task foi revertido para `[ ]` antes de registrar
a pausa; passos e validações `[X]` permanecem.

### `working-tree-sujo` — lista arquivos alheios encontrados

Adicionar uma linha com os arquivos fora do escopo detectados no
`git status --porcelain`. Suficiente para o usuário identificar o que
precisa tratar.

```
> Pausa em 2026-04-20 09:30: working-tree-sujo — mudanças fora do escopo impedem commit automático.
> Ciclos consumidos: 0. Última ação: checagem de working tree no passo 2.
> Erro final: —.
> Arquivos alheios: src/lib/cache.ts (modified), docs/notes.md (untracked).
> Snapshot: SPEC mtime 2026-04-19 18:00, TASKS mtime 2026-04-19 17:50.
```

### `regressao-fora-escopo` — adiciona path do teste regressor

```
> Pausa em 2026-04-19 16:00: regressao-fora-escopo — suíte completa quebrou após validação seletiva verde.
> Ciclos consumidos: 1. Última ação: Validação item 2.
> Erro final: AssertionError em billing.spec.ts: total deveria ser 100, recebeu 90.
> Teste regressor: tests/billing.spec.ts
> Snapshot: SPEC mtime 2026-04-18 09:12, TASKS mtime 2026-04-19 15:50.
```

## Exemplo completo (vários motivos na mesma task)

Tasks podem acumular várias pausas ao longo do tempo. Exemplo de uma
task que pausou três vezes antes de eventualmente concluir:

```markdown
## [ ] T07: integrar gateway de pagamento
- **USs cobertas:** US04
- **Nível:** API
- **needs:** T03
- **Passos:**
  - [X] criar cliente HTTP do gateway
  - [X] mapear payloads de erro
  - [ ] implementar retry com backoff
- **Validação:**
  - [ ] teste de integração com mock do gateway
  - [ ] suíte completa verde

> Pausa em 2026-04-15 11:20: lacuna-spec — PRD não define se idempotência é por order_id ou por hash do body.
> Ciclos consumidos: 0. Última ação: passo T07.2.
> Erro final: —.
> Snapshot: SPEC mtime 2026-04-15 09:00, TASKS mtime 2026-04-15 11:00.

> Pausa em 2026-04-16 09:45: lacuna-spec — Rule "retry com backoff" não define teto de tentativas.
> Ciclos consumidos: 0. Última ação: passo T07.3.
> Erro final: —.
> Premissa registrada inline: assumido máximo de 3 retries com backoff exponencial 200ms/400ms/800ms.
> Snapshot: SPEC mtime 2026-04-16 08:30, TASKS mtime 2026-04-16 09:30.

> Pausa em 2026-04-17 14:10: esgotamento-ciclos — retry estoura quando o gateway retorna 502 no 1º try.
> Ciclos consumidos: 5. Última ação: Validação item 1.
> Erro final: TimeoutError ao aguardar resposta do mock.
> Tentativas: (1) ajuste de timeout; (2) jitter; (3) reset de backoff; (4) circuit breaker; (5) ignorar 502 no 1º try.
> Snapshot: SPEC mtime 2026-04-17 09:00, TASKS mtime 2026-04-17 14:05.
```

A retomada exibe as três notas como contexto antes de perguntar ao
usuário se quer continuar do ponto da última pausa ou revisar o PRD/PLAN
primeiro.
