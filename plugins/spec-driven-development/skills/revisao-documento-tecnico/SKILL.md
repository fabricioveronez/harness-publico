---
name: revisao-documento-tecnico
description: >
  Revisa documentos técnicos (PRDs, specs, RFCs, TRDs, planos de implementação, TASKS)
  antes da implementação para identificar inconsistências, definições em aberto, conflitos
  entre seções e imprecisões técnicas. Investiga o código existente, dependências e outros
  documentos do projeto para validar se o que o documento descreve é viável e coerente com
  o estado atual do sistema — e resolve por inferência o que a evidência permitir, em vez
  de devolver toda decisão ao usuário. Use esta skill sempre que o usuário pedir para
  revisar, analisar ou validar um documento técnico — mesmo que não use o termo "revisão".
  Também quando mencionar "verificar PRD", "analisar spec", "revisar o plano", "validar
  as tasks", "revisar TRD", "tem alguma coisa faltando", "está pronto para implementar?",
  "revisar antes de codar", "validar documento", "checar inconsistências", ".aidev",
  ou qualquer variação que indique avaliação de qualidade de um documento técnico
  antes de iniciar a implementação.
---

# Revisão de Documento Técnico

Skill para revisão crítica de documentos técnicos com foco em identificar — e, quando a
evidência permitir, **resolver** — tudo que precisa estar fechado antes da implementação.
Vale para qualquer documento técnico: PRD, spec, RFC, TRD, PLAN.md, TASKS.md ou formatos
que ainda não existem. O processo é genérico; a forma da avaliação emerge do documento.

## Quando usar

- Antes de implementar uma feature baseada em um documento técnico
- Quando o usuário quer validar se um PRD/spec/plano está completo
- Quando o usuário pergunta se há algo faltando ou inconsistente em um documento
- Antes de executar um PLAN/TASKS gerado a partir de um PRD

## Filosofia

O objetivo não é concordar com o documento — é ser crítico e encontrar problemas antes
que eles se tornem bugs ou retrabalho. Um documento técnico "aprovado" com definições
vagas gera implementações que precisam de refatoração.

A revisão não acontece no vácuo. Um documento pode parecer perfeito isoladamente mas
estar desalinhado com o que já existe no código, com o que outros documentos prometem,
ou com como as tecnologias referenciadas realmente funcionam. Por isso a investigação
do contexto real (código, docs, dependências) é parte essencial da revisão.

E a investigação não serve só para *encontrar* problemas — serve para **resolvê-los**.
O revisor é um assistente, não um entrevistador: quando o contexto investigado contém a
resposta para uma pendência ou ambiguidade, a postura correta é propor essa resposta com
a fonte citada, não devolver a pergunta ao usuário. O usuário decide apenas onde a
decisão é genuinamente dele (ver "Fronteiras de decisão"). Perguntar o que a evidência
já responde desperdiça o tempo do usuário; inventar o que a evidência não cobre cria
requisito falso. A régua entre os dois é sempre a mesma: **evidência citável**.

## Processo de revisão

### Passo 1: Leitura e compreensão

Leia o documento completo antes de emitir qualquer análise. Entenda:
- Que tipo de documento é e qual problema ele resolve
- Qual a proposta central (arquitetura, fluxo, escopo)
- Quais as dependências com outros documentos/sistemas

### Passo 2: Investigação do contexto real

Antes de analisar o documento em si, investigue o estado atual do projeto para ter
uma base de comparação sólida. Isso evita apontar problemas fictícios ou ignorar
problemas reais — e é o que alimenta a resolução por inferência mais adiante.

#### 2a — Documentos relacionados

- Leia os documentos referenciados pelo documento revisado (frontmatter `depends_on`,
  `references`, links no corpo)
- Busque outros documentos no projeto que mencionem o mesmo componente ou feature
  (usar Grep/Glob em `docs/`, `.aidev/` e similares)
- Para cada dependência, identifique: o que esse documento espera receber? O que
  o outro documento promete entregar? As interfaces batem?

#### 2b — Código existente

- Verifique se já existe código implementado para o que o documento descreve
  (buscar por nomes de classes, funções, endpoints, variáveis de ambiente mencionados)
- Se existir código, compare: o documento reflete o que já foi implementado ou
  contradiz? Há funcionalidades no código que o documento ignora?
- Verifique se as dependências/bibliotecas mencionadas existem no projeto
  (requirements.txt, pyproject.toml, package.json, go.mod, etc.)

#### 2c — Tecnologias referenciadas (validação obrigatória)

- Para APIs, SDKs ou ferramentas externas mencionadas no documento, valide se
  os campos, métodos ou comportamentos descritos são reais e corretos
- Não confiar apenas no próprio conhecimento — documentações mudam e informações
  podem estar desatualizadas ou incorretas. Um campo que "parece existir" pode
  ter sido removido, renomeado, ou nunca ter existido como descrito.
- Usar ferramentas externas para validar afirmações técnicas:
  - **MCPs de documentação** (context7, docs-langchain) para consultar docs de
    bibliotecas e frameworks diretamente
  - **WebSearch** para validar contra documentação oficial, issues conhecidas e
    comportamentos reais em produção
- Verificar também limitações e edge cases das tecnologias que o documento não
  menciona mas que impactam a implementação (ex: campos que podem ser nulos em
  cenários reais mesmo sendo "obrigatórios" na spec)

### Passo 3: Esqueleto de avaliação

Com o documento lido e o contexto investigado, construa o **esqueleto de avaliação**
deste documento específico. A estrutura da revisão não vem de um formulário fixo —
emerge do documento. O que é fixo são as **perguntas estruturantes**, que devem sempre
ser respondidas; a forma da resposta é livre:

1. **Qual é o upstream deste documento?** A fonte de verdade contra a qual ele se mede
   (um PLAN se mede contra o PRD; um TRD contra o código/stack real; uma spec contra o
   sistema que descreve). É contra o upstream que a coerência será avaliada.
2. **Quais invariantes ele carrega?** Propriedades que nenhuma correção pode violar
   (ex: TASKS.md não perde marcações `[X]` nem renumera IDs de task).
3. **Quem é o dono da edição?** Se existe uma skill dona do artefato, correções serão
   delegadas a ela; se não existe, o revisor edita diretamente (ver Pós-revisão).
4. **Quais modos de falha importam para este documento?** Selecionar do repertório
   abaixo o que se aplica e adicionar dimensões específicas que o repertório não prevê
   (ex: para um TASKS.md, a integridade do grafo de `needs:` — dependências circulares
   ou apontando para tasks inexistentes).

Exemplos ilustrativos de respostas que costumam emergir — **não prescrever**, o
esqueleto é consequência do documento, não forma que o documento preenche:

| Tipo | Upstream típico | Invariantes típicos | Dono típico da edição |
|---|---|---|---|
| PRD | intenção do usuário, TRD | Registro de Decisões | `escrever-prd` |
| PLAN/TASKS | PRD | IDs de task, marcações `[X]` | `criar-plan` (reconciliação) |
| TRD | código/stack real | — | `escrever-trd` |
| spec/RFC avulsa | sistema que descreve | — | revisor edita direto |

Apresente o esqueleto em 3–5 linhas no início da saída ("avaliando este documento como
X, upstream Y, dimensões A/B/C") — é um checkpoint barato para o usuário corrigir a
lente antes da revisão profunda, sem virar cerimônia de aprovação.

#### Repertório de modos de falha

Catálogo de onde documentos técnicos costumam falhar. O esqueleto seleciona o que se
aplica — não é checklist obrigatório, e o documento pode exigir dimensões que não
estão aqui.

**Definições explicitamente em aberto**
- Termos como "inferido", "validar", "a definir", "TBD", "TODO", "pendente"
- Campos vazios no frontmatter, checkboxes que contradizem o status do documento

**Inconsistências internas**
- Valores que aparecem em mais de um lugar com números diferentes
- Edge cases que se contradizem entre seções
- Funcionalidades na visão geral mas ausentes do detalhamento, ou vice-versa
- Etapas/milestones que não cobrem tudo que o documento descreve

**Coerência com upstream e derivados**
- O documento desvia da sua fonte de verdade? (PLAN que ignora requisito do PRD,
  TRD que descreve stack que o código não usa)
- Há requisito órfão (no upstream sem reflexo aqui) ou item fantasma (aqui sem
  origem no upstream)?
- Derivados deste documento ficaram defasados depois de uma mudança nele (drift)?
- O documento descreve algo que o código já implementa de forma diferente?
- **Contratos de interface entre componentes**: quando um documento menciona entregar
  dados a outro componente (handler, pipeline, API, fila), verificar se o contrato da
  interface está definido — quais campos, tipos e formatos são garantidos. Suposições
  implícitas do consumidor precisam estar formalizadas no produtor.

**Ambiguidades e imprecisões técnicas**
- Campos/APIs mencionados sem especificar versão ou precedência
- Interfaces entre componentes não especificadas ("entregar ao pipeline" sem mecanismo)
- Termos genéricos com múltiplas interpretações possíveis na implementação
- Nomes genéricos de variáveis de ambiente, endpoints, classes ou tabelas que podem
  colidir (ex: `INTERVAL` é genérico demais — preferir `EVENT_COLLECTION_INTERVAL_MINUTES`)

**Riscos e mitigações**
- Mitigações que não resolvem o risco real
- Riscos com impacto incorreto (subestimado ou superestimado)
- Riscos não documentados que são óbvios pela proposta técnica
- Mitigações descartadas que já são suportadas nativamente pelas tecnologias
  referenciadas (paginação nativa, retry do SDK) — se o custo é um parâmetro na
  chamada, o adiamento não se justifica

### Passo 4: Revisão e resolução por inferência

Percorra o esqueleto. Para **cada achado**, antes de reportá-lo, tente resolvê-lo com
o contexto investigado no Passo 2:

- Se a resposta existe no código, em outro documento, numa convenção observada do
  projeto ou na documentação oficial da tecnologia → formule a **recomendação única**
  com a fonte citada (`arquivo:linha`, documento, URL). Alternativas viáveis entram
  apenas como veto ("alternativa Y se [condição]"), não como menu de opções.
- Se não há evidência citável → o achado vai para a zona do usuário, mas ainda assim
  formulado como proposta: "recomendo X por [razão], confirma?" em vez de pergunta
  aberta. O usuário decide melhor sobre uma proposta concreta do que sobre uma
  pergunta em branco.

#### Fronteiras de decisão

**Zona de autonomia** — o revisor recomenda e aplica em lote (com direito a veto):
- Achados com evidência rastreável e citável no repo, nos docs ou na documentação
  oficial da tecnologia
- Imprecisões técnicas com resposta objetiva (campo de API inexistente, nome genérico,
  mitigação já nativa do SDK)

**Zona do usuário** — o revisor recomenda mas só aplica com confirmação individual:
- Decisão de produto sem rastro — escopo, prioridade, comportamento visível ao usuário
  final sem precedente no projeto
- Contradição com decisão já registrada (ex: Registro de Decisões) — algo decidido e
  documentado só muda com aval humano, mesmo diante de evidência nova
- Contratos de interface com outros componentes — o raio de impacto vai além do
  documento revisado
- Qualquer achado **Bloqueante** — criticidade máxima nunca se auto-resolve em lote
- Correções que alteram o **upstream** do documento revisado (ex: achado no PLAN que
  exige mudar o PRD) — mudar a fonte de verdade é sempre decisão humana

### Passo 5: Classificação e apresentação

Apresente os achados organizados por criticidade.

**Níveis de criticidade:**
- **Bloqueante**: invalida a implementação ou causa comportamento incorreto garantido
- **Alto**: risco de retrabalho significativo na integração ou perda silenciosa de dados
- **Médio**: pode causar problemas em produção sob certas condições
- **Baixo**: melhoria de qualidade sem impacto funcional imediato

**Formato de saída:**

Primeiro o esqueleto em resumo (Passo 3), depois todos os achados em uma única tabela,
ordenados por criticidade. Cada achado ocupa uma linha autocontida: quem lê apenas ela
entende o problema, sabe onde está no documento, vê a recomendação com a fonte e sabe
se o item se resolve em lote ou aguarda sua decisão.

```
## Achados da revisão

| # | Linha | Achado | Criticidade | Recomendação | Resolução |
|---|-------|--------|-------------|--------------|-----------|
| 1 | 79 | Mecanismo de disparo da notificação não definido no PRD 003 | Bloqueante | Pipeline do PRD 002 chama função de notificação ao final da persistência — é o padrão já usado em `pipeline/persist.ts:88` | **Sua decisão** |
| 2 | 81 | Bot Discord sem justificativa — webhook é mais simples para one-way | Alto | Trocar para webhook (`DISCORD_WEBHOOK_URL`), conforme docs oficiais do Discord para notificações sem interação | Auto |
```

A tabela é o único formato de apresentação dos achados — não listar os mesmos pontos
em seções separadas antes dela.

**Após a tabela**, ofereça a aplicação: "Itens **Auto** aplico em lote — vete os que
discordar. Itens **Sua decisão** aguardam confirmação individual." O lote não espera
as pendências da zona do usuário: pendência de produto não trava correção técnica
evidenciada.

### Diretrizes de apresentação

- Sempre referencie a linha do documento onde o problema aparece
- Toda recomendação inferida cita a fonte — recomendação sem fonte é opinião, e
  opinião pertence à zona do usuário
- Quando identificar inconsistência com código ou outro doc, mostre a evidência
  (nome do arquivo, linha, trecho relevante)
- Separe fatos de opiniões — "O PRD diz X, mas o código em Y faz Z" (fato)
  vs "Recomendo alinhar para X porque..." (opinião com justificativa)
- Não invente problemas — se o documento está claro e consistente, não force crítica
- Seja crítico mas construtivo — o objetivo é melhorar o documento, não destruí-lo

## Pós-revisão: aplicação de correções

Após o usuário aprovar o lote (ou vetar itens) e confirmar os itens da zona do usuário,
aplique as correções **respeitando o dono de cada artefato** (identificado no Passo 3):

- **Existe skill dona** (`escrever-prd`, `criar-plan`, `escrever-trd`): corrigir via
  ela. Em cadeias derivadas (PRD → PLAN/TASKS), corrigir o upstream e propagar pela
  reconciliação da skill dona — ela já protege os invariantes (IDs, `[X]`). Não
  reimplementar essas regras aqui.
- **Problema exclusivo do artefato derivado** (ex: `needs:` quebrado no TASKS.md, que
  não decorre do PRD): editar diretamente, preservando os invariantes do esqueleto.
- **Sem dono** (spec avulsa, RFC): editar diretamente.

Ao editar diretamente:
- Atualizar **todas** as seções impactadas — uma mudança cascateia pelo documento
  inteiro (visão geral, regras, edge cases, critérios de aceite, milestones). Não
  corrigir apenas o ponto onde o problema foi detectado.
- Registrar novas decisões na seção de decisões do documento (quando existir) com a
  data atual e o motivo
- Adicionar critérios de aceite quando a correção introduzir comportamento novo
- Adicionar tasks quando a correção introduzir trabalho de implementação novo

## O que NÃO fazer

- Não sugira mudanças de formatação ou estilo — foco é conteúdo técnico
- Não aplique nada antes de apresentar a tabela e receber o aval do lote — a
  autonomia começa depois do checkpoint, não antes
- Não infira sem fonte citável — inferência sem evidência é invenção de requisito,
  pior que perguntar
- Não devolva pergunta aberta quando a evidência responde — resolver com fonte é o
  papel do revisor; entrevistar o usuário sobre o que o repo já diz é desperdício
- Não assuma que silêncio é erro — se algo não está no documento e não precisa estar,
  não reclame
- Não repita informações do documento de volta como "resumo" — vá direto aos problemas
- Não opine sobre decisões já tomadas e registradas — foque no que ainda está indefinido
