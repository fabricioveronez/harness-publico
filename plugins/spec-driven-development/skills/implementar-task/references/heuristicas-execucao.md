# Heurísticas de Execução

Regras operacionais que a skill `implementar-task` aplica em pontos
específicos do fluxo. Cada heurística tem (a) o sinal que ela busca,
(b) o fallback explícito quando o sinal não aparece e (c) um exemplo
curto. Nenhuma heurística autoriza a skill a inventar — quando o
fallback se aplica, a skill **avisa o usuário**.

---

## 1. Inferência de teste associado a um passo (otimização C)

A otimização C ("feedback granular por passo") só dispara quando a
skill consegue mapear um passo a um teste específico. A inferência
segue uma cascata estrita; pare na primeira que casar.

### Cascata

1. **Passo cita explicitamente um arquivo de teste.** Procurar no
   texto do passo qualquer ocorrência de `*.test.*`, `*.spec.*`,
   `tests/...`, `__tests__/...`. Se houver, esse é o teste do passo.

2. **Passo cita um arquivo de produção e existe teste irmão.** Se o
   passo cita `src/foo/bar.ts` (ou similar), procurar nesta ordem:
   - `src/foo/bar.test.*` / `src/foo/bar.spec.*`
   - `src/foo/__tests__/bar.*`
   - `tests/foo/bar.*`
   O primeiro que existir é o teste do passo.

3. **Sem casamento.** Pular C silenciosamente para esse passo. **Não
   tentar** inferir por palavras-chave do título da task — gera ruído
   e risco de associar passo a teste errado.

### Fallback

Sem teste associado, o passo é executado normalmente; a Validação
intrínseca da task continua sendo o gate confiável.

### Exemplo

Passo: `- [ ] criar handler em src/api/users/create.ts respeitando schema`

- Cascata 1: nenhum arquivo de teste citado no texto.
- Cascata 2: existe `src/api/users/create.test.ts` → teste associado.
- Após executar o passo, rodar: `<Comando de teste> -- src/api/users/create.test.ts`
  (ou equivalente do framework).

---

## 2. Construção do filtro seletivo (otimização B)

Durante o loop de correção (até 5 ciclos), rodar a suíte completa
seria lento. A skill constrói um filtro a partir do contexto disponível.

### Regra

O filtro é a **união** dos testes inferidos a partir de:

- **Arquivos Afetados do PLAN** intersecção com **arquivos tocados pela
  task em execução** (heurística da seção 1, aplicada ao escopo da
  task inteira, não passo a passo).
- **Testes citados no bloco Validação da task** (qualquer caminho
  `*.test.*` / `*.spec.*` mencionado).

### Fallback

Se a interseção for vazia (nenhum teste casa), **fallback explícito
para suíte completa**, com aviso ao usuário:

> "Execução seletiva indisponível para esta task — rodando suíte
> completa nos 5 ciclos. Isso pode ser lento."

### Exemplo

PLAN — "Arquivos Afetados": `src/api/users/create.ts`,
`src/api/users/list.ts`, `src/lib/auth.ts`.

Task T03 toca `src/api/users/create.ts`. Validação cita
`tests/integration/users.spec.ts`.

- Filtro: `src/api/users/create.test.ts` ∪
  `tests/integration/users.spec.ts`.
- Comando: `<Comando de teste do PLAN> -- src/api/users/create.test.ts tests/integration/users.spec.ts`
  (a sintaxe exata depende do test runner — adaptar conforme convenção
  do framework detectado em `Comando de teste`).

---

## 3. Interpretação de critérios de aceite do SPEC (gate final)

Ao fim da cadeia de tasks, a skill executa os critérios de aceite (§5a) do
`SPEC.md` que sejam **programaticamente verificáveis**. O SPEC não marca
explicitamente quais critérios são automatizáveis — a skill interpreta
por heurística textual sobre a coluna "Como verificar (observável)".

### Sinais de critério executável

Um critério é executável quando o "Método de verificação" da tabela
contém **pelo menos um** destes sinais:

- Comando entre crase: `` `npm test` ``, `` `curl /health` ``,
  `` `git log --oneline` ``.
- Verbo de execução acompanhado de objeto técnico: "rodar X",
  "executar Y", "invocar Z", "inspecionar arquivo W".
- Path de arquivo plausível: `tests/...`, `src/...`,
  `./.aidev/{slug}/TASKS.md`.

### Sinais de critério manual (não executar)

- Palavras como "verificar visualmente", "revisão", "inspeção
  manual", "p99 em prod", "métrica em produção", "depende do usuário".
- Critérios cujo método é só uma descrição em prosa sem comando ou
  path.

### Comportamento

Para cada critério da tabela "Critérios de Aceite":

1. Aplicar a regra acima e classificar como **executável** ou **manual**.
2. Critérios executáveis: extrair o comando (do bloco em crase ou
   inferido do verbo + objeto), executar, reportar `OK | FALHA |
   ERRO_DE_EXECUÇÃO`.
3. Critérios manuais: listar como `verificação manual sugerida` no
   relatório final, sem tentar executar.

### Importante

O gate final **não promove o status para `concluído`** mesmo que tudo
passe — essa transição é responsabilidade da `validar-implementacao`, no
fechamento. O gate só reporta o estado.

### Exemplo

Critério do PRD 002:
> | Skill nunca cria commit git | Invocar cadeia completa; `git log` deve permanecer no mesmo HEAD; working tree pode estar sujo |

- Sinais executáveis: `` `git log` `` em crase + verbo "Invocar".
- Comando inferido: `git log --oneline -1` no início e no fim, comparar HEAD.
- Reporte: `OK` (HEAD inalterado) | `FALHA` (HEAD mudou).

Critério do PRD 002:
> | Execução seletiva (B) durante ciclos mais rápida que suíte completa | Comparar tempos em projeto com suíte não-trivial |

- Sinais executáveis: nenhum (não há comando, "comparar tempos" é
  prosa, "suíte não-trivial" é qualitativo).
- Reporte: `verificação manual sugerida — comparar timing entre
  execução seletiva e suíte completa em projeto real`.

---

## 4. Detecção de drift entre invocações

Quando a skill é reinvocada e encontra o bundle
(`SPEC.md`/`PLAN.md`/`TASKS.md`) existente, precisa decidir se pode
continuar com confiança ou se houve mudança desde a última pausa que
invalida o estado salvo.

### Regra

A última nota de pausa de cada task carrega um `Snapshot` com `mtime`
do `SPEC.md`, do `TASKS.md` e do PRD (quando `prd:` aponta um slug) no
momento da pausa (ver `template-nota-pausa.md`). Ao retomar:

1. Localizar a **última nota de pausa do arquivo** (qualquer task) e
   extrair o `Snapshot`.
2. Comparar `mtime` atuais do SPEC, do TASKS e do PRD (quando existe)
   contra o `Snapshot`.
3. Classificar:
   - **Sem drift** — `mtime` atuais ≤ snapshot. Retomar normalmente.
   - **Drift no TASKS** apenas — alguém editou o TASKS manualmente
     desde a pausa. Antes de retomar, **mostrar diff resumido** e
     perguntar se as mudanças são propositais ou se o usuário quer
     reconciliar via `preparar-execucao`.
   - **Drift no SPEC ou no PRD** — o contrato (ou sua fonte de verdade)
     mudou desde a pausa. Sinalizar que reconciliação via
     `preparar-execucao` é fortemente recomendada antes de prosseguir,
     porque PLAN/TASKS podem estar desatualizados.
   - **Drift em contrato + TASKS** — pausa para reconciliação obrigatória;
     não continuar sem alinhamento explícito do usuário.

### Fallback

Quando não há nota de pausa anterior (primeira execução, ou todas as
tasks completaram e a skill foi reinvocada para o gate final), pular
detecção de drift — não há baseline para comparar.

### Exemplo

Última nota da task T03 (registrada em 2026-04-17 14:30):
```
> Snapshot: SPEC mtime 2026-04-17 09:05, TASKS mtime 2026-04-17 14:25, PRD mtime 2026-04-17 09:00.
```

Ao retomar em 2026-04-19:
- `mtime` atual do SPEC: `2026-04-18 10:00` → drift no SPEC.
- `mtime` atual do TASKS: `2026-04-17 14:25` → sem drift.

Ação: alertar
> "SPEC foi alterado em 2026-04-18 10:00 (após a última pausa em
> 2026-04-17 14:30). Recomendo invocar `preparar-execucao` em modo
> reconciliação antes de retomar a execução. Continuar mesmo assim
> ou pausar para reconciliar?"

---

## 5. Construção do commit por task (consolidação do progresso)

Ao fim de cada task verde (passo 6 do fluxo), a skill cria **um
commit** consolidando o trabalho. A mensagem segue semantic commit em
uma linha, sem corpo, sem assinatura IA — regra do `CLAUDE.md` do
usuário.

### Formato da mensagem

```
<tipo>(<slug>): <titulo-da-task em minúsculo> [T{NN}]
```

- **`<tipo>`** inferido pelo campo `**Nível:**` da task no `TASKS.md`
  (tabela abaixo).
- **`<slug>`** é o slug do bundle (nome do diretório em `./.aidev/`,
  removendo o prefixo numérico — ex.: `002-implementar-task` →
  `implementar-task`).
- **`<titulo-da-task>`** é o título da task sem o prefixo `TNN:`,
  normalizado para minúsculo. Preservar nomes próprios de arquivo,
  rota e símbolo (ex.: `/api/users`, `UserService`).
- **`[T{NN}]`** é o ID da task no final, entre colchetes, para
  rastreabilidade bidirecional `git log ↔ TASKS.md`.

### Tabela Nível → tipo semantic

| Valor de `**Nível:**` no TASKS.md | Tipo semantic |
|---|---|
| `código novo`, `implementação`, `feature`, `API`, `UI`, `CLI` | `feat` |
| `refatoração`, `refactor` | `refactor` |
| `infra`, `configuração`, `config`, `build`, `ci`, `tooling` | `chore` |
| `documento`, `documentação`, `docs` | `docs` |
| `teste`, `testes`, `cobertura`, `qa` | `test` |
| `correção`, `bugfix`, `fix`, `hotfix` | `fix` |

### Fallback para Nível não mapeado

Quando o valor de `**Nível:**` não casa com nenhuma linha da tabela
(ou o campo está ausente), usar `chore` e **avisar** o usuário na
saída final da task:

> "Nível '<valor>' não mapeia para semantic commit conhecido. Commit
> saiu como `chore`. Se estiver errado, ajuste manualmente com
> `git commit --amend` e considere padronizar 'Nível' no PLAN/TASKS
> para próximas tasks."

Nunca tentar inferir um tipo "parecido" por proximidade textual — o
fallback é sempre `chore`, explícito. Chute silencioso polui o
histórico.

### Arquivos incluídos no commit

O conjunto de arquivos commitados é a **interseção** entre:

1. **"Arquivos Afetados"** declarados no `PLAN.md` (pode estar na
   seção global ou por task, conforme a estrutura do PLAN).
2. **Arquivos efetivamente modificados/criados** no working tree,
   detectados via `git status --porcelain`.

Somado a:

3. **`./.aidev/{slug}/TASKS.md`** (sempre incluído — carrega os novos
   `[X]` da task e entra no mesmo commit para o histórico refletir o
   estado de progresso).

**Nunca** usar `git add -A` ou `git add .` — arrasta arquivos
alheios. Se um arquivo modificado **não está** em "Arquivos
Afetados", a skill já teria pausado no passo 2 com
`working-tree-sujo`. Se mesmo assim chegar aqui (ex.: passo da task
editou arquivo não previsto no PLAN), tratar como incoerência — a
correção é reconciliação via `preparar-execucao`, não burlar o filtro.

### Comando completo

```bash
git add <arquivos-do-escopo> ./.aidev/{slug}/TASKS.md
git commit -m "<tipo>(<slug>): <titulo> [T{NN}]"
```

Sem `--no-verify`, sem `--no-gpg-sign`, sem `-n`. Hooks falhando são
sinais, não obstáculos.

### Exemplo

Task no `TASKS.md`:
```markdown
## [X] T03: implementar handler /api/users
- **Nível:** código novo
- **USs cobertas:** US02
- ...
```

Slug do PRD: `002-implementar-task` → slug limpo `implementar-task`.

"Arquivos Afetados" do PLAN: `src/api/users/create.ts`,
`src/api/users/__tests__/create.test.ts`, `src/api/router.ts`.

`git status --porcelain` mostra modificados:
`src/api/users/create.ts`, `src/api/users/__tests__/create.test.ts`,
`./.aidev/002-implementar-task/TASKS.md`.

Interseção (sem `src/api/router.ts` porque não foi mexido nesta task):

```bash
git add src/api/users/create.ts src/api/users/__tests__/create.test.ts \
        ./.aidev/002-implementar-task/TASKS.md
git commit -m "feat(implementar-task): implementar handler /api/users [T03]"
```

### Falha no commit

Pre-commit hook rejeita, signing falha, permissão negada, repositório
em estado inconsistente, etc.:

1. **Não** tentar novamente automaticamente — não é ruído a retentar;
   é sinal.
2. **Reverter o `[X]` do título da task** para `[ ]`. `[X]` de passos
   e itens de Validação permanecem — o trabalho foi feito.
3. Registrar pausa `falha-commit` conforme
   `references/template-nota-pausa.md`. Incluir o comando exato e o
   stderr relevante do hook.
4. Devolver controle ao usuário.

---

## Princípio comum

Todas as cinco heurísticas obedecem o **guardrail de fonte de
verdade** da skill: quando o sinal pretendido não aparece, a skill
**avisa** e cai num fallback explícito — nunca chuta em silêncio.
Falha de heurística é fenômeno gerenciável; chute silencioso é bug
oculto.
