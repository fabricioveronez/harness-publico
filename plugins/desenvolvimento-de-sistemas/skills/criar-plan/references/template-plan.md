# Template PLAN.md

Estrutura canônica do `PLAN.md` gerado pela skill `criar-plan`. O PLAN captura
a abordagem técnica que guia a implementação de um PRD — é o "como" para o
"o quê" do PRD. Pareado com `TASKS.md` no mesmo diretório `./.aidev/{slug}/`.

## Semântica dos campos de controle

**`prd`** — slug do PRD que este plano atende. Igual ao nome do arquivo do
PRD sem extensão (ex.: `003-autenticacao-oauth`). É a cola entre PLAN e a
fonte de verdade; nunca omitir.

**`status`** — ciclo de vida do plano, espelhando o PRD mas com semântica
própria:

- `rascunho` — em geração, revisão ou edição ativa
- `pronto` — revisado, aguardando a primeira execução
- `em-execucao` — ao menos uma task já iniciou ou foi marcada
- `concluido` — todas as tasks com `[X]`; plano congelado como histórico

**`created`** — data (YYYY-MM-DD) da primeira geração. Não muda em edições
subsequentes.

---

```markdown
---
prd: <slug-do-prd>
status: rascunho | pronto | em-execucao | concluido
created: YYYY-MM-DD
---

# PLAN: [Título da feature, espelhando o PRD]

## Referência ao PRD

- **Arquivo:** [`../../docs/prds/NNN-slug.md`](caminho)
- **Resumo:** [2-3 linhas sintetizando a feature — o leitor que cair aqui
  deve entender do que se trata sem abrir o PRD, mas o PRD é a fonte
  autoritativa.]

## Abordagem Técnica

[Decisões de alto nível que guiam a implementação. Cada decisão em 1-2
linhas, com justificativa curta. Não é um romance — é um mapa.]

- [Decisão 1 — ex.: "Autenticação via JWT emitido pelo backend; refresh
  token guardado em HttpOnly cookie. Motivo: evita lidar com OAuth server
  neste MVP."]
- [Decisão 2]
- [Decisão 3]

## Arquivos Afetados

Lista dos arquivos que serão criados ou alterados durante a implementação,
com propósito breve. Marcar `[NOVO]` para criação.

- `src/path/para/arquivo.ts` — [propósito]
- `src/outra/area/modulo.ts` — [propósito] `[NOVO]`
- `tests/feature.spec.ts` — [propósito] `[NOVO]`

## Diagrama de Implementação

[Bloco de código texto mostrando fluxo entre componentes, estrutura de
pastas proposta, ou modelo de dados simplificado. O formato depende do
que for mais útil para esta feature — não há obrigação de tipo específico.]

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ [Componente] │────▶│ [Componente] │────▶│ [Componente] │
│              │     │              │     │   [NOVO]     │
└──────────────┘     └──────────────┘     └──────────────┘
```

## Dependências Novas

Bibliotecas externas que precisam ser adicionadas ao projeto. Incluir
versão quando aplicável.

- `biblioteca-x` (^1.2.0) — [para quê]
- `outra-lib` (^0.5.0) — [para quê]

[Se não há dependências novas, escrever: "Nenhuma dependência nova."]

## Premissas Assumidas

O que a skill presumiu na ausência de informação explícita. O usuário
deve revisar — se uma premissa estiver errada, voltar à skill e ajustar.

- [Premissa 1 — ex.: "Assumido que usuários autenticados têm session
  válida via middleware global."]
- [Premissa 2]

## Contexto Técnico Global

[Origem e resumo do contexto técnico do projeto. Uma das duas formas:]

- **Carregado de:** `./docs/trd.md`
  - Stack: [resumo relevante]
  - Padrões: [resumo relevante]
  - Comando de teste: `[ex.: npm test, pytest, cargo test]` (ou `Sem suíte de testes detectada`)

**OU**, se o TRD não existia:

- **Coletado em mini-modo** (sem TRD no projeto):
  - Stack: [resposta da coleta]
  - Padrões de teste: [resposta]
  - Comando de teste: `[ex.: npm test, pytest, cargo test]` (ou `Sem suíte de testes detectada`)
  - Estrutura dominante: [resposta]
  - Convenções específicas: [resposta]
  - Restrições de ambiente: [resposta]

## Milestones Cobertos

Lista dos IDs de milestone do PRD endereçados por este plano. Se o plano
cobre parcialmente (ex.: só M1), deixar explícito.

- **Milestone 1**: [título do PRD] — coberto integralmente
- **Milestone 2**: [título do PRD] — coberto parcialmente (tasks T08-T10)

## Riscos Técnicos

Pontos de atenção que não justificam abrir um PRD novo mas merecem
registro — impactam execução.

| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| [descrição] | Alto/Médio/Baixo | [plano] |
| [descrição] | Alto/Médio/Baixo | [plano] |
```

---

## Regras de preenchimento

- **Autocontido dentro do escopo técnico** — o PLAN é o roteiro da
  implementação, não precisa repetir o PRD. Mas qualquer decisão que altere
  o comportamento descrito no PRD é sinal de que deve voltar ao PRD primeiro.
- **Conciso, não exaustivo** — decisões em 1-2 linhas, não parágrafos.
  Exaustividade mora nas tasks.
- **Seção `Arquivos Afetados` é lista, não narrativa** — uma linha por
  arquivo, com propósito de uma frase.
- **Diagrama é opcional mas útil** — se a feature envolve múltiplos
  componentes, vale 1000 palavras.
- **Premissas existem para serem desafiadas** — não as esconda; a skill
  deve listar tudo que assumiu, e o usuário tem o dever de revisar.
- **Comando de teste é obrigatório quando há suíte** — esse campo é
  consumido pela skill `implementar-task` para rodar linha de base, gate
  de validação e execução seletiva durante o loop de correção. Se o
  projeto não tem suíte de testes, registrar literalmente
  `Sem suíte de testes detectada` (não omitir o campo). A skill `criar-plan`
  extrai esse comando do TRD quando existe ou pergunta no mini-modo.
