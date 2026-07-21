---
name: escrever-prd
description: >
  Escreve PRDs (Product Requirements Documents) — cria novos ou edita existentes
  que ainda não foram concluídos. Funciona no modo draft-first: gera o documento
  completo imediatamente a partir do que o usuário fornecer, marcando premissas
  inferidas inline para revisão pontual — sem entrevistas longas. Quando o input
  cobre múltiplas features, detecta automaticamente e propõe divisão em PRDs
  separados, criando-os em sequência na mesma sessão. Cada PRD é autocontido
  e foca em comportamento e regras de negócio; detalhes técnicos ficam em TRD/ADR.
  Use quando o usuário quiser criar ou editar um PRD, documento de requisitos,
  especificação de feature, planejar uma funcionalidade, definir escopo de uma entrega,
  documentar requisitos, ou avaliar a quebra/granularidade de um PRD — mesmo que não use
  o termo "PRD" explicitamente. Também quando mencionar "requisitos do produto",
  "spec de feature", "escopo da feature", "documento de requisitos", "refinar PRD",
  "ajustar PRD", "quebra de PRD", "granularidade de PRD", ou fornecer uma descrição longa
  de funcionalidades para especificar.
---

# Escrever PRD

Cria e edita PRDs de feature. Um PRD é uma **unidade de raciocínio de produto**: o conjunto
de comportamento e regras de negócio cujas decisões se explicam juntas. É **documento humano**
— a fonte de verdade da intenção do produto. Descreve a feature de forma completa em
comportamento e regra de negócio; a IA o consulta sob demanda para o *porquê* e implementa a
partir do SPEC (derivado dele em `preparar-execucao`). O contexto técnico para implementar vem
do TRD (carregado junto na implementação). O campo de referências conecta PRDs entre si e a
recursos externos quando necessário.

A skill cobre tanto a criação do PRD quanto a edição de PRDs existentes que ainda
não foram concluídos — PRDs com `status: concluido` são imutáveis e não devem ser
editados por esta skill.

## Papel do PRD no fluxo

O PRD cumpre dois papéis:

1. **Spec de feature** — documento autocontido de comportamento e regras de negócio, usado para implementar a feature
2. **Controle de estado** — fonte de verdade do ciclo de vida da feature, via campo `status` e grafo de `depends_on`

Princípios que decorrem disso:

- **Imutabilidade em `concluido`** — quando o status chega a `concluido`, o PRD congela e vira registro histórico. Mudanças posteriores de comportamento devem abrir um novo PRD, não editar um concluído
- **Progressive disclosure via `depends_on`** — dependências entre PRDs são declaradas explicitamente; o agente só lê um PRD dependente quando o contexto da implementação exigir
- **Separação de responsabilidades** — PRD cobre comportamento e regra de negócio; TRD e ADR cobrem restrições técnicas, stack e decisões de arquitetura. O PRD **referencia** o artefato técnico, mas não o **dirige, dimensiona nem rastreia** — a forma do PRD é decidida pelo produto, não pela execução
- **IDs estáveis** — USs e Milestones recebem IDs (US01, Milestone 1...) que não mudam após atribuídos, porque artefatos futuros (planejamento, tasks) referenciam por esses IDs

## Entrada

O usuário fornece uma descrição do que quer construir, podendo incluir:

- Descrição do problema ou oportunidade
- Ideia de solução
- Contexto técnico
- Restrições conhecidas

$ARGUMENTS — se fornecido, usar como descrição inicial da feature.

## Fluxo de Execução

### 1. Identificação do modo

Antes de tudo, identificar se a solicitação é de **criação** ou **edição**:

- **Criação** — o usuário descreve uma feature nova ou não referencia nenhum PRD existente
- **Edição** — o usuário referencia um PRD específico (por número, nome ou arquivo) ou pede ajuste/refinamento de algo existente

No modo edição:
1. Ler o PRD referenciado em `./docs/prds/`
2. Verificar o `status` — se for `concluido`, interromper e avisar o usuário que PRDs concluídos são imutáveis e mudanças de comportamento devem abrir um novo PRD
3. Para PRDs em `rascunho`, `pronto` ou `em-progresso`, prosseguir com a edição preservando `prd_number`, IDs de US e Milestones já atribuídos

### 2. Análise de Escopo e Lacunas Bloqueantes

Antes de gerar, fazer duas verificações rápidas:

**2a. Detecção de múltiplas features**

O teste da unidade não é desconexão — é auto-suficiência. Um PRD cobre **uma** feature quando
**cada parte se explica sozinha e entrega algo observável ao usuário**. Se o input tem partes
que passam nesse teste separadamente, são features distintas — **ainda que dependentes entre
si**. Dependência é normal e vive no `depends_on` (uma feature encadeada não deixa de ser uma
feature própria); não é ela que impede o corte.

**Sinal de sanidade:** se a feature exige muitos marcos de produto (na prática, mais de ~6),
provavelmente são várias features — reavalie o corte. Poucos marcos não forçam nada: uma
feature pequena pode ter 1 ou 2 marcos legítimos.

Se detectar múltiplas features, **propor split concreto antes de gerar**:

```
Detectei 3 features no input. Sugiro criar:
  PRD-A: [nome da feature A]
  PRD-B: [nome da feature B]
  PRD-C: [nome da feature C]

Começamos pelo PRD-A?
```

Aguardar confirmação ou ajuste do corte. Registrar internamente a lista de PRDs pendentes.

**2b. Lacunas bloqueantes**

Verificar se há informação sem a qual o draft seria inutilizável — algo impossível de inferir com razoabilidade. Exemplos de lacuna bloqueante real: não consegue determinar o domínio da feature nem o sistema em que se insere.

Se houver lacuna bloqueante: **uma pergunta fechada** (com opções quando possível), sem entrevista. Qualquer outra lacuna — inferir e marcar no draft.

Se não houver: gerar imediatamente.

### 3. Geração do Draft com Premissas

Gerar o PRD completo **imediatamente**, sem aguardar mais informações. O que não foi fornecido é inferido e marcado inline.

**Formato de premissa:**
```markdown
- Token expirado → redirecionar para login *(premissa — confirme ou corrija)*
```

Usar `*(premissa — confirme ou corrija)*` em qualquer conteúdo inferido: rules, edge cases, critérios de aceite, escopo negativo, milestones. O usuário revisa texto concreto — não responde perguntas abstratas.

**Geração:**
1. Ler o template em `references/template-prd.md`
2. Gerar o PRD completo preenchendo todas as seções
3. Inferir rules e edge cases que não foram fornecidos, marcando cada um como premissa
4. Apresentar o draft ao usuário para revisão pontual

Regras de geração:
- Usar linguagem clara e objetiva — evitar jargão desnecessário
- Preencher todas as seções — marcar como premissa o que foi inferido; só usar "A definir" para o que o usuário explicitamente deixou em aberto
- O PRD é autocontido em **comportamento e regra de negócio** — não em contexto técnico. Stack, arquitetura e padrões vêm do TRD (carregado junto na implementação); a seção Contexto traz só um ponteiro quando relevante, sem duplicar stack
- Cada funcionalidade deve ser uma User Story (US) com ID sequencial (US01, US02...)
- Cada US deve conter: user story no formato "Como [persona], quero [ação], para [benefício]", Rules (regras de negócio e comportamentos esperados) e Edge cases (situações anômalas com comportamento esperado)
- Cada US deve ter pelo menos uma Rule e um Edge case — inferir os mais prováveis quando não fornecidos, marcando como premissa
- Edge cases seguem o formato: "[situação anômala] → [comportamento esperado]"
- Critérios de aceite (§5a) cobrem funcionais e não-funcionais **específicos da feature** — tempo de resposta, disponibilidade e capacidade entram quando têm razão de negócio (registrar o limiar **e o porquê**). NFR global do projeto (p95 geral, uptime, criptografia) mora no TRD, não no PRD. Métricas de sucesso (baseline→meta) vão em §5b
- Critérios vagos como "deve funcionar bem" ou "boa performance" não são aceitáveis — reformular até que sejam objetivamente verificáveis; se não houver dados suficientes, marcar como premissa
- Um **milestone é um marco de produto**: um conjunto coeso de funcionalidades que entrega algo ao usuário — algo que se anunciaria como conquista, não uma fatia de execução. Cada milestone é definido por **quais USs cobre** (por ID), por uma **justificativa de por que é um marco** (auto-avaliação: se a justificativa sai forçada, provavelmente é tarefa disfarçada ou dois marcos espremidos) e por um **checklist de aceite** (critérios de §5a filtrados pelas USs do marco, marcáveis pelo Aprovador após a implementação). **Sem número mínimo** de milestones; o teto de ~6 é o sinal de sanidade do 2a. Não detalhar tarefas técnicas nem ordem de execução no milestone — a decomposição (passos, validação, ordem) é do `preparar-execucao`
- Incluir o **Fluxo de Negócio** (§4, diagrama de jornada/processo onde os pontos de decisão são regras) apenas quando a ramificação de regra não ficar clara no texto. Topologia técnica (componentes/serviços, modelo de dados) não entra no PRD — fica no "Diagrama de Implementação" do PLAN
- A seção "Fora do escopo" é obrigatória — inferir itens óbvios de exclusão quando não fornecidos, marcando como premissa
- O "Registro de Decisões" registra decisões **de produto** e premissas de negócio significativas. Decisão arquitetural/técnica não entra — vira ADR
- Se o input trouxer uma **decisão arquitetural durável** (escolha de banco, estratégia de auth, padrão arquitetural, lib estruturante), não a incorpore como decisão de produto: sinalize que é um ADR e sugira registrar via `escrever-trd` Modo Decision (`docs/adrs/`). O PRD pode referenciá-la em §8
- A seção "Referências" lista links para documentação, issues, PRDs relacionados, APIs, designs ou recursos externos mencionados no contexto
- O campo `references` no frontmatter deve conter os mesmos links da seção Referências em formato de lista
- IDs de US (US01, US02...) e de Milestone (Milestone 1, 2...) são estáveis — uma vez atribuídos não mudam, pois artefatos futuros (planejamento, tasks) referenciam por esses IDs
- No modo criação, o `status` inicial ao salvar é sempre `rascunho`. No modo edição, preservar o `status` atual do PRD — transições entre `pronto`, `em-progresso` e `concluido` são feitas por skills futuras de planejamento e execução

### 4. Mapeamento de Dependências

Antes de apresentar o PRD para revisão final:

1. Listar os arquivos existentes em `./docs/prds/` (ou no caminho informado pelo usuário)
2. Para cada PRD existente, avaliar se a feature atual depende de algo já especificado nele — depende quer dizer que a implementação desta feature pressupõe comportamento, entidade, interface ou regra descritos no outro PRD
3. Preencher o campo `depends_on` no frontmatter com a lista dos `prd_number` identificados (ex: `depends_on: ["001", "003"]`)
4. Registrar no "Registro de Decisões" o critério usado para definir cada dependência — evita reconstruir o raciocínio no futuro

Regras:
- Dependência deve ser real e específica — não listar todo PRD "relacionado" ou "do mesmo domínio"
- Se não houver dependências, manter `depends_on: []`
- O carregamento dos PRDs dependentes é sob demanda (progressive disclosure) — não incluir o conteúdo deles no PRD atual

### 5. Refinamento Pontual

Aplicar as correções solicitadas pelo usuário no draft — premissas corrigidas, escopo ajustado, regras refinadas. Repetir até aprovação.

Se a revisão mudar o escopo da feature, reavaliar `depends_on` antes de salvar — uma feature que ganha ou perde responsabilidades pode ganhar ou perder dependências.

### 6. Salvar Arquivo

**No modo criação**, salvar o PRD novo:

1. **Determinar o próximo número**: listar os arquivos existentes em `./docs/prds/` e identificar o maior número usado (formato `NNN`). O próximo PRD recebe o número sequencial seguinte. Se não existir nenhum PRD, começar com `001`.
2. **Nomear o arquivo**: `NNN-[nome-em-kebab-case].md` (ex: `003-autenticacao-oauth.md`)
3. **Local padrão**: `./docs/prds/`
4. Se o usuário especificou outro caminho, usar o caminho informado
5. Criar o diretório se não existir
6. Preencher o campo `prd_number` no frontmatter com o número atribuído (ex: `003`)

**No modo edição**, sobrescrever o arquivo original preservando `prd_number`, nome do arquivo, `status` atual e IDs de US e Milestone já atribuídos. Novas USs recebem o próximo ID sequencial disponível.

### 7. Continuidade Multi-PRD

Após salvar, verificar se havia um split proposto no passo 2a com PRDs pendentes.

Se sim:
```
PRD-A salvo. Continua com PRD-B: [nome da feature B]?
```

Ao confirmar, iniciar o ciclo para o próximo PRD — aproveitando as decisões do PRD anterior como contexto para inferências mais precisas (mesma stack, mesmo sistema, mesmos padrões detectados).

Repetir até que todos os PRDs do split estejam salvos ou o usuário interrompa.
