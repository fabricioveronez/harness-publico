# Modo Preparar — do escopo ao bundle executável

Traduz a intenção (PRD, documento de brainstorm, ou descrição direta) no contrato
executável e no scaffolding técnico: decompõe o escopo em **fatias**, gera o
bundle de cada uma e o **manifesto** do conjunto, e **commita** o resultado.

Cobre três situações, detectadas por `scripts/bundle_state.py`:

| Situação | Entra em |
|---|---|
| não há bundle para o escopo | **criação** |
| há bundle e o usuário quer ajustar algo | **edição** |
| o usuário pediu explicitamente ("o PRD mudou", "reconcilia") | **reconciliação** |

Reconciliação **nunca** é automática. Ela reescreve plano em cima de progresso
real, e fazer isso sem o usuário pedir é o tipo de ajuda que destrói trabalho.

---

## 1. Determinar a origem e a fonte de verdade

Três entradas possíveis, e a escolha define quem vence em conflito depois:

**Com PRD.** O usuário cita um PRD (número, slug, arquivo). Localize em
`docs/prds/` (pergunte o diretório na primeira vez do projeto). Leia o `status`:

- `concluido` → **abortar**. PRD concluído é imutável; feature que evolui abre PRD novo.
- `rascunho` → siga, e ao aprovar o corte ofereça promover para `pronto` (passo 6).
- `pronto` / `em-progresso` → siga.

O SPEC vira uma **projeção** do PRD: copie as US com IDs estáveis, Rules e Edge
cases. Não invente Rule que não esteja lá — lacuna vira premissa marcada e um
aviso para voltar ao `escrever-prd`.

**Com documento de origem que não é PRD** (brainstorm, RFC, notas de reunião,
transcrição). É o caso mais comum em projeto que ainda não tem processo formal.
Leia o documento inteiro e trate-o como **insumo, não como contrato**: ele carrega
raciocínio, alternativas descartadas e pendências em aberto — nada disso entra no
SPEC. O que entra é o comportamento decidido.

Duas coisas merecem atenção nesse tipo de documento:

- **Decisão registrada ≠ requisito.** "Descartamos webhook em favor de polling" é
  contexto técnico (vai para o PLAN, ou vira ADR via `escrever-trd`), não Rule.
- **Pendência em aberto é lacuna, não premissa livre.** Se o documento diz
  explicitamente que algo não foi decidido, não decida por ele em silêncio.
  Pergunte, ou registre como premissa **visível** no SPEC e sinalize no resumo.

O `prd:` do bundle fica `none`; o SPEC é a fonte de verdade.

**Sem documento.** Descrição direta do usuário. Entreviste o mínimo para montar o
contrato — persona, comportamento esperado (vira Rules), situações anômalas (Edge
cases), como se verifica (critérios de aceite). Agrupe até 2 perguntas por
mensagem; entrevista longa cansa mais do que ajuda.

## 2. Slug base

- Com PRD → número + nome do arquivo (`003-toil`).
- Sem PRD → kebab-case curto da feature, confirmado com o usuário.

Cada fatia vira `{base}-{fatia}`; o manifesto é `{base}-manifest.md`. Com **uma**
fatia, o bundle é `{base}/` sem sufixo e **sem manifesto**.

## 3. Contexto técnico

Procure o TRD em `docs/trd.md`, `TRD.md`, `docs/TRD.md`. Se achar, registre a
origem no PLAN e extraia o **comando de teste**.

Se não achar, faça uma coleta curta (até 6 perguntas, 2 por mensagem): stack,
padrões e ferramentas de teste, **comando de teste**, estrutura de pastas,
convenções, restrições de ambiente.

O campo `Comando de teste:` é obrigatório no PLAN. O modo Implementar o consome
para a linha de base e para o filtro seletivo, e quebra sem ele. Sem suíte,
escreva literalmente `Sem suíte de testes detectada` — a ausência declarada é
informação; o campo faltando é bug.

## 4. Decompor em fatias

Decida **quantas fatias** antes de gerar qualquer arquivo. Fatia é a unidade de
*feature independente e testável*.

1. **Corte por independência + testabilidade.** Cada fatia (a) entrega algo
   observável de ponta a ponta, (b) tem **Arquivos Afetados disjuntos** das irmãs,
   e (c) cabe em **um** marco quando há PRD. Marco e US são rastreabilidade, não
   régua: um marco pode virar várias fatias; uma fatia não cruza dois marcos.

2. **N=1 é válido e é o default de escopo pequeno.** Não force split. Fatia
   artificial é o mesmo anti-padrão da task horizontal, e ainda paga o custo de
   worktree e merge por nada.

3. **A disjunção de arquivos é o que habilita o paralelismo — e é literal.**
   Duas fatias que tocam o mesmo arquivo não rodam juntas: a segunda recebe
   `needs:` apontando a primeira. Se muitas fatias colidem, o corte está errado;
   volte ao passo 1 em vez de encher o manifesto de dependências.

4. **Ondas** saem do grafo: fatia sem `needs` entra na onda 1; a onda de uma fatia
   com `needs` é `1 + max(onda das dependências)`.

5. **Apresente o corte e espere aprovação.** Liste fatia, USs cobertas, marco,
   `needs`/`[P]` e o que roda em paralelo. Mudar o corte depois custa retrabalho —
   este é o momento barato.

## 5. Gerar (em lote atômico)

Para **cada fatia**, gere `SPEC.md`, `PLAN.md` e `TASKS.md` a partir de
`templates/`. Depois o manifesto, se houver 2+ fatias.

### O contrato e o plano de teste

O `SPEC.md` carrega o comportamento **e** como ele se prova. A tabela de critérios
de aceite é **declarativa**, não prosa:

```markdown
| ID   | Critério                        | Nível      | Automatizável | Alvo                  |
|------|---------------------------------|------------|---------------|-----------------------|
| CA01 | sync não dispara execução       | integração | sim           | `tests/sync.spec.ts`  |
| CA02 | painel lista as duas fontes     | e2e        | sim           | `tests/e2e/painel.ts` |
| CA03 | leitura visual do board         | manual     | não           | verificação visual    |
```

Isso substitui a classificação por heurística textual que antes era refeita em
dois lugares diferentes, cada um interpretando a mesma prosa por conta própria.
Declarado uma vez, o gate final e o modo Validar executam **o mesmo conjunto**.

O `PLAN.md` ganha `## Estratégia de teste`: níveis em uso, fixtures/seeds
necessários, e o que fica **fora da automação com o porquê**. Estratégia é parte
do "como", e o PLAN já é dono do "como" — não precisa de arquivo próprio.

Cada task no `TASKS.md` referencia os critérios pelo **ID** no bloco `Validação:`,
em vez de reescrever o critério em prosa:

```markdown
- **Validação:**
  - [ ] CA01 — `npm test -- tests/sync.spec.ts`
  - [ ] CA03
```

Rode `python3 scripts/cobertura.py --bundle .aidev/{slug}` antes de gravar. Ele
acusa US sem task, critério sem task, task sem critério e referência a ID
inexistente. Lacuna aqui é barata; lacuna descoberta no gate final custa uma
execução inteira.

### Verticalização e paralelismo de task

Prefira sempre o **nível mais alto viável** de entrega: usuário > API/CLI >
componente interno. Task horizontal ("criar todo o schema") só se o slice vertical
for artificial — bootstrap, refatoração grande, infra.

Depois de gerar todas as tasks, faça a passagem de `[P]`: task com `needs: —` é
candidata; se duas candidatas tocam o mesmo arquivo, a segunda perde o `[P]` e
ganha `needs:` apontando a primeira. Nunca `[P]` junto com `needs:` preenchido.

Cadeia linear de mais de 3 tasks dependentes é sinal de horizontalização
disfarçada — avise o usuário, sem bloquear.

### Gravação

Escreva **tudo ou nada**. Se qualquer arquivo falhar, apague o que já foi gravado.
Um `.aidev/` com decomposição parcial (bundle sem os três arquivos, ou manifesto
apontando fatia que não existe) trava todos os outros modos.

Antes de gravar, mostre o resumo: número de fatias, USs e tasks por fatia, ondas,
quais tasks receberam `[P]` e quais receberam `needs:` por conflito detectado.

## 6. Commitar o bundle e ajustar status

**Este passo não é opcional.** O modo Orquestrar cria worktrees a partir do HEAD;
um bundle gravado mas não commitado não existe dentro do worktree, e a fatia
abriria um `./.aidev/` vazio. Além disso, `git status --porcelain` não fica limpo
com o bundle untracked, e a orquestração aborta antes de começar.

```bash
git add .aidev/ && git commit -m "docs(sdd): bundle {base} ({N} fatias)"
```

Depois:

```bash
python3 scripts/transicao.py bundle {slug} --para pronto      # por fatia
python3 scripts/transicao.py prd {slug-prd} --para pronto     # se veio de PRD em rascunho
```

A promoção do PRD para `pronto` fecha uma transição que antes não tinha dono
nenhum — e por isso todo PRD ficava em rascunho para sempre, arrancando um alerta
na preparação e uma confirmação na implementação, em todo ciclo. Como é status de
artefato de outra skill, **peça o aval** antes; mas ofereça, em vez de deixar o
usuário editar YAML na mão.

## 7. Modo edição

Bundle existe e o usuário quer ajustar. Leia o manifesto e os bundles, e preserve:

- IDs de US e de task já atribuídos, e os slugs de fatia (nunca mudam);
- **tudo que está `[X]`**, em título, passo ou validação;
- decisões já registradas nos PLANs.

Onde o ajuste mora depende do que mudou:

| Mudou | Vai para |
|---|---|
| comportamento, **com** PRD | `escrever-prd` e depois reconciliação — não edite o SPEC |
| comportamento, **sem** PRD | o próprio `SPEC.md` (ele é a fonte) |
| narrativa técnica sem efeito em task | só o `PLAN.md` |
| abordagem que invalida passos | `PLAN.md` + revisão do `TASKS.md` |
| nova task | próximo ID sequencial, no fim da fatia |
| feature independente nova | nova fatia + linha no manifesto + recomputar ondas |

Se o conjunto tinha 1 fatia e ganha a segunda, o bundle único precisa virar
`{base}-{fatia}` e nasce um manifesto. **Avise** — isso muda o slug que as outras
consumidoras enxergam.

Se a edição invalida uma task `[X]`, pergunte: manter como histórico com nota, ou
adicionar subtask de reverificação. Nunca apague o `[X]` em silêncio.

Mostre o diff antes de gravar. Grave em lote atômico. Commite.

## 8. Modo reconciliação

Só sob pedido explícito. Compare a fonte de verdade (PRD quando existe, senão o
SPEC editado) com o que o bundle reflete.

Se o PRD virou `concluido` desde a criação → **abortar**.
Se a divergência for grande a ponto de reconciliar custar mais que recriar →
sinalize e sugira apagar e recomeçar, em vez de remendar.

Caso contrário, planeje em nível de fatia e de task:

- **Toda task `[X]` é preservada.** Sem exceção.
- **US nova** → cabe numa fatia existente (task nova, ID continuando) ou abre
  fatia nova (bundle + linha no manifesto + recomputar ondas). Fatias novas entram
  **abaixo**; slugs existentes não mudam.
- **US removida mas já entregue por task `[X]`** → registre como "órfã concluída"
  no PLAN da fatia e nota no manifesto. Não delete.
- **Fatia esvaziada sem nenhum `[X]`** → remova bundle e linha do manifesto. Com
  `[X]`, vira órfã concluída e fica.
- **Recompute o manifesto** — tabela, ondas e rollup.

Apresente o resumo (o que mudou na fonte, o que será criado, o que fica intocado,
o que vira órfão) antes de gravar. Grave em lote. Commite.

## Fora deste modo

Não executa task, não marca `[X]`, não edita PRD/TRD/ADR, não cria worktree e não
promove status para `concluido`.
