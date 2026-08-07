# Heurísticas de execução

Regras operacionais do modo Implementar. Cada uma tem o sinal que busca, o
fallback explícito quando o sinal não aparece, e um exemplo. Nenhuma autoriza
inventar: quando o fallback se aplica, **avise o usuário**. Falha de heurística é
fenômeno gerenciável; chute silencioso é bug oculto.

## Índice

1. [Inferir o teste de um passo](#1-inferir-o-teste-de-um-passo)
2. [Filtro seletivo no loop de correção](#2-filtro-seletivo-no-loop-de-correção)
3. [Critérios de aceite no gate final](#3-critérios-de-aceite-no-gate-final)
4. [Drift entre invocações](#4-drift-entre-invocações)
5. [Commit por task](#5-commit-por-task)

---

## 1. Inferir o teste de um passo

Serve ao feedback granular: depois de executar um passo, rodar só o teste daquele
passo dá sinal em segundos em vez de minutos. Cascata estrita — pare na primeira
que casar.

1. **O passo cita um arquivo de teste.** Procure `*.test.*`, `*.spec.*`,
   `tests/...`, `__tests__/...` no texto do passo.
2. **O passo cita um arquivo de produção com teste irmão.** Para `src/foo/bar.ts`,
   procure nesta ordem: `src/foo/bar.test.*`, `src/foo/bar.spec.*`,
   `src/foo/__tests__/bar.*`, `tests/foo/bar.*`.
3. **Sem casamento** → pule silenciosamente para esse passo. **Não** tente inferir
   por palavra-chave do título da task: associar passo ao teste errado gera ruído
   e faz perder ciclo caçando falha que não existe.

Fallback: o passo roda normalmente; o bloco `Validação:` da task continua sendo o
gate confiável.

**Exemplo.** Passo: `- [ ] criar handler em src/api/cards/create.ts`. Cascata 1
não casa; cascata 2 acha `src/api/cards/create.test.ts`. Rode
`<Comando de teste> -- src/api/cards/create.test.ts`.

---

## 2. Filtro seletivo no loop de correção

Rodar a suíte inteira em 5 ciclos é lento o bastante para desencorajar o loop. O
filtro é a **união** de:

- testes inferidos (seção 1) dos arquivos que a task tocou — interseção entre
  "Arquivos Afetados" do PLAN e o que mudou de fato;
- caminhos `*.test.*` / `*.spec.*` citados no bloco `Validação:` da task;
- o campo `Alvo` dos critérios (`CA`) que a task referencia, quando é um caminho.

Fallback: interseção vazia → suíte completa nos 5 ciclos, **com aviso**:

> "Execução seletiva indisponível para esta task — rodando suíte completa nos
> ciclos. Pode ficar lento."

Lembre que verde no seletivo **não** encerra o ciclo: rode a suíte completa uma
vez como gate. Seletivo verde com suíte vermelha é `regressao-fora-escopo`.

---

## 3. Critérios de aceite no gate final

Com o SPEC no formato declarativo, **não há heurística**: a tabela §5a traz `ID`,
`Nível`, `Automatizável` e `Alvo`. Rode `scripts/cobertura.py`, execute os alvos
dos critérios marcados como automatizáveis, reporte `OK | FALHA |
ERRO_DE_EXECUÇÃO`, e liste os manuais como verificação sugerida.

Isso substitui a classificação por regex sobre prosa que existia antes — e que era
refeita em dois lugares (gate final e validação), cada um podendo chegar a uma
conclusão diferente sobre o mesmo critério.

**Fallback para bundle legado** (tabela sem coluna `ID`, herdada de um bundle
antigo): `cobertura.py` avisa e você classifica pelo texto — comando entre crase,
verbo de execução com objeto técnico, ou path plausível indicam executável;
"verificar visualmente", "revisão", "métrica em produção" indicam manual. Ao
encontrar esse caso, **ofereça migrar** o SPEC para o formato declarativo no modo
Preparar: é uma edição pequena que elimina a ambiguidade de vez.

O gate final **não fecha nada**. Fechar é do modo Validar.

---

## 4. Drift entre invocações

A última nota de pausa carrega um `Snapshot` com o **hash** do conteúdo do
`SPEC.md`, do `TASKS.md` e do PRD (quando existe) no momento da pausa:

```bash
git hash-object .aidev/{slug}/SPEC.md   # ou: shasum -a 256 <arquivo> | cut -c1-12
```

**O hash do `TASKS.md` sai da versão em HEAD, não do disco:**

```bash
git show HEAD:.aidev/{slug}/TASKS.md | git hash-object --stdin | cut -c1-12
```

O motivo é que o snapshot é gravado *dentro* do `TASKS.md`, junto com a nota de
pausa e os `[X]` do passo. Tirar o hash do disco criaria uma referência
circular: o arquivo muda ao registrar a própria pausa, e toda retomada acusaria
"TASKS alterado desde a pausa" por uma escrita que o próprio protocolo fez,
mandando o usuário conferir um diff que ele nunca produziu. O que interessa
detectar é edição **externa** entre invocações, e é isso que a versão em HEAD
isola.

Use hash de conteúdo, **não `mtime`**. `git checkout`, `git worktree add` e clone
reescrevem o timestamp sem alterar uma linha do arquivo — e num fluxo que cria
worktree por fatia, o `mtime` acusaria drift no SPEC de toda fatia, toda onda,
interrompendo a execução antes de começar por uma mudança que não existiu.

Ao retomar, compare os hashes atuais com o `Snapshot`:

| Situação | Ação |
|---|---|
| todos iguais | retome normalmente |
| só o `TASKS.md` mudou | mostre o diff resumido e pergunte se foi proposital |
| o SPEC ou o PRD mudou | **interrompa antes de tudo**; reconciliação é fortemente recomendada, porque PLAN e TASKS podem estar desatualizados |
| contrato **e** TASKS mudaram | reconciliação obrigatória; não continue sem alinhamento explícito |

Fallback: sem nota de pausa anterior (primeira execução, ou cadeia que completou)
não há baseline — pule a detecção.

---

## 5. Commit por task

### Mensagem

```
<tipo>(<slug>): <título da task em minúsculo> [T{NN}]
```

Uma linha, sem corpo, sem assinatura de IA. `<slug>` é o nome do diretório do
bundle sem o prefixo numérico (`003-toil-api` → `toil-api`). Preserve nomes
próprios de arquivo, rota e símbolo (`/api/cards`, `CardService`).

### Tipo, a partir do campo `**Nível:**`

| Valor de `Nível` | Tipo |
|---|---|
| `usuário`, `usuario`, `API`, `componente`, `código novo`, `implementação`, `feature`, `UI`, `CLI` | `feat` |
| `refatoração`, `refactor` | `refactor` |
| `infra`, `configuração`, `config`, `build`, `ci`, `tooling` | `chore` |
| `documento`, `documentação`, `docs` | `docs` |
| `teste`, `testes`, `cobertura`, `qa` | `test` |
| `correção`, `bugfix`, `fix`, `hotfix` | `fix` |

Os três valores que o `template-tasks.md` declara — `usuário`, `API`, `componente`
— estão todos aqui de propósito: um valor legítimo do template caindo no fallback
seria bug da tabela, não do autor da task.

Sem casamento → `chore`, **com aviso** ao usuário sugerindo padronizar o campo.
Nunca infira um tipo "parecido" por proximidade textual.

### Arquivos incluídos

A interseção entre "Arquivos Afetados" do PLAN e o que `git status --porcelain`
mostra como modificado, **mais tudo que o próprio fluxo escreveu**:

- `.aidev/{slug}/TASKS.md` — carrega os `[X]` novos, e é o que faz o histórico
  refletir o progresso;
- o arquivo de memória da execução (`docs/MEMORY.md`, ou
  `docs/.memory/{base}-{fatia}.md` dentro de um worktree);
- `SPEC.md` e `PLAN.md` do bundle **quando houve transição de status** nesta
  invocação (o `transicao.py` escreve nos três arquivos ao promover para
  `em-execucao`).

A regra por trás dos três é a mesma: **arquivo que o fluxo escreveu, o fluxo
commita**. Fora do commit ele deixa o working tree sujo, e a invocação seguinte
pausa com `working-tree-sujo` por um arquivo que ninguém pediu — laço que só sai
com commit manual. Dentro de um worktree é pior: `git worktree remove` recusa sair
sujo e a limpeza da onda quebra.

O que a regra **não** afrouxa: arquivo de código fora de "Arquivos Afetados"
continua sendo incoerência, e a saída é reconciliar no modo Preparar. A exceção
vale só para os artefatos de controle do próprio ciclo.

```bash
git add <arquivos-do-escopo> .aidev/{slug}/TASKS.md <arquivo-de-memoria>
# se houve transição de status nesta invocação, os outros dois vão junto:
git add .aidev/{slug}/SPEC.md .aidev/{slug}/PLAN.md
git commit -m "<tipo>(<slug>): <título> [T{NN}]"
```

Nunca `git add -A` — arrasta arquivo alheio. Nunca `--no-verify`, `--no-gpg-sign`
ou `-n`. Se um arquivo modificado não está em "Arquivos Afetados", isso já deveria
ter parado no passo 1 como `working-tree-sujo`; se chegou aqui, é incoerência, e
a correção é reconciliar no modo Preparar — não afrouxar o filtro.

### Falha no commit

1. **Não** tente de novo automaticamente — hook que rejeita é sinal, não ruído.
2. Reverta o `[X]` do **título** (a consolidação não aconteceu). Os `[X]` de
   passos e validações permanecem: o trabalho foi feito.
3. Registre pausa `falha-commit` com o comando exato e o stderr relevante.
4. Devolva o controle.
