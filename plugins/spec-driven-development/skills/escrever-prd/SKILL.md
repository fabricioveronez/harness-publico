---
name: escrever-prd
description: >
  Cria e edita Epics de alto nível e PRDs de feature, escolhendo um único tipo de
  artefato por execução. Use para formalizar uma iniciativa, Epic, MVP ou visão que
  coordena várias capacidades; para criar ou refinar requisitos de uma feature; ou
  para avaliar a granularidade e propor a decomposição de uma Epic. Epics preservam
  research, resultados e capacidades candidatas sem gerar PRDs. PRDs especificam
  comportamento e regras de negócio sem detalhar arquitetura ou implementação.
---

# Escrever PRD

Porta de entrada para dois artefatos de produto:

- **Epic** — direção de alto nível para um resultado que pode envolver várias capacidades.
- **PRD** — unidade autocontida de comportamento e regras de negócio para uma feature.

## Hard gate: um fluxo por execução

Escolha **Epic ou PRD antes de gerar ou editar qualquer arquivo**. Uma execução cria ou
edita no máximo um artefato e termina. A passagem de Epic para decomposição, de
decomposição para PRD ou de um PRD para o seguinte exige nova solicitação explícita.

- O fluxo Epic não cria nem edita PRDs.
- O fluxo PRD não cria, replaneja nem atualiza Epics.
- Decompor uma Epic produz somente uma proposta na conversa; não altera arquivos.

## Seleção do fluxo

### Epic

Escolha Epic quando o pedido mencionar explicitamente Epic ou iniciativa, ou quando
descrever um MVP, visão ou resultado amplo composto por capacidades que entregam partes
distintas de um mesmo objetivo.

Se o usuário pediu um PRD, mas o input contém várias features autocontidas unidas por um
resultado comum, não gere o PRD nem os documentos filhos. Explique o corte e proponha
trabalhar primeiro no nível da Epic. Aguarde confirmação.

Depois de escolher este fluxo, leia
[`references/fluxo-epic.md`](references/fluxo-epic.md). Leia o template indicado por ele
somente quando for gerar ou editar uma Epic.

### PRD

Escolha PRD quando o pedido descreve uma feature autocontida: o conjunto de comportamentos
e regras cujas decisões se explicam juntas e entregam um resultado observável.

Se o input mistura features sem um resultado agregador real, proponha PRDs separados e
aguarde o usuário escolher um. Dependência ou encadeamento entre features não impede o
corte; dependências reais vivem em `depends_on`.

Depois de escolher este fluxo, leia
[`references/fluxo-prd.md`](references/fluxo-prd.md). Leia o template indicado por ele
somente quando for gerar ou editar um PRD.

### Teste de granularidade

Para cada parte candidata, pergunte:

1. Ela se explica como uma capacidade ou feature reconhecível?
2. Ela entrega um resultado observável sem precisar absorver as regras das outras partes?
3. As decisões dela podem amadurecer separadamente?

Partes que passam no teste são separáveis. Se compartilham um objetivo maior, o conjunto é
candidato a Epic. Se não compartilham, são PRDs independentes. Rules, exceções e controles
que só tornam uma feature correta permanecem dentro do mesmo PRD.

## Protocolo compartilhado

1. Identifique criação, edição, análise ou decomposição antes de carregar o fluxo.
2. Inspecione o projeto e os artefatos existentes antes de perguntar fatos descobríveis.
3. Faça uma única pergunta fechada apenas quando uma lacuna tornar o artefato inutilizável
   ou quando Epic versus PRD continuar materialmente ambíguo.
4. Nos modos de criação e edição, produza um draft completo. Marque conteúdo inferido com
   `*(premissa — confirme ou corrija)*`; use “A definir” somente quando o usuário adiar a
   decisão explicitamente.
5. Mantenha comportamento, intenção e razão de negócio nos artefatos de produto. Stack,
   arquitetura e NFR global pertencem ao TRD; decisão técnica durável pertence a ADR;
   decomposição técnica e ordem de execução pertencem a PLAN/TASKS.
6. Apresente o draft, refine até aprovação, salve segundo o fluxo escolhido e pare.

## Entrada

O usuário pode fornecer problema, oportunidade, solução imaginada, evidências, restrições,
referências ou um arquivo existente. `$ARGUMENTS`, quando presente, é a descrição inicial.
