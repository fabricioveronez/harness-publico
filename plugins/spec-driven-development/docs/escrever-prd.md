# escrever-prd

Cria e edita PRDs (Product Requirements Documents) — o **documento humano** da feature, fonte
de verdade da intenção de produto. Trabalha em modo **draft-first**: gera o documento completo
imediatamente a partir do que o usuário fornecer, marcando as premissas inferidas inline
(`*(premissa — confirme ou corrija)*`) para revisão pontual, em vez de conduzir entrevista
longa. O PRD cobre problema, solução de produto, escopo, funcionalidades (User Stories com
Rules e Edge cases), critérios de aceite e métricas, fluxo de negócio e milestones.

Um PRD é uma **unidade de raciocínio de produto**: o conjunto de comportamento e regras cujas
decisões se explicam juntas. Quando o input cobre mais de uma feature, a skill **detecta e
propõe um split** em PRDs separados antes de gerar qualquer coisa, e cria os PRDs restantes em
sequência na mesma sessão. Além de especificar, o PRD é o **controle de estado** da feature,
via campo `status` e grafo de `depends_on`.

Detalhe técnico (stack, arquitetura, NFR global) fica no TRD; decisão arquitetural durável vira
ADR — a skill sinaliza e sugere registrar via `escrever-trd` (Modo Decision).

## Pré-requisitos e configuração

- Nenhuma configuração prévia. Basta uma descrição do que se quer construir (problema,
  ideia de solução, restrições conhecidas).
- **Modo edição** — a skill lê o PRD referenciado em `./docs/prds/`, verifica o `status` e
  preserva `prd_number`, nome do arquivo, `status` atual e os IDs de US e Milestone já
  atribuídos. USs novas recebem o próximo ID sequencial.
- **Local e nome do arquivo** — `./docs/prds/NNN-nome-em-kebab-case.md` (ex.:
  `003-autenticacao-oauth.md`). O número é sequencial, determinado varrendo o diretório, e
  gravado no campo `prd_number` do frontmatter. O diretório é criado se não existir; outro
  caminho pode ser informado pelo usuário.
- **Estrutura gerada** — segue `references/template-prd.md`, que também define o vocabulário de
  `status`: `rascunho | pronto | em-progresso | concluido`.

## Dependências externas

Nenhuma. A skill trabalha só com arquivos markdown do próprio projeto.

## Skills relacionadas

- **preparar-execucao** — o passo seguinte: projeta o `SPEC.md` a partir do PRD e gera o bundle
  de execução. É ela quem consome o PRD `pronto`.
- **revisao-documento-tecnico** — revisa o PRD antes de partir para a execução.
- **escrever-trd** — dona do TRD e dos ADRs. Decisão arquitetural durável identificada no input
  do PRD é roteada para o Modo Decision dela (`docs/adrs/`); o PRD apenas referencia em §8.
- **validar-implementacao** — fecha o ciclo e promove o `status` do PRD para `concluido`.
  Nenhuma outra skill edita o corpo do PRD.
- **brainstorm** — madurar a ideia antes de formalizar com `escrever-prd`.
- **banco-de-ideias** — registrar a ideia no Notion antes de escrever o PRD formal.

## Exemplos de uso

```
Quero criar um PRD para um sistema de autenticação com SSO

Cria um documento de requisitos para uma API de pagamentos

Preciso planejar uma feature de notificações em tempo real para o nosso app

Criar PRD: plataforma de agendamento de consultas médicas online

Ajusta o PRD 003 para incluir o fluxo de convite por e-mail

Refinar o PRD de pagamentos: faltou o edge case de reembolso parcial

Esse PRD está grande demais? Avalia a granularidade e me diz se vale quebrar
```

### Como funciona (resumo)

1. **Modo** — detecta criação vs. edição (referência a um PRD existente = edição).
2. **Análise de escopo** — detecta múltiplas features e **propõe o split** ("Detectei 3
   features… Começamos pelo PRD-A?"), aguardando confirmação. Só interrompe com pergunta quando
   há lacuna **bloqueante** (algo impossível de inferir); o resto é inferido e marcado.
3. **Draft** — gera o PRD completo de uma vez, com as premissas marcadas inline.
4. **Dependências** — varre `./docs/prds/`, avalia dependência real e específica com cada PRD
   existente e preenche `depends_on` no frontmatter, registrando o critério no Registro de
   Decisões.
5. **Refinamento** — aplica as correções do usuário até a aprovação (reavaliando `depends_on` se
   o escopo mudou).
6. **Salvar** — numera, nomeia e grava.
7. **Continuidade multi-PRD** — se havia split pendente, oferece seguir para o próximo PRD,
   reaproveitando as decisões do anterior como contexto.

## Limitações conhecidas

- **PRDs com `status: concluido` são imutáveis** — a skill interrompe no modo edição. Mudança
  de comportamento posterior abre um **novo** PRD, que pode referenciar o antigo.
- **Não transiciona `status`** — no modo criação salva sempre como `rascunho`; no modo edição
  preserva o status atual. As transições para `pronto`, `em-progresso` e `concluido` são das
  skills de preparação, execução e validação.
- **Não cobre o técnico** — stack, arquitetura, padrões e NFR global ficam no TRD; decisão
  arquitetural durável vira ADR. A skill **gera** o Fluxo de Negócio (§4, diagrama de jornada
  onde os pontos de decisão são regras) quando a ramificação não fica clara no texto, mas nunca
  topologia técnica (componentes, serviços, modelo de dados) — isso é o "Diagrama de
  Implementação" do PLAN.
- **Não decompõe em tasks** — milestone é **marco de produto** (conjunto coeso de USs que
  entrega algo anunciável), não fatia de execução. Passos, validação e ordem são do
  `preparar-execucao`. Não há número mínimo de milestones; **mais de ~6 é o sinal de que são
  várias features** e o corte deve ser reavaliado.
- **IDs são estáveis** — US01, US02, Milestone 1… não mudam depois de atribuídos, porque os
  artefatos seguintes referenciam por eles.
- Critérios de sucesso vagos ("deve funcionar bem", "boa performance") são reformulados até
  ficarem verificáveis ou marcados como premissa — não passam como estão.
- A qualidade do documento depende da riqueza do input: quanto mais contexto, menos premissas
  a revisar.

### Referências da skill

- `references/template-prd.md` — estrutura canônica do PRD, vocabulário de `status` e
  semântica dos milestones.
