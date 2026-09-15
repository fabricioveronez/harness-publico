# Template — Nota de pausa

Bloco que o modo Implementar anexa ao fim do bloco da task no `TASKS.md` quando
precisa devolver o controle antes de marcar a task como `[X]`.

## Onde entra

Blockquote depois da `Validação:` e antes da próxima `## [ ] T...` (ou do fim do
arquivo). **Acumulativo**: cada nova pausa na mesma task vira um blockquote novo
abaixo do anterior. Nunca sobrescreva a anterior — o histórico é o que permite
não repetir a mesma correção na retomada seguinte.

## Formato

```
> Pausa em YYYY-MM-DD HH:MM: <motivo> — <descrição ≤120 chars>.
> Ciclos consumidos: N. Última ação: <TNN.M | Validação item K>.
> Erro final: <resumo ≤2 linhas, ou "—">.
> Snapshot: SPEC sha <hash12>, TASKS sha <hash12>, PRD sha <hash12>.
```

O `Snapshot` guarda **hash de conteúdo**, não `mtime`:

```bash
git hash-object .aidev/{slug}/SPEC.md | cut -c1-12                    # SPEC: do disco
git show HEAD:.aidev/{slug}/TASKS.md | git hash-object --stdin | cut -c1-12   # TASKS: de HEAD
```

O `TASKS.md` sai de **HEAD**, não do disco, porque o snapshot é gravado dentro
dele: tirar do disco faria toda retomada acusar drift no TASKS por causa da
própria nota que acabou de ser escrita.

`git checkout`, `git worktree add` e clone reescrevem timestamp sem mudar uma
linha. Com `mtime`, toda fatia de toda onda paralela acusaria drift no SPEC e a
execução pararia antes de começar, por uma mudança que não houve. `PRD sha` só
entra quando `prd:` aponta um slug.

## Vocabulário controlado de motivo

Texto livre é proibido: o motivo é lido pelo relatório de orquestração e pela
retomada.

| Motivo | Quando |
|---|---|
| `esgotamento-ciclos` | 5 ciclos de correção e a validação seletiva ainda falha |
| `lacuna-spec` | falta regra de negócio no contrato para decidir |
| `interrupcao-manual` | usuário cancelou no meio de uma task |
| `regressao-fora-escopo` | seletivo verde, suíte completa pegou regressão alhures |
| `infra-erro-fatal` | comando ausente, timeout, permissão negada — não consome ciclo |
| `flaky-detectado` | alterna passa/falha em ≥2 ciclos com mesmo input |
| `incoerencia-estrutural` | TASKS/PLAN incoerentes (ex.: `needs` para ID inexistente) |
| `falha-pre-existente` | linha de base já estava vermelha antes da task |
| `falha-commit` | commit rejeitado (hook, signing, permissão) |
| `working-tree-sujo` | mudanças fora do escopo da próxima task elegível |

## Variantes

**`lacuna-spec` com decisão inline** — acrescente antes do `Snapshot`:

```
> Premissa registrada inline: assumida janela de 60 segundos por IP.
```

**`esgotamento-ciclos`** — acrescente o resumo das tentativas, para a retomada não
repetir:

```
> Tentativas: (1) early return; (2) optional chaining; (3) defaults; (4) schema; (5) middleware.
```

**`falha-commit`** — acrescente o comando exato:

```
> Comando: git commit -m "feat(toil-sync): mapear payloads de erro [T04]"
```

O `[X]` do **título** foi revertido antes de registrar; os `[X]` de passos e
validações permanecem.

**`working-tree-sujo`** — acrescente os arquivos alheios encontrados:

```
> Arquivos alheios: src/lib/cache.ts (modified), docs/notes.md (untracked).
```

**`regressao-fora-escopo`** — acrescente o teste regressor:

```
> Teste regressor: tests/billing.spec.ts
```

## Exemplo

```markdown
## [ ] T07: integrar gateway de pagamento
- **USs cobertas:** US04
- **Nível:** API
- **needs:** T03
- **Passos:**
  - [X] criar cliente HTTP
  - [ ] implementar retry com backoff
- **Validação:**
  - [ ] CA05

> Pausa em 2026-08-07 11:20: lacuna-spec — contrato não define teto de tentativas do retry.
> Ciclos consumidos: 0. Última ação: T07.2.
> Erro final: —.
> Premissa registrada inline: assumido máximo de 3 retries, backoff 200/400/800ms.
> Snapshot: SPEC sha 8f3a1c02b471, TASKS sha 22d9e7c1a0f3.

> Pausa em 2026-08-07 14:10: esgotamento-ciclos — retry estoura com 502 na primeira tentativa.
> Ciclos consumidos: 5. Última ação: Validação item 1.
> Erro final: TimeoutError aguardando resposta do mock.
> Tentativas: (1) timeout; (2) jitter; (3) reset de backoff; (4) circuit breaker; (5) ignorar 502.
> Snapshot: SPEC sha 8f3a1c02b471, TASKS sha 91b0d4ee27ac.
```
