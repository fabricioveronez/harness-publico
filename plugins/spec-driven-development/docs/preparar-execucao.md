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

- **Com PRD** — um PRD em `status: pronto` ou `em-progresso` (gerado por
  `escrever-prd`). PRDs `concluido` são imutáveis: a skill recusa gerar bundle.
  A skill pergunta o diretório de PRDs na primeira invocação (default:
  `./docs/prds/`).
- **Sem PRD** — nada além da descrição da feature. A skill entrevista o mínimo
  para montar o contrato e autora o `SPEC.md` (que passa a ser a fonte de
  verdade); o bundle fica com `prd: none`.
- Um TRD (`./docs/trd.md`), quando existe, é carregado como contexto técnico
  global; senão, a skill entra em **mini-modo de coleta** (entrevista curta
  sobre stack, convenções e comando de teste).

## Formato OKF

`SPEC.md`/`PLAN.md`/`TASKS.md` têm frontmatter OKF: `type` (`spec`/`plan`/
`tasks`) é o único campo obrigatório; `title`, `description`, `resource`, `tags`
são recomendados; `created`, `status`/`plan_status` e `prd` são convenção da
skill. Os três se cruzam por links markdown (PLAN→SPEC, TASKS→PLAN) e apontam
para PRD/TRD/ADR quando existem.

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

## Limitações conhecidas

- A skill **não marca `[X]`** em tasks — isso é papel de quem executa
  (`implementar-task` ou humano).
- A skill **não edita o PRD** — mudança de comportamento com PRD volta para
  `escrever-prd`; sem PRD, o ajuste do contrato é no próprio `SPEC.md`.
- **Reconciliação é sempre manual** — só roda sob pedido explícito; a skill não
  detecta mudanças no PRD/SPEC automaticamente.
- Qualidade do contrato depende da entrada — USs sem `Rules`/`Edge cases` (no
  PRD) ou descrição rasa (sem PRD) forçam inferência e geram tasks frágeis. A
  skill marca premissas e alerta antes de prosseguir.
- **PRD com `status: concluido` é rejeitado** — por design; feature que evolui
  abre novo PRD.
- **Decompõe e prepara o paralelismo, mas não executa** — gera as fatias, o
  grafo e o manifesto; rodar as fatias em paralelo (worktrees, fan-out, merge) é
  da `orquestrar-execucao`.
- **N=1 não gera manifesto** — feature pequena/direta vira bundle único
  `./.aidev/{base}/`, sem sufixo de fatia e sem manifesto (comportamento
  idêntico ao anterior).
