---
tipo: runbook
processo: spec-driven-development
plugins: [spec-driven-development]
skills: [escrever-prd, escrever-trd, preparar-execucao, orquestrar-execucao, implementar-task, validar-implementacao, revisao-documento-tecnico]
status: rascunho
ultima-validacao: 2026-07-21
tags: [runbook, spec-driven-development, software]
---

# Runbook — Desenvolvimento guiado por especificação (spec-driven)

Este guia mostra, do começo ao fim, como transformar uma ideia de funcionalidade em código pronto e conferido, **conversando com o Claude Code**. Cada etapa pesada é feita por uma *skill* (uma habilidade especializada do Claude Code) — você não edita documentos nem escreve código à mão; você descreve o que quer, aprova o que aparece, e segue para a próxima etapa.

A ideia central: primeiro registra-se **o que** a funcionalidade deve fazer (o comportamento), depois **como** construir, depois **constrói-se** tarefa por tarefa, e no fim **confere-se** se o que ficou pronto bate com o que foi combinado. Esse encadeamento evita o retrabalho de "codar primeiro, descobrir o que era pra ser depois".

Uma coisa muda conforme o tamanho do trabalho: na hora de preparar a construção, a ferramenta pode **quebrar a funcionalidade em fatias** — pedaços independentes que podem ser construídos ao mesmo tempo, sem um esperar o outro. Quando isso acontece, entra um passo a mais (o Passo 3), que dispara as fatias em paralelo. Quando não acontece, esse passo simplesmente não existe e você segue direto.

Este guia é para **qualquer pessoa**, mesmo sem conhecimento técnico. Termos técnicos aparecem explicados na primeira vez e estão reunidos no **Glossário**, no fim.

## O que você tem no início e no fim

| No início você tem | No fim você tem |
|---|---|
| Uma ideia de funcionalidade (uma frase ou um parágrafo do que precisa ser construído) | A funcionalidade implementada em código, com cada tarefa registrada em commits, e um relatório confirmando que o código bate com o que foi especificado |

O fecho tem um passo semi-manual (rodar a conferência final e, se você usa um repositório remoto, publicar as mudanças) — ver a seção **Passo manual**.

## 1. Como usar este runbook

- O processo é conduzido **conversando com o Claude Code**: você digita uma frase (os exemplos estão em cada passo, no campo **O que falar**) e a **skill certa é escolhida sozinha**.
- Em vários pontos a ferramenta **para e pede sua aprovação** (revisar um documento, aprovar como o trabalho foi fatiado, decidir sobre uma divergência). Isso é esperado — é onde você mantém o controle.
- Cada etapa pode levar **alguns minutos**. Faça **um passo de cada vez, na ordem**.
- **Nem todo passo se aplica sempre.** O Passo 1 (PRD) é opcional e vale a pena em projeto grande. O Passo 3 (orquestração) só existe se o Passo 2 tiver quebrado o trabalho em 2 ou mais fatias.

## 2. As skills deste processo (briefing)

### `[[escrever-prd]]` — registra o que a funcionalidade deve fazer (opcional)
Cria o **PRD** (Product Requirements Document — o documento de requisitos, em linguagem de negócio) descrevendo comportamento, regras e critérios de aceite. É a leitura para humanos e a fonte de verdade em projetos grandes. Se você descrever coisas demais de uma vez, ela detecta e **propõe dividir em vários PRDs** antes de escrever. → Doc completo: `[[escrever-prd]]`

### `[[preparar-execucao]]` — prepara o pacote de execução
Transforma a intenção em um **pacote de execução**: o **SPEC** (o contrato enxuto que a IA usa para construir e conferir), o **PLAN** (a abordagem técnica) e o **TASKS** (a lista de tarefas). É também aqui que ela decide se o trabalho vira **uma fatia só** ou **várias fatias** que podem correr em paralelo. → Doc completo: `[[preparar-execucao]]`

### `[[orquestrar-execucao]]` — dispara as fatias em paralelo (só com 2+ fatias)
Lê o **manifesto** das fatias, descobre quais podem correr juntas (uma "onda"), e dispara uma construção por fatia ao mesmo tempo, cada uma numa **área de trabalho isolada** para não atrapalhar as outras. Ao fim de cada onda, junta tudo de volta e libera a onda seguinte. → Doc completo: `[[orquestrar-execucao]]`

### `[[implementar-task]]` — constrói tarefa por tarefa
Executa a lista de tarefas, escreve o código, roda os testes e, a cada tarefa concluída e verde, salva um **commit** (um ponto de salvamento no histórico do código). É o motor da construção — com várias fatias, é ele que a orquestração dispara várias vezes em paralelo. → Doc completo: `[[implementar-task]]`

### `[[validar-implementacao]]` — confere e fecha
Ao final, verifica se o código entregue é coerente com o contrato, ajusta pequenas divergências, pergunta sobre as grandes, e **fecha o ciclo** marcando a funcionalidade como concluída. → Doc completo: `[[validar-implementacao]]`

### Transversais (opcionais, sob demanda)
- `[[escrever-trd]]` — cria o **TRD** (Technical Requirements Document — documento técnico global do projeto: stack, padrões, comando de teste) e registra **ADRs** (registros de decisão de arquitetura). Não é um passo da fila: é escrito uma vez e, quando existe, é carregado automaticamente como contexto pelas outras skills. → `[[escrever-trd]]`
- `[[revisao-documento-tecnico]]` — revisa qualquer documento (PRD, SPEC, PLAN, TASKS, TRD) antes de seguir, e aplica em lote as correções que tiverem evidência no próprio projeto. → `[[revisao-documento-tecnico]]`

## 3. Antes de começar (pré-requisitos)

**O que você precisa ter:**
- Uma ideia de funcionalidade — pode ser uma frase.
- Um projeto de código onde a funcionalidade será construída.

**Preparo técnico do ambiente** (feito uma vez):
- **Git** configurado no projeto (nome e e-mail; e chave de assinatura, se o projeto exigir). É o que permite salvar os commits a cada tarefa.
- **Git versão 2.5 ou mais nova** — necessário só para o caminho paralelo (Passo 3), que usa o recurso de *worktree*. Qualquer Git dos últimos anos serve.
- **Nada pendente sem salvar** no projeto antes de começar a construção. Tanto a construção quanto a orquestração param se encontrarem mudanças soltas.
- **Ferramenta de teste do projeto** (opcional, mas recomendada). Se o projeto não tiver testes, o fluxo funciona mesmo assim — a conferência de cada tarefa continua acontecendo. Se tiver, os testes precisam estar **passando antes de começar**: falha que já existia trava a construção, porque contaminaria a conferência de cada tarefa.

> **Como saber se está pronto?** Rode o Passo 2 com sua ideia. Se faltar alguma informação (como o comando de teste do projeto), a ferramenta **pergunta** antes de gerar qualquer arquivo.

## 4. Visão geral do fluxo

```
[Ideia de funcionalidade]
      │
      ▼
PASSO 1 · escrever-prd (opcional, projeto grande)  →  PRD em docs/prds/NNN-nome.md
      │                                                (pule em projeto pequeno)
      ▼
PASSO 2 · preparar-execucao   →  ela mostra o corte e pede sua aprovação
      │
      ├─── 1 fatia ────────────────────────────────┐
      │    .aidev/{nome}/ com SPEC + PLAN + TASKS  │
      │                                            ▼
      │                              PASSO 4 · implementar-task
      │                              (código + 1 commit por tarefa)
      │                                            │
      └─── 2+ fatias ──────────────────┐           │
           .aidev/{nome}-{fatia}/ …    │           │
           + .aidev/{nome}-manifest.md │           │
                                       ▼           │
                     PASSO 3 · orquestrar-execucao │
                     (ondas; 1 área isolada por    │
                      fatia; junta ao fim da onda; │
                      chama implementar-task) ─────┘
                                       │
                                       ▼
                     PASSO 5 · validar-implementacao
                     (uma vez por fatia)  →  relatório + status "concluido"
                                       │
                                       ▼
      [Passo manual: conferência final / publicar as mudanças]
```

## 5. Passo a passo

### Passo 1 — Registrar o que a funcionalidade faz · `[[escrever-prd]]`

Aqui você descreve, em linguagem de negócio, **o que** a funcionalidade precisa fazer: as regras, os casos especiais, os critérios que dizem "está pronto". A IA gera o PRD completo já a partir da sua descrição, marcando o que ela assumiu para você revisar. Se o que você descreveu for grande demais para um documento só, ela **propõe a divisão em vários PRDs** antes de escrever qualquer coisa. **Em projeto pequeno, pule este passo** — a especificação é escrita direto no Passo 2.

| | |
|---|---|
| **O que falar** | *"Cria um PRD para o cadastro de clientes com aprovação por e-mail"* |
| **O que ela pede** | Uma descrição da funcionalidade (problema, regras, restrições que você já conheça) |
| **Onde você aprova** | Duas vezes: se ela propuser dividir em vários PRDs, e depois no PRD em si — apresentado com as premissas marcadas, para você corrigir antes de salvar |
| **O que sai** | Um arquivo de PRD em `docs/prds/NNN-nome.md` (numerado em sequência) |

**Como verificar antes de seguir:** abra `docs/prds/` e confirme que existe o arquivo novo, com as regras (Rules) e os casos especiais (Edge cases) preenchidos em cada funcionalidade.

### Passo 2 — Preparar o pacote de execução · `[[preparar-execucao]]`

A IA transforma a intenção em um **pacote de execução**: o SPEC (o contrato de comportamento, enxuto, que a IA vai seguir), o PLAN (como construir) e o TASKS (a lista de tarefas). Com PRD, ela projeta o SPEC a partir dele; **sem PRD, ela entrevista você** e escreve o SPEC direto.

É também aqui que ela decide o **corte**: se o trabalho couber num pedaço só, sai um pacote único; se render mais de um pedaço independente e testável, saem **várias fatias**, cada uma com seu próprio pacote, mais um **manifesto** dizendo quais podem correr ao mesmo tempo e quais dependem de outra. Ela mostra esse corte e **espera sua aprovação** — é o momento certo de ajustar, porque mudar o corte depois custa retrabalho.

| | |
|---|---|
| **O que falar** | *"Prepara a execução do PRD 003"* — ou, sem PRD: *"Prepara a execução do login por magic link"* |
| **O que ela pede** | A referência ao PRD (número/nome) ou, sem PRD, a descrição da funcionalidade e o comando de teste do projeto |
| **Onde você aprova** | Ela lista as fatias propostas (o que cada uma cobre, o que roda em paralelo, o que espera o quê) antes de gravar qualquer arquivo |
| **O que sai** | **1 fatia:** a pasta `.aidev/{nome}/` com `SPEC.md`, `PLAN.md`, `TASKS.md`. **2+ fatias:** uma pasta `.aidev/{nome}-{fatia}/` por fatia, mais o manifesto `.aidev/{nome}-manifest.md` |

**Como verificar antes de seguir:** abra a pasta `.aidev/`. Se houver **um** diretório com os três arquivos, você segue para o **Passo 4**. Se houver **vários** diretórios e um arquivo terminado em `-manifest.md`, você segue para o **Passo 3**. No topo de cada arquivo há um cabeçalho com a linha `type:` (`spec`, `plan`, `tasks`) — é o formato padronizado (OKF) que o restante do fluxo espera.

### Passo 3 — Disparar as fatias em paralelo · `[[orquestrar-execucao]]`

> **Só faça este passo se o Passo 2 gerou 2 ou mais fatias** (existe um arquivo `-manifest.md`). Com uma fatia só, pule direto para o Passo 4.

A IA lê o manifesto e monta as **ondas**: na primeira onda entram as fatias que não dependem de ninguém; nas seguintes, as que ficaram esperando. Dentro de uma onda, cada fatia é construída **ao mesmo tempo** que as outras, cada uma numa **área de trabalho isolada** (um *worktree* — uma cópia separada do projeto), justamente para que os salvamentos de uma não atropelem os da outra. Terminada a onda, ela junta o trabalho de todas de volta no projeto principal e libera a onda seguinte.

Por baixo, quem constrói continua sendo o `[[implementar-task]]` do Passo 4 — a orquestração só o dispara várias vezes. Se você interromper no meio, pode chamar de novo: ela retoma de onde parou.

| | |
|---|---|
| **O que falar** | *"Executa as fatias do PRD 003 em paralelo"* ou *"Retoma a orquestração"* |
| **O que ela pede** | O manifesto do Passo 2 e o projeto **sem mudanças pendentes** (senão ela para e pede para você salvar ou descartar antes) |
| **Onde você aprova** | Ela para e devolve o controle quando uma fatia pausa, quando o merge dá conflito ou quando falha ao preparar uma área isolada |
| **O que sai** | Código de todas as fatias construído e reunido no projeto, com os commits de cada tarefa; um relatório dizendo o estado de cada fatia (concluída, pausada, bloqueada ou pendente) |

**Como verificar antes de seguir:** leia o relatório final e confirme que todas as fatias estão como **concluída**. Fatia **pausada** ou **bloqueada** precisa ser resolvida antes de validar (veja *Problemas comuns*).

### Passo 4 — Construir tarefa por tarefa · `[[implementar-task]]`

> Este é o passo para quem tem **uma fatia só**. Com várias fatias, o Passo 3 já chamou esta skill para você — pule para o Passo 5.

A IA executa a lista de tarefas: para cada uma, escreve o código, roda os testes e, quando a tarefa fica **verde** (tudo passando), salva um commit. Ela usa o SPEC como guia principal e só abre o PRD quando precisa entender o *porquê* de uma regra. Se bater numa lacuna (algo que o contrato não cobre), ela **para e pergunta**. Ela também mantém um arquivo de memória em `docs/MEMORY.md`, com o que aconteceu na sessão e as decisões que valem para o futuro — é o que permite retomar depois sem reler tudo.

| | |
|---|---|
| **O que falar** | *"Implementa as tasks do PRD 003"* ou *"Continua de onde parou"* |
| **O que ela pede** | O pacote pronto do Passo 2; nada pendente sem salvar; e os testes do projeto passando antes de começar |
| **Onde você aprova** | Ela para e devolve o controle em lacunas do contrato, falhas persistentes ou mudanças soltas fora do escopo |
| **O que sai** | Código implementado e um commit por tarefa concluída; as tarefas marcadas `[X]` no `TASKS.md`; o `docs/MEMORY.md` atualizado |

**Como verificar antes de seguir:** rode `git log` e confirme que há commits novos (um por tarefa). Abra o `TASKS.md` e confirme que as tarefas concluídas estão marcadas com `[X]`.

### Passo 5 — Conferir e fechar · `[[validar-implementacao]]`

A IA confere se o código entregue **bate com o contrato**: cada regra honrada, cada caso especial tratado, cada critério de aceite passando — e se o SPEC continua fiel ao PRD. Ao achar uma divergência, ela **avalia o tamanho primeiro**: as pequenas ela ajusta sozinha; as grandes ela **pausa e pergunta a você**. No fim, sem divergência grande em aberto, ela marca a funcionalidade como concluída.

**Com várias fatias, este passo se repete uma vez por fatia** — a validação trabalha um pacote de cada vez.

| | |
|---|---|
| **O que falar** | *"Valida a implementação do PRD 003"* ou *"Fecha o ciclo dessa feature"* |
| **O que ela pede** | O pacote implementado e os testes do projeto passando (falha que já existia faz ela parar antes de analisar) |
| **Onde você aprova** | Toda **divergência grande** é apresentada a você com as opções antes de qualquer ajuste |
| **O que sai** | Um relatório de conferência (cobertura, critérios, divergências) e o `status` do pacote — e do PRD, se houver — promovido para `concluido` |

**Como verificar antes de seguir:** leia o relatório e confirme que a linha "divergências grandes em aberto" está zerada e o veredito é `concluido`. Abra o `SPEC.md` e confirme que o `status:` no cabeçalho virou `concluido`.

## 6. Passo manual (fecho)

Fora das skills, restam ações suas:

1. **Rodar a conferência final por conta própria**, se quiser — os critérios "manuais" listados pela validação (ex.: verificação visual em tela) são feitos por você.
2. **Publicar as mudanças**, se o projeto usa repositório remoto: `git push` (ou abrir um Pull Request, conforme o costume da sua equipe). As skills salvam commits locais, mas **não publicam** nem fazem deploy.

## 7. Problemas comuns

| O que aparece | Por que acontece | O que fazer |
|---|---|---|
| A preparação recusa gerar o pacote | O PRD está com `status: concluido` (imutável) | Abra um PRD novo (Passo 1); PRDs concluídos não evoluem |
| A construção ou a orquestração para logo no início dizendo que há mudanças pendentes | Há mudanças soltas no projeto fora do escopo da tarefa | Salve, guarde (stash) ou descarte essas mudanças e chame de novo |
| A construção para dizendo que os testes já estavam falhando | Havia falha no projeto **antes** de começar; ela contaminaria a conferência de cada tarefa | Conserte a falha existente (ou peça ajuda a quem cuida do projeto) e chame de novo |
| A construção para com "lacuna no SPEC" | O contrato não cobre uma decisão de negócio necessária | Com PRD: ajuste via `[[escrever-prd]]` e reconcilie via `[[preparar-execucao]]`. Sem PRD: ajuste o SPEC via `[[preparar-execucao]]` |
| Retomei a execução e ela avisou de mudança no SPEC/PRD | O contrato mudou desde a última pausa | Rode `[[preparar-execucao]]` em modo reconciliação antes de continuar |
| A orquestração parou com **conflito ao juntar** as fatias | As fatias mexeram nos mesmos arquivos — sinal de que o corte do Passo 2 não era mesmo independente | Volte ao `[[preparar-execucao]]` e reconcilie o corte; a orquestração não resolve conflito |
| A orquestração reportou **erro ao preparar a área isolada** de uma fatia | Sobrou uma área de trabalho ou um ramo antigo com o mesmo nome | Peça a limpeza das áreas órfãs e rode a orquestração de novo — as outras fatias da onda seguiram normalmente |
| Uma fatia ficou **bloqueada** | Ela depende de outra fatia que pausou ou não terminou | Resolva a fatia de que ela depende (o relatório diz qual) e chame a orquestração de novo |
| A validação para numa "divergência grande" | O código contradiz o contrato, ou o ajuste mexeria no PRD | Escolha uma das opções que ela apresenta (corrigir o código, ajustar o documento, ou aceitar) |

## 8. Exemplo completo (do começo ao fim)

1. Você tem a ideia: "cadastro de clientes com confirmação por e-mail". Fala *"Cria um PRD para cadastro de clientes com confirmação por e-mail"* → sai `docs/prds/004-cadastro-clientes.md` (Passo 1).
2. Fala *"Prepara a execução do PRD 004"*. Ela responde que dá para quebrar em duas fatias e mostra o corte: `api` (cadastro e confirmação no servidor) e `ui` (a tela), com a `ui` dependendo da `api`. Você aprova → saem `.aidev/004-cadastro-clientes-api/` e `.aidev/004-cadastro-clientes-ui/`, cada uma com `SPEC.md`, `PLAN.md` e `TASKS.md`, mais `.aidev/004-cadastro-clientes-manifest.md` (Passo 2).
3. Fala *"Executa as fatias do PRD 004 em paralelo"* → a primeira onda constrói a `api` no ramo `exec/004-cadastro-clientes-api`, junta no projeto, e a segunda onda faz o mesmo com a `ui`. O relatório final mostra as duas como **concluída** (Passo 3 — ele chamou o `implementar-task` por baixo, então você não faz o Passo 4).
4. Fala *"Valida a implementação de 004-cadastro-clientes-api"* e depois *"…-ui"* → saem dois relatórios: critérios OK, `status` de cada pacote promovido a `concluido`, e o PRD 004 fechado (Passo 5).
5. Você roda `git push` para publicar (Passo manual).

Se o mesmo cadastro fosse pequeno e a preparação tivesse gerado **uma fatia só**, o caminho seria: sai `.aidev/004-cadastro-clientes/`, você fala *"Implementa as tasks do PRD 004"* (Passo 4) e depois *"Valida a implementação do PRD 004"* (Passo 5) — sem Passo 3.

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
| pacote (bundle) | O conjunto SPEC + PLAN + TASKS de uma funcionalidade, dentro de `.aidev/` |
| `.aidev/{nome}/` | A pasta onde vive o pacote de execução de uma funcionalidade |
| fatia | Um pedaço independente e testável da funcionalidade, com pacote próprio, que pode ser construído em paralelo com outras |
| manifesto | O arquivo `.aidev/{nome}-manifest.md`: índice das fatias, quem depende de quem e o que roda junto |
| onda | Um grupo de fatias que pode ser construído ao mesmo tempo, porque nenhuma depende de outra do grupo |
| worktree (área de trabalho isolada) | Uma cópia separada do projeto onde uma fatia é construída sem atrapalhar as outras |
| branch (ramo) | Uma linha paralela do histórico do código; cada fatia constrói na sua |
| merge (juntar) | Trazer o trabalho de um ramo de volta para o principal |
| slug | Nome curto e simplificado da funcionalidade, usado para nomear a pasta |
| commit | Ponto de salvamento no histórico do código (Git) |
| working tree | O estado atual dos arquivos do projeto ainda não salvos em commit |
| US (User Story) | Uma funcionalidade descrita do ponto de vista do usuário |
| status `concluido` | Marca no cabeçalho do documento indicando que aquele ciclo foi fechado. O PRD passa por `rascunho → pronto → em-progresso → concluido`; os arquivos do pacote, por `rascunho → pronto → em-execucao → concluido` |

## Manutenção

As skills usadas, a situação (`status`) e a data de validação ficam no frontmatter no topo deste arquivo. Este runbook está como **`rascunho`**: foi escrito a partir dos docs das skills, mas **ainda não foi rodado de ponta a ponta** — em especial o caminho de **2+ fatias** (Passo 3), que nunca foi executado de verdade. Promova para `validado` e atualize `ultima-validacao` depois de executar o processo inteiro com sucesso. Ao mudar qualquer skill do fluxo, revalide de ponta a ponta e atualize a data.
