---
tipo: runbook
processo: spec-driven-development
plugins: [spec-driven-development]
skills: [escrever-prd, escrever-trd, preparar-execucao, implementar-task, validar-implementacao, revisao-documento-tecnico]
status: rascunho
ultima-validacao: 2026-07-13
tags: [runbook, spec-driven-development, software]
---

# Runbook — Desenvolvimento guiado por especificação (spec-driven)

Este guia mostra, do começo ao fim, como transformar uma ideia de funcionalidade em código pronto e conferido, **conversando com o Claude Code**. Cada etapa pesada é feita por uma *skill* (uma habilidade especializada do Claude Code) — você não edita documentos nem escreve código à mão; você descreve o que quer, aprova o que aparece, e segue para a próxima etapa.

A ideia central: primeiro registra-se **o que** a funcionalidade deve fazer (o comportamento), depois **como** construir, depois **constrói-se** task por task, e no fim **confere-se** se o que ficou pronto bate com o que foi combinado. Esse encadeamento evita o retrabalho de "codar primeiro, descobrir o que era pra ser depois".

Este guia é para **qualquer pessoa**, mesmo sem conhecimento técnico. Termos técnicos aparecem explicados na primeira vez e estão reunidos no **Glossário**, no fim.

## O que você tem no início e no fim

| No início você tem | No fim você tem |
|---|---|
| Uma ideia de funcionalidade (uma frase ou um parágrafo do que precisa ser construído) | A funcionalidade implementada em código, com cada tarefa registrada em commits, e um relatório confirmando que o código bate com o que foi especificado |

O fecho tem um passo semi-manual (rodar a conferência final e, se você usa um repositório remoto, publicar as mudanças) — ver a seção **Passo manual**.

## 1. Como usar este runbook

- O processo é conduzido **conversando com o Claude Code**: você digita uma frase (os exemplos estão em cada passo, no campo **O que falar**) e a **skill certa é escolhida sozinha**.
- Em vários pontos a ferramenta **para e pede sua aprovação** (revisar um documento, confirmar uma divisão, decidir sobre uma divergência). Isso é esperado — é onde você mantém o controle.
- Cada etapa pode levar **alguns minutos**. Faça **um passo de cada vez, na ordem**.
- Projetos **grandes** passam por todos os passos. Projetos **pequenos** podem pular o passo do PRD (Passo 1) — a especificação é escrita direto no Passo 2.

## 2. As skills deste processo (briefing)

### `[[escrever-prd]]` — registra o que a funcionalidade deve fazer (opcional)
Cria o **PRD** (Product Requirements Document — o documento de requisitos, em linguagem de negócio) descrevendo comportamento, regras e critérios de aceite. É a leitura para humanos e a fonte de verdade em projetos grandes. → Doc completo: `[[escrever-prd]]`

### `[[preparar-execucao]]` — prepara o pacote de execução
Gera três arquivos no pacote da funcionalidade: o **SPEC** (o contrato enxuto que a IA usa para construir e conferir), o **PLAN** (a abordagem técnica) e o **TASKS** (a lista de tarefas). Projeta o SPEC a partir do PRD; sem PRD, entrevista você e escreve o SPEC direto. → Doc completo: `[[preparar-execucao]]`

### `[[implementar-task]]` — constrói tarefa por tarefa
Executa a lista de tarefas em sequência, escreve o código, roda os testes e, a cada tarefa concluída e verde, salva um **commit** (um ponto de salvamento no histórico do código). → Doc completo: `[[implementar-task]]`

### `[[validar-implementacao]]` — confere e fecha
Ao final, verifica se o código entregue é coerente com o contrato, ajusta pequenas divergências, pergunta sobre as grandes, e **fecha o ciclo** marcando a funcionalidade como concluída. → Doc completo: `[[validar-implementacao]]`

### Transversais (opcionais, sob demanda)
- `[[escrever-trd]]` — cria o **TRD** (Technical Requirements Document — documento técnico global do projeto: stack, padrões, comando de teste) e registra **ADRs** (registros de decisão de arquitetura). Quando existe, é carregado automaticamente como contexto. → `[[escrever-trd]]`
- `[[revisao-documento-tecnico]]` — revisa qualquer documento (PRD, SPEC, PLAN, TRD) antes de seguir. → `[[revisao-documento-tecnico]]`

## 3. Antes de começar (pré-requisitos)

**O que você precisa ter:**
- Uma ideia de funcionalidade — pode ser uma frase.
- Um projeto de código onde a funcionalidade será construída.

**Preparo técnico do ambiente** (feito uma vez):
- **Git** configurado no projeto (nome e e-mail; e chave de assinatura, se o projeto exigir). É o que permite salvar os commits a cada tarefa.
- **Ferramenta de teste do projeto** (opcional, mas recomendada). Se o projeto não tiver testes, o fluxo funciona mesmo assim — a conferência de cada tarefa continua acontecendo.

> **Como saber se está pronto?** Rode o Passo 2 com sua ideia. Se faltar alguma informação (como o comando de teste do projeto), a ferramenta **pergunta** antes de gerar qualquer arquivo.

## 4. Visão geral do fluxo

```
[Ideia de funcionalidade]
      │
      ▼
PASSO 1 · escrever-prd (opcional, projeto grande)  →  PRD em docs/prds/
      │                                                (pule em projeto pequeno)
      ▼
PASSO 2 · preparar-execucao   →  pacote .aidev/{slug}/ com SPEC + PLAN + TASKS
      │
      ▼
PASSO 3 · implementar-task    →  código + um commit por tarefa concluída
      │
      ▼
PASSO 4 · validar-implementacao  →  relatório de conferência + ciclo fechado (status "concluido")
      │
      ▼
[Passo manual: rodar a conferência final / publicar as mudanças]
```

## 5. Passo a passo

### Passo 1 — Registrar o que a funcionalidade faz · `[[escrever-prd]]`

Aqui você descreve, em linguagem de negócio, **o que** a funcionalidade precisa fazer: as regras, os casos especiais, os critérios que dizem "está pronto". A IA gera o PRD completo já a partir da sua descrição, marcando o que ela assumiu para você revisar. **Em projeto pequeno, pule este passo** — a especificação é escrita direto no Passo 2.

| | |
|---|---|
| **O que falar** | *"Cria um PRD para o cadastro de clientes com aprovação por e-mail"* |
| **O que ela pede** | Uma descrição da funcionalidade (problema, regras, restrições que você já conheça) |
| **Onde você aprova** | A IA apresenta o PRD com as premissas marcadas; você corrige e aprova antes de salvar |
| **O que sai** | Um arquivo de PRD em `docs/prds/NNN-nome.md` |

**Como verificar antes de seguir:** abra `docs/prds/` e confirme que existe o arquivo novo, com as regras (Rules) e os casos especiais (Edge cases) preenchidos em cada funcionalidade.

### Passo 2 — Preparar o pacote de execução · `[[preparar-execucao]]`

A IA transforma a intenção em um **pacote de execução**: o SPEC (o contrato de comportamento, enxuto, que a IA vai seguir), o PLAN (como construir) e o TASKS (a lista de tarefas). Com PRD, ela projeta o SPEC a partir dele; **sem PRD, ela entrevista você** e escreve o SPEC direto.

| | |
|---|---|
| **O que falar** | *"Prepara a execução do PRD 003"* — ou, sem PRD: *"Prepara a execução do login por magic link"* |
| **O que ela pede** | A referência ao PRD (número/nome) ou, sem PRD, a descrição da funcionalidade e o comando de teste do projeto |
| **Onde você aprova** | A IA mostra um resumo (quantas tarefas, principais decisões, arquivos afetados) antes de gravar |
| **O que sai** | A pasta `.aidev/{slug}/` com três arquivos: `SPEC.md`, `PLAN.md`, `TASKS.md` |

**Como verificar antes de seguir:** abra a pasta `.aidev/{slug}/` e confirme que os três arquivos existem. No topo de cada um há um cabeçalho com a linha `type:` (`spec`, `plan`, `tasks`) — é o formato padronizado (OKF) que o restante do fluxo espera.

### Passo 3 — Construir tarefa por tarefa · `[[implementar-task]]`

A IA executa a lista de tarefas em sequência: para cada uma, escreve o código, roda os testes e, quando a tarefa fica **verde** (tudo passando), salva um commit. Ela usa o SPEC como guia principal e só abre o PRD quando precisa entender o *porquê* de uma regra. Se bater numa lacuna (algo que o contrato não cobre), ela **para e pergunta**.

| | |
|---|---|
| **O que falar** | *"Implementa as tasks do PRD 003"* ou *"Continua de onde parou"* |
| **O que ela pede** | Nada além do pacote pronto do Passo 2; um working tree limpo (sem mudanças soltas fora do escopo) |
| **Onde você aprova** | A IA para em lacunas ou falhas persistentes e devolve o controle com opções |
| **O que sai** | Código implementado e um commit por tarefa concluída; as tarefas marcadas `[X]` no `TASKS.md` |

**Como verificar antes de seguir:** rode `git log` e confirme que há commits novos (um por tarefa). Abra o `TASKS.md` e confirme que as tarefas concluídas estão marcadas com `[X]`.

### Passo 4 — Conferir e fechar · `[[validar-implementacao]]`

A IA confere se o código entregue **bate com o contrato**: cada regra honrada, cada caso especial tratado, cada critério de aceite passando. Ao achar uma divergência, ela **avalia o tamanho primeiro**: as pequenas ela ajusta sozinha; as grandes ela **pausa e pergunta a você**. No fim, sem divergência grande em aberto, ela marca a funcionalidade como concluída.

| | |
|---|---|
| **O que falar** | *"Valida a implementação do PRD 003"* ou *"Fecha o ciclo dessa feature"* |
| **O que ela pede** | O pacote implementado (Passo 3 concluído) |
| **Onde você aprova** | Toda **divergência grande** é apresentada a você com as opções antes de qualquer ajuste |
| **O que sai** | Um relatório de conferência (cobertura, critérios, divergências) e o `status` do pacote (e do PRD, se houver) promovido para `concluido` |

**Como verificar antes de seguir:** leia o relatório e confirme que a linha "divergências grandes em aberto" está zerada e o veredito é `concluido`. Abra o `SPEC.md` e confirme que o `status:` no cabeçalho virou `concluido`.

## 6. Passo manual (fecho)

Fora das skills, restam ações suas:

1. **Rodar a conferência final por conta própria**, se quiser — os critérios "manuais" listados pela validação (ex.: verificação visual em tela) são feitos por você.
2. **Publicar as mudanças**, se o projeto usa repositório remoto: `git push` (ou abrir um Pull Request, conforme o costume da sua equipe). As skills salvam commits locais, mas **não publicam** nem fazem deploy.

## 7. Problemas comuns

| O que aparece | Por que acontece | O que fazer |
|---|---|---|
| A preparação recusa gerar o pacote | O PRD está com `status: concluido` (imutável) | Abra um PRD novo (Passo 1); PRDs concluídos não evoluem |
| A construção para logo no início dizendo "working tree sujo" | Há mudanças soltas no projeto fora do escopo da tarefa | Salve, guarde (stash) ou descarte essas mudanças e chame de novo |
| A construção para com "lacuna no SPEC" | O contrato não cobre uma decisão de negócio necessária | Com PRD: ajuste via `[[escrever-prd]]` e reconcile via `[[preparar-execucao]]`. Sem PRD: ajuste o SPEC via `[[preparar-execucao]]` |
| A validação para numa "divergência grande" | O código contradiz o contrato, ou o ajuste mexeria no PRD | Escolha uma das opções que ela apresenta (corrigir o código, ajustar o documento, ou aceitar) |
| Retomei a execução e ela avisou de mudança no SPEC/PRD | O contrato mudou desde a última pausa | Rode `[[preparar-execucao]]` em modo reconciliação antes de continuar |

## 8. Exemplo completo (do começo ao fim)

1. Você tem a ideia: "cadastro de clientes com confirmação por e-mail". Fala *"Cria um PRD para cadastro de clientes com confirmação por e-mail"* → sai `docs/prds/004-cadastro-clientes.md` (Passo 1).
2. Fala *"Prepara a execução do PRD 004"* → sai a pasta `.aidev/004-cadastro-clientes/` com `SPEC.md`, `PLAN.md`, `TASKS.md` (Passo 2).
3. Fala *"Implementa as tasks do PRD 004"* → a IA constrói tarefa a tarefa; ao fim, `git log` mostra commits como `feat: cria endpoint de cadastro` e o `TASKS.md` está todo `[X]` (Passo 3).
4. Fala *"Valida a implementação do PRD 004"* → sai o relatório: 3/3 US cobertas, critérios OK, `status` do pacote e do PRD promovido a `concluido` (Passo 4).
5. Você roda `git push` para publicar (Passo manual).

## Glossário

| Termo | O que significa |
|---|---|
| Skill | Habilidade especializada do Claude Code, acionada por uma frase sua |
| PRD | Product Requirements Document — documento de requisitos em linguagem de negócio (o que a funcionalidade faz) |
| SPEC | O contrato enxuto de comportamento que a IA usa para construir e conferir (gerado no Passo 2) |
| PLAN | Documento com a abordagem técnica (como construir) |
| TASKS | A lista de tarefas de execução |
| TRD | Technical Requirements Document — documento técnico global do projeto (stack, padrões, comando de teste) |
| ADR | Registro de uma decisão de arquitetura relevante |
| OKF | Open Knowledge Format — o formato padronizado (markdown com cabeçalho) dos arquivos do pacote |
| `.aidev/{slug}/` | A pasta onde vive o pacote de execução (SPEC+PLAN+TASKS) de uma funcionalidade |
| slug | Nome curto e simplificado da funcionalidade, usado para nomear a pasta |
| commit | Ponto de salvamento no histórico do código (Git) |
| working tree | O estado atual dos arquivos do projeto ainda não salvos em commit |
| US (User Story) | Uma funcionalidade descrita do ponto de vista do usuário |
| status `concluido` | Marca no cabeçalho do documento indicando que aquele ciclo foi fechado |

## Manutenção

As skills usadas, a situação (`status`) e a data de validação ficam no frontmatter no topo deste arquivo. Este runbook está como **`rascunho`**: foi escrito a partir dos docs das skills, mas **ainda não foi rodado de ponta a ponta** — promova para `validado` e atualize `ultima-validacao` depois de executar o processo inteiro com sucesso. Ao mudar qualquer skill do fluxo, revalide de ponta a ponta e atualize a data.
