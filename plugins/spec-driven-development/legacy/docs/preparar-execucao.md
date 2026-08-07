# preparar-execucao

Gera e mantém o **bundle de execução** de uma feature — `SPEC.md` + `PLAN.md` +
`TASKS.md` — em `./.aidev/{slug}/`, um diretório versionado que forma um bundle
**Open Knowledge Format (OKF)**. O `SPEC.md` é o contrato comportamental
orientado à IA (US Rules, Edge cases, critérios de aceite); o `PLAN.md` é a
abordagem técnica; o `TASKS.md` é o checklist de execução. Tem dois modos de
entrada — projeta o SPEC de um PRD pronto (projeto grande) ou, sem PRD,
entrevista o usuário e autora o SPEC direto (projeto pequeno) — e cobre ainda
edição e reconciliação sob demanda, preservando IDs e marcações `[X]`.

Decompõe o escopo em **1..N fatias** — cada fatia é uma *feature independente e
testável* com seu próprio bundle `./.aidev/{base}-{fatia}/`. Quando há 2+
fatias, emite também um **manifesto** `./.aidev/{base}-manifest.md` (índice das
fatias + grafo de dependência + ondas de paralelismo), consumido pela
`orquestrar-execucao` para rodar as fatias independentes em paralelo. O gatilho
é o tamanho do escopo, não a presença de PRD: feature pequena degenera em **1
fatia** (bundle único `./.aidev/{base}/`, sem manifesto).

## Pré-requisitos e configuração

- **Com PRD** — um PRD gerado por `escrever-prd`. `pronto` e `em-progresso`
  seguem direto; **`rascunho` gera alerta** e a skill pergunta se prossegue
  mesmo assim; `concluido` é imutável e a skill **recusa** gerar bundle. Na
  primeira invocação ela pergunta o diretório de PRDs (default: `./docs/prds/`).
- **Sem PRD** — nada além da descrição da feature. A skill entrevista o mínimo
  para montar o contrato e autora o `SPEC.md` (que passa a ser a fonte de
  verdade); o bundle fica com `prd: none`.
- Um TRD (`./docs/trd.md`), quando existe, é carregado como contexto técnico
  global; senão, a skill entra em **mini-modo de coleta** (entrevista curta
  sobre stack, convenções e comando de teste).

### Formato OKF e vocabulário de status

`SPEC.md`/`PLAN.md`/`TASKS.md` têm frontmatter OKF: `type` (`spec`/`plan`/
`tasks`) é o único campo obrigatório; `title`, `description`, `resource`, `tags`
são recomendados; `created`, `status`/`plan_status` e `prd` são convenção da
skill. Os três se cruzam por links markdown (PLAN→SPEC, TASKS→PLAN) e apontam
para PRD/TRD/ADR quando existem.

O bundle e o PRD usam **vocabulários de `status` diferentes**, de propósito —
são artefatos distintos, com ciclos de vida distintos:

| Artefato | Campo | Valores |
|---|---|---|
| PRD | `status` | `rascunho \| pronto \| em-progresso \| concluido` |
| `SPEC.md`, `PLAN.md` | `status` | `rascunho \| pronto \| em-execucao \| concluido` |
| `TASKS.md` | `plan_status` | `rascunho \| pronto \| em-execucao \| concluido` |

## Dependências externas

Nenhuma. A skill é autossuficiente e trabalha só com arquivos markdown.

## Skills relacionadas

- **escrever-prd** — opcional. Gera o PRD que a skill projeta no SPEC (projeto
  grande). Sem PRD, a skill autora o SPEC direto.
- **implementar-task** — consome cada bundle: carrega o `SPEC.md` como contexto
  primário, executa as tasks e marca `[X]`.
- **orquestrar-execucao** — quando a decomposição tem 2+ fatias, consome o
  manifesto e roda as fatias independentes em paralelo (worktree por fatia).
- **validar-implementacao** — fecha o ciclo: valida código ↔ contrato, ajusta
  drift e promove o `status` para `concluido`.
- **escrever-trd** — contexto técnico global (TRD) e ADRs referenciados pelo
  bundle.
- **revisao-documento-tecnico** — revisa SPEC/PLAN/TASKS antes de executar; as
  correções estruturais voltam para esta skill.

## Exemplos de uso

```
Prepara a execução do PRD 003

Gera o spec e as tasks da feature de autenticação

Quebra o PRD de pagamentos em tasks

Prepara a execução do login por magic link   (projeto sem PRD)

Reabre o bundle do PRD 003 — quero adicionar uma task de rate limiting

Reconcilia o plano do PRD 005: adicionei uma US nova

Atualiza o bundle, o PRD mudou

Prepara a execução do PRD 003 e quebra em fatias paralelas
```

### Aprovação do corte

Antes de gerar qualquer arquivo, a skill **apresenta a decomposição para
aprovação**: lista as fatias propostas (slug, USs cobertas, marco, `needs`/`[P]`)
e o que roda em paralelo. É o checkpoint onde o usuário ajusta o corte — depois
dele, mudar o corte custa reconciliação.

Um sinal de corte ruim que a skill alerta sozinha: **sequência linear de mais de
3 tasks dependentes**, que costuma indicar horizontalização disfarçada (fatias
que na verdade são camadas técnicas, não features).

## Limitações conhecidas

- A skill **não marca `[X]`** em tasks — isso é papel de quem executa
  (`implementar-task` ou humano).
- A skill **não edita o PRD** — mudança de comportamento com PRD volta para
  `escrever-prd`; sem PRD, o ajuste do contrato é no próprio `SPEC.md`.
- **Reconciliação é sempre manual** — só roda sob pedido explícito; a skill não
  detecta mudanças no PRD/SPEC automaticamente. Se a divergência for grande
  demais, ela sugere **apagar `./.aidev/{slug}/` e recriar** em vez de remendar.
- **Gravação é atômica** — se qualquer arquivo do conjunto falhar ao gravar, o
  que já foi escrito é apagado, para não deixar decomposição parcial no disco.
- **Passar de 1 para 2+ fatias renomeia o bundle** — o bundle único
  `./.aidev/{base}/` vira `./.aidev/{base}-{fatia}/`. A skill avisa, porque o
  slug que as consumidoras enxergam muda (referências antigas quebram).
- Qualidade do contrato depende da entrada — USs sem `Rules`/`Edge cases` (no
  PRD) ou descrição rasa (sem PRD) forçam inferência e geram tasks frágeis. A
  skill marca premissas e alerta antes de prosseguir.
- **PRD com `status: concluido` é rejeitado** — por design; feature que evolui
  abre novo PRD.
- **Decompõe e prepara o paralelismo, mas não executa** — gera as fatias, o
  grafo e o manifesto; rodar as fatias em paralelo (worktrees, fan-out, merge) é
  da `orquestrar-execucao`.
- **N=1 não gera manifesto** — feature pequena/direta vira bundle único
  `./.aidev/{base}/`, sem sufixo de fatia e sem manifesto.

### Referências da skill

- `references/template-spec.md`, `template-plan.md`, `template-tasks.md` —
  estrutura canônica de cada arquivo do bundle.
- `references/template-manifest.md` — índice das fatias, grafo de dependência e
  ondas de paralelismo.
