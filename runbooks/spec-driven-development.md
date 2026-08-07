---
tipo: runbook
processo: spec-driven-development
plugins: [spec-driven-development]
skills: [escrever-prd, escrever-trd, fv-spec-driven, revisao-documento-tecnico]
status: validado
ultima-validacao: 2026-08-07
tags: [runbook, spec-driven-development, software]
---

# Runbook — Desenvolvimento guiado por especificação (spec-driven)

Este guia mostra, do começo ao fim, como transformar uma ideia de funcionalidade em código pronto e conferido, **conversando com o Claude Code**. Você não edita documentos nem escreve código à mão: descreve o que quer, aprova o que aparece, e segue.

A ideia central: primeiro registra-se **o que** a funcionalidade deve fazer (o comportamento) e **como se prova** que está certo; depois **constrói-se** tarefa por tarefa; no fim **confere-se** se o que ficou pronto bate com o que foi combinado. Esse encadeamento evita o retrabalho de "codar primeiro, descobrir o que era pra ser depois".

Uma coisa muda conforme o tamanho do trabalho: na preparação, a ferramenta pode **quebrar a funcionalidade em fatias** — pedaços independentes que podem ser construídos ao mesmo tempo. Quando isso acontece, entra um passo a mais. Quando não acontece, esse passo simplesmente não existe.

Este guia é para **qualquer pessoa**, mesmo sem conhecimento técnico. Termos técnicos aparecem explicados na primeira vez e estão reunidos no **Glossário**, no fim.

## O que você tem no início e no fim

| No início você tem | No fim você tem |
|---|---|
| Uma ideia de funcionalidade — pode ser uma frase, um documento de brainstorm, ou um PRD | A funcionalidade implementada, cada tarefa registrada em commits, e um relatório confirmando que o código bate com o que foi especificado |

O fecho tem um passo semi-manual (a conferência final que só uma pessoa pode fazer e, se você usa repositório remoto, publicar as mudanças) — ver **Passo manual**.

## 1. Como usar este runbook

- O processo é conduzido **conversando com o Claude Code**: você digita uma frase e a **skill certa é escolhida sozinha**.
- **Você não precisa saber em que fase está.** A skill principal olha o estado dos arquivos no disco e descobre sozinha o que fazer em seguida. Na dúvida, *"continua"* costuma bastar.
- Em vários pontos ela **para e pede sua aprovação** (aprovar como o trabalho foi fatiado, decidir sobre uma divergência). Isso é esperado — é onde você mantém o controle.
- Cada etapa pode levar **alguns minutos**. Faça **um passo de cada vez**.
- **Nem todo passo se aplica sempre.** O Passo 1 (PRD) é opcional. O Passo 3 (paralelo) só existe se a preparação tiver gerado 2 ou mais fatias.

## 2. As skills deste processo

### `[[fv-spec-driven]]` — o ciclo inteiro, em quatro modos

É a skill principal, e faz quase tudo. Ela tem quatro **modos**, e escolhe sozinha qual usar a partir do que já existe no projeto:

| Modo | O que faz |
|---|---|
| **Preparar** | transforma a intenção no pacote de execução e decide se vira uma fatia ou várias |
| **Orquestrar** | roda as fatias em paralelo, cada uma numa área de trabalho isolada |
| **Implementar** | escreve o código, tarefa por tarefa, salvando um commit a cada uma |
| **Validar** | confere o código contra o combinado e fecha o ciclo |

→ Doc completo: `[[fv-spec-driven]]`

### Skills de documento (opcionais, sob demanda)

Estas cuidam de documentos que a skill principal **lê mas nunca edita**:

- `[[escrever-prd]]` — cria o **PRD** (documento de requisitos em linguagem de negócio). Vale em projeto grande; em projeto pequeno, pule.
- `[[escrever-trd]]` — cria o **TRD** (documento técnico do projeto: stack, padrões, comando de teste) e registra **ADRs** (decisões de arquitetura). Escrito uma vez; quando existe, é lido automaticamente.
- `[[revisao-documento-tecnico]]` — revisa qualquer documento antes de seguir.

## 3. Antes de começar

**O que você precisa ter:**
- Uma ideia de funcionalidade — uma frase, um documento de brainstorm, ou um PRD.
- Um projeto de código onde ela será construída.

**Preparo do ambiente** (uma vez):
- **Git** configurado (nome, e-mail e chave de assinatura se o projeto exigir).
- **Git 2.5 ou mais novo** — só para o caminho paralelo, que usa *worktree*. Qualquer Git dos últimos anos serve.
- **Nada pendente sem salvar** antes de começar a construção.
- **Ferramenta de teste** (opcional, recomendada). Sem testes o fluxo funciona; com testes, eles precisam estar passando antes de começar — com uma exceção importante, explicada no Passo 4.

> **Como saber se está pronto?** Rode o Passo 2. Se faltar informação (como o comando de teste), a ferramenta **pergunta** antes de gerar qualquer arquivo.

## 4. Visão geral

```
[Ideia · brainstorm · PRD]
      │
      ▼
PASSO 1 · escrever-prd (opcional, projeto grande)  →  docs/prds/NNN-nome.md
      │
      ▼
PASSO 2 · fv-spec-driven, modo Preparar
      │    → mostra o corte e pede sua aprovação
      │    → grava .aidev/ e COMMITA o pacote
      │
      ├─── 1 fatia ──────────────────────────────┐
      │    .aidev/{nome}/ com SPEC + PLAN + TASKS│
      │                                          ▼
      │                          PASSO 4 · modo Implementar
      │                          (código + 1 commit por tarefa)
      │                                          │
      └─── 2+ fatias ────────────────┐           │
           .aidev/{nome}-{fatia}/ …  │           │
           + .aidev/{nome}-manifest.md│          │
                                     ▼           │
                     PASSO 3 · modo Orquestrar   │
                     (ondas; 1 área isolada por  │
                      fatia; junta ao fim) ──────┘
                                     │
                                     ▼
                     PASSO 5 · modo Validar
                     (uma vez por fatia)  →  relatório + fechamento
                                     │
                                     ▼
      [Passo manual: conferência final / publicar]
```

## 5. Passo a passo

### Passo 1 — Registrar o que a funcionalidade faz · `[[escrever-prd]]`

Descreva, em linguagem de negócio, **o que** a funcionalidade precisa fazer. A IA gera o PRD completo a partir da sua descrição, marcando o que assumiu. Se o que você descreveu for grande demais, ela propõe dividir em vários PRDs. **Em projeto pequeno, pule** — a especificação sai direto no Passo 2.

| | |
|---|---|
| **O que falar** | *"Cria um PRD para o cadastro de clientes com aprovação por e-mail"* |
| **O que ela pede** | A descrição (problema, regras, restrições que você já conheça) |
| **Onde você aprova** | Duas vezes: se propuser dividir em vários PRDs, e no PRD em si |
| **O que sai** | `docs/prds/NNN-nome.md` |

**Como verificar:** abra `docs/prds/` e confirme que as regras (Rules) e os casos especiais (Edge cases) estão preenchidos.

### Passo 2 — Preparar o pacote de execução · modo **Preparar**

A IA transforma a intenção num **pacote de execução**: o SPEC (o contrato de comportamento **e como cada ponto se prova**), o PLAN (como construir) e o TASKS (a lista de tarefas).

A entrada pode ser um PRD, **um documento de brainstorm** ou só uma descrição sua. Com brainstorm, ela trata o documento como matéria-prima e não como contrato: o que foi decidido vira regra, o que ficou em aberto vira **premissa visível** (nunca decisão silenciosa), e o que foi **descartado** continua descartado.

É aqui que ela decide o **corte**: um pedaço só, ou **várias fatias** que podem correr ao mesmo tempo. Ela mostra o corte, diz **quanto paralelismo isso realmente entrega**, e espera sua aprovação — é o momento barato de mudar.

Ao final, ela **salva o pacote em commit**. Isso não é detalhe: o Passo 3 cria cópias do projeto a partir do último commit, e um pacote não salvo simplesmente não apareceria lá dentro.

| | |
|---|---|
| **O que falar** | *"Prepara a execução do PRD 003"* · *"Prepara a execução do que está em docs/brainstorm-x.md"* · *"Prepara a execução do login por magic link"* |
| **O que ela pede** | A referência ao PRD/documento, ou a descrição; e o comando de teste do projeto, se não houver TRD |
| **Onde você aprova** | Ela lista as fatias propostas, o que roda em paralelo e o ganho real de paralelismo, antes de gravar |
| **O que sai** | **1 fatia:** `.aidev/{nome}/` com os três arquivos. **2+ fatias:** uma pasta por fatia mais `.aidev/{nome}-manifest.md`. Em ambos os casos, **commitado** |

**Como verificar:** abra `.aidev/`. Um diretório com os três arquivos → siga para o **Passo 4**. Vários diretórios mais um arquivo `-manifest.md` → siga para o **Passo 3**. Confira também que `git status` está limpo — o pacote deve ter entrado em commit.

> **Sobre o plano de teste.** No SPEC, cada critério de aceite tem um código (`CA01`, `CA02`…), um nível (unitário, integração, ponta a ponta, manual) e um **alvo** — o arquivo de teste ou o comando que o prova. As tarefas apontam para esses códigos. É isso que permite conferir cobertura por contagem, em vez de por impressão.

### Passo 3 — Rodar as fatias em paralelo · modo **Orquestrar**

> **Só faça este passo se o Passo 2 gerou 2 ou mais fatias.** Com uma fatia só, pule para o Passo 4.

A IA lê o manifesto e monta as **ondas**: primeiro as fatias que não dependem de ninguém, depois as que ficaram esperando. Dentro de uma onda, cada fatia é construída **ao mesmo tempo** que as outras, cada uma numa **área de trabalho isolada** (um *worktree* — uma cópia separada do projeto), para que os salvamentos de uma não atropelem os da outra. Terminada a onda, ela junta tudo de volta, consolida as anotações de memória e libera a onda seguinte.

Por baixo, quem constrói é o modo Implementar do Passo 4 — a orquestração só o dispara várias vezes.

| | |
|---|---|
| **O que falar** | *"Roda as fatias do PRD 003 em paralelo"* · *"Executa o manifesto"* · *"Continua"* |
| **O que ela pede** | O projeto **sem mudanças pendentes** e o pacote já salvo em commit |
| **Onde você aprova** | Ela devolve o controle quando uma fatia pausa, quando o merge dá conflito, ou quando falha ao preparar uma área isolada |
| **O que sai** | Código de todas as fatias reunido no projeto, com os commits de cada tarefa, e um relatório do estado de cada fatia |

**Como verificar:** o relatório deve mostrar todas as fatias como **concluída**. Fatia **pausada** ou **bloqueada** precisa ser resolvida antes de validar.

> **Conflito ao juntar** significa que as fatias mexeram nos mesmos arquivos — ou seja, o corte não era mesmo independente. A ferramenta **não** resolve isso sozinha, e não deve: ela para e devolve ao Passo 2 para reconciliar o corte.

### Passo 4 — Construir tarefa por tarefa · modo **Implementar**

> Este é o passo de quem tem **uma fatia só**. Com várias fatias, o Passo 3 já chamou este modo — pule para o Passo 5.

Para cada tarefa: escreve o código, roda os testes e, quando fica **verde**, salva um commit. Se um teste falha, tenta corrigir por até 5 tentativas. Se bater numa lacuna — algo que o contrato não cobre — ela **para e pergunta**, sem inventar regra de negócio.

Ela mantém um arquivo de memória (`docs/MEMORY.md`) com decisões e lições que valem para o futuro, e é o que permite retomar depois sem reler tudo.

| | |
|---|---|
| **O que falar** | *"Implementa as tasks do PRD 003"* · *"Continua de onde parou"* |
| **O que ela pede** | O pacote pronto do Passo 2 e nada pendente sem salvar |
| **Onde você aprova** | Ela devolve o controle em lacunas do contrato, falhas persistentes ou mudanças soltas fora do escopo |
| **O que sai** | Código, um commit por tarefa, tarefas marcadas `[X]` no `TASKS.md`, e `docs/MEMORY.md` atualizado |

**Como verificar:** rode `git log` e confirme os commits novos (um por tarefa). Abra o `TASKS.md` e confirme os `[X]`.

> **Sobre "os testes precisam estar passando".** Há uma exceção que confunde: num projeto onde os testes do contrato já existem mas o código ainda não, a suíte começa **vermelha por definição**. Isso é esperado, e a ferramenta distingue esse caso de uma falha alheia. Ela só para quando a falha está **fora** do que a fatia vai construir.

### Passo 5 — Conferir e fechar · modo **Validar**

A IA confere se o código **bate com o contrato**: cada regra honrada, cada caso especial tratado, cada critério de aceite passando. Ao achar divergência, avalia o tamanho: as pequenas ela ajusta no documento; as grandes ela **pausa e pergunta**.

**Com várias fatias, este passo se repete uma vez por fatia.**

| | |
|---|---|
| **O que falar** | *"Valida a implementação do PRD 003"* · *"Fecha o ciclo dessa feature"* |
| **O que ela pede** | O pacote implementado e a suíte de testes passando |
| **Onde você aprova** | Toda **divergência grande** é apresentada com as opções antes de qualquer ajuste |
| **O que sai** | Um relatório (cobertura, critérios, divergências) e o fechamento por status |

**Como verificar:** leia o relatório. A linha "divergências grandes em aberto" deve estar zerada, e a linha **Fechamento** diz se o ciclo inteiro fechou ou quantas fatias ainda faltam.

> **Por que o PRD não fecha na primeira fatia.** Com várias fatias, a ferramenta fecha o pacote daquela fatia mas **mantém o PRD e o manifesto abertos** até a última fechar. É proposital: PRD concluído é imutável, e fechá-lo cedo trancaria as fatias irmãs — elas não poderiam mais ser implementadas nem ajustadas. O relatório sempre diz quais faltam.

## 6. Passo manual (fecho)

1. **Rodar a conferência final que só você pode fazer** — os critérios marcados como *manual* no relatório (ex.: verificação visual de tela).
2. **Publicar as mudanças**, se o projeto usa repositório remoto: `git push`, ou abrir um Pull Request. As skills salvam commits locais, mas **não publicam** nem fazem deploy.

## 7. Problemas comuns

| O que aparece | Por que acontece | O que fazer |
|---|---|---|
| A preparação recusa gerar o pacote | O PRD está com `status: concluido` (imutável) | Abra um PRD novo; PRDs concluídos não evoluem |
| A orquestração para dizendo que o pacote não está salvo | O `.aidev/` não entrou em commit, e a área isolada é criada a partir do último commit | Peça para salvar o pacote em commit e rode de novo |
| A construção para dizendo que há mudanças pendentes | Há mudanças soltas **fora** do escopo da tarefa | Salve, guarde (stash) ou descarte **essas** mudanças. Atenção: o pacote em `.aidev/` **não** deve ser descartado |
| A construção para com "lacuna no contrato" | O contrato não cobre uma decisão de negócio necessária | Com PRD: ajuste via `[[escrever-prd]]` e reconcilie. Sem PRD: ajuste o SPEC pedindo reconciliação |
| Retomei e ela avisou de mudança no contrato | Alguém editou o SPEC ou o PRD desde a pausa | Peça reconciliação antes de continuar |
| A tarefa esgotou as 5 tentativas e, ao retomar, ela não tenta mais 5 | O orçamento é **por tarefa**, não por vez que você chama | É proposital: sem isso, uma tarefa impossível repetiria para sempre. Ou você dá uma abordagem nova, ou o problema é do contrato |
| A orquestração parou com **conflito ao juntar** | As fatias mexeram nos mesmos arquivos — o corte não era independente | Volte ao Passo 2 e reconcilie o corte; ela não resolve conflito sozinha |
| Uma área isolada não pôde ser removida | A fatia deixou arquivo não salvo | Verifique o que sobrou antes de forçar a remoção — forçar descarta o que estiver lá |
| Uma fatia ficou **bloqueada** | Depende de outra fatia que pausou | Resolva a fatia de que ela depende (o relatório diz qual) e chame de novo |
| A validação para numa "divergência grande" | O código contradiz o contrato, ou o ajuste mexeria no PRD | Escolha uma das opções apresentadas (corrigir o código, ajustar o documento, ou aceitar) |
| Ela avisa que o pacote está em "formato legado" | Bundle criado pelo fluxo antigo, com critérios em prosa | Funciona assim mesmo, com uma conferência menos precisa. Peça a migração para o formato com códigos quando puder |

## 8. Exemplo completo

1. Você tem a ideia: "cadastro de clientes com confirmação por e-mail". Fala *"Cria um PRD para cadastro de clientes com confirmação por e-mail"* → sai `docs/prds/004-cadastro-clientes.md` (Passo 1).
2. Fala *"Prepara a execução do PRD 004"*. Ela responde que dá para quebrar em duas fatias e mostra o corte: `api` e `ui`, com a `ui` dependendo da `api` — e avisa que isso entrega 1× de paralelismo, perguntando se compensa ou se prefere uma fatia só. Você aprova as duas → saem os dois pacotes, o manifesto, e um commit com tudo (Passo 2).
3. Fala *"Roda as fatias do PRD 004 em paralelo"* → a primeira onda constrói a `api` numa área isolada, junta no projeto, e a segunda faz o mesmo com a `ui`. O relatório mostra as duas como **concluída** (Passo 3 — ele chamou o modo Implementar por baixo, então você não faz o Passo 4).
4. Fala *"Valida a implementação da fatia api"* → relatório com os critérios OK, pacote da `api` fechado, e a linha **Fechamento** avisando que o conjunto aguarda a `ui`. Depois *"…da fatia ui"* → segundo relatório, e aí sim manifesto e PRD 004 fecham juntos (Passo 5).
5. Você roda `git push` (Passo manual).

Se a mesma feature fosse pequena e a preparação tivesse gerado **uma fatia só**: sai `.aidev/004-cadastro-clientes/`, você fala *"Implementa as tasks do PRD 004"* (Passo 4) e depois *"Valida a implementação do PRD 004"* (Passo 5) — sem Passo 3.

## Glossário

| Termo | O que significa |
|---|---|
| Skill | Habilidade especializada do Claude Code, acionada por uma frase sua |
| Modo | Uma das quatro fases dentro da skill principal; ela escolhe sozinha qual usar |
| PRD | Documento de requisitos em linguagem de negócio (o que a funcionalidade faz) |
| SPEC | O contrato de comportamento **e** como cada ponto se prova |
| PLAN | A abordagem técnica (como construir), incluindo a estratégia de teste |
| TASKS | A lista de tarefas de execução |
| TRD | Documento técnico global do projeto (stack, padrões, comando de teste) |
| ADR | Registro de uma decisão de arquitetura |
| pacote (bundle) | O conjunto SPEC + PLAN + TASKS de uma funcionalidade, dentro de `.aidev/` |
| fatia | Um pedaço independente e testável da funcionalidade, com pacote próprio |
| manifesto | O arquivo que indexa as fatias, diz quem depende de quem e o que roda junto |
| onda | Um grupo de fatias que pode ser construído ao mesmo tempo |
| paralelismo efetivo | Fatias ÷ ondas. Perto de 1 quer dizer que o corte é quase sequencial |
| critério de aceite (`CA01`…) | Um ponto do contrato com nível, e com o teste ou comando que o prova |
| worktree (área isolada) | Cópia separada do projeto onde uma fatia é construída sem atrapalhar as outras |
| branch (ramo) | Linha paralela do histórico do código; cada fatia constrói na sua |
| merge (juntar) | Trazer o trabalho de um ramo de volta para o principal |
| commit | Ponto de salvamento no histórico do código |
| working tree | O estado atual dos arquivos ainda não salvos em commit |
| US (User Story) | Uma funcionalidade descrita do ponto de vista do usuário |
| status `concluido` | Marca indicando que aquele ciclo foi fechado |

## Manutenção

As skills usadas, a situação e a data de validação ficam no frontmatter, no topo.

Este runbook está como **`validado`**: o fluxo foi executado de ponta a ponta, incluindo o caminho de 2+ fatias, em seis ensaios com 44 verificações automáticas. O que os ensaios encontraram foi corrigido na skill antes desta escrita.

Dois pontos ainda não cobertos por ensaio, para quem for revalidar: uma onda com **3+ fatias** simultâneas (o maior testado foi 2), e uma fatia que **pausa no meio de uma onda** e é retomada depois. Ao mudar a skill, revalide de ponta a ponta e atualize a data.
