# escrever-trd

Cria e mantém o **TRD** (Technical Requirements Document) em `docs/trd.md` — o documento
técnico global do projeto: arquivo único, versionado, que captura stack, arquitetura,
requisitos não-funcionais, dependências externas, padrões e decisões globais. É o contexto
técnico carregado automaticamente por `preparar-execucao` e `implementar-task`; sem ele, essas
skills operam às cegas e podem gerar planos ou implementações que divergem da realidade.

A granularidade é deliberadamente baixa: o TRD cobre o que é **global e estável**. Requisito de
uma feature fica no PRD; decisão técnica durável vira **ADR**, criado por esta mesma skill no
**Modo Decision** (`docs/adrs/NNN-slug.md`), que também atualiza a seção Decisões Globais do TRD.

A skill analisa o projeto automaticamente, enriquece com busca externa e só entrevista o usuário
sobre o que sobrou — o objetivo é minimizar atrito e maximizar o que se deduz sem perguntar.

## Pré-requisitos e configuração

- **Nenhuma configuração.** Os três modos são detectados sozinhos: **Criação** quando
  `docs/trd.md` não existe, **Edição** quando existe, e **Decision** por intenção explícita
  ("registra a decisão de…", "cria um ADR", "decidimos trocar X por Y") — que sobrepõe a
  detecção automática e independe de o TRD existir.
- Um projeto de código para analisar. Quanto mais o projeto revelar (`package.json`,
  `pyproject.toml`, `go.mod`, `.env.example`, `docker-compose.yml`, `terraform/`, configs de
  lint e teste), menor a entrevista.
- `docs/` e `docs/adrs/` são criados se não existirem. Outro caminho para os ADRs pode ser
  informado pelo usuário.

### Estrutura do TRD gerado

Segue `references/template-trd.md`, com 6 seções:

| Seção | Conteúdo |
|---|---|
| **Stack** | Linguagem, runtime, framework, banco, ferramentas de build e pacotes |
| **Arquitetura** | Padrão arquitetural, estrutura de pastas, módulos principais |
| **Requisitos Não-Funcionais** | Performance, disponibilidade/SLA, escalabilidade, segurança, observabilidade — com valores mensuráveis |
| **Dependências Externas** | APIs de terceiros, serviços de infraestrutura e sistemas internos com SLA, rate limit ou contrato relevante |
| **Padrões** | Testes (framework + comando), estilo de código, error handling, logging, auth |
| **Decisões Globais** | Referências progressivas aos ADRs (título, data, status, link) |

## Dependências externas

- **WebSearch** (opcional) — enriquecer as dependências externas detectadas com constraints
  públicos: rate limits, SLAs, timeouts, quotas, comportamentos padrão.
- **MCPs de documentação** (opcional) — `context7` para bibliotecas e frameworks, ou MCPs
  específicos de serviços. Havendo mais de uma opção para o mesmo serviço, a skill prefere a
  mais especializada (MCP do serviço > WebSearch genérica).

Nenhuma é obrigatória, mas sem elas o enriquecimento não acontece e a **entrevista fica maior**
— cada constraint não encontrado vira pergunta. Sistemas **internos** nunca são buscados: essa
informação vem só do usuário. Todo resultado de busca entra como **sugestão pré-preenchida com a
fonte** (`[WebSearch]`, `[context7]`…), validada pelo usuário no preview — nunca como fato.

## Skills relacionadas

- **preparar-execucao** — consome `docs/trd.md` como contexto técnico global; sem ele, entra em
  mini-modo de coleta (entrevista curta sobre stack, convenções e comando de teste).
- **implementar-task** — consome `docs/trd.md` quando referenciado pelo `PLAN.md`.
- **escrever-prd** — documenta a feature, não o projeto. Quando um input de PRD traz uma decisão
  arquitetural durável, ela é roteada para o **Modo Decision** desta skill.
- **revisao-documento-tecnico** — revisa o TRD; esta skill é o "dono da edição" para onde as
  correções voltam.
- **orquestrar-execucao** — indireta: cada `implementar-task` disparado em paralelo carrega o
  mesmo TRD como contexto.

### Posição no fluxo spec-driven

O TRD **não é um passo sequencial** do fluxo — é um artefato **global**, escrito uma vez e
mantido, que alimenta as demais skills sob demanda:

```
escrever-prd (opcional) → preparar-execucao ─┬─ 1 fatia ──→ implementar-task ──→ validar-implementacao
                                             └─ 2+ fatias → orquestrar-execucao ┘
                                     ▲
                            docs/trd.md + docs/adrs/
                            (carregados como contexto por
                             preparar-execucao e implementar-task)
```

## Exemplos de uso

```
Cria o TRD desse projeto

Documenta a stack e os padrões do projeto

O TRD está desatualizado — a stack mudou

Atualiza o TRD, adicionamos o Redis

Registra a decisão de usar Postgres em vez de Mongo

Cria um ADR para a estratégia de autenticação

Decidimos trocar o REST por gRPC — registra isso
```

### Como funciona (resumo)

**Criação** — 5 passos antes de gravar qualquer arquivo:

1. **Análise automática** — lê arquivos do projeto para inferir stack, arquitetura, padrões e
   dependências sem perguntar.
2. **Enriquecimento por busca externa** — busca os constraints públicos de cada dependência
   externa identificada; o resultado vira sugestão com fonte.
3. **Mini-entrevista** — só o que não foi inferido nem enriquecido: **≤5 perguntas** (máximo
   aceitável: 8), agrupadas de 2 em 2. Precisar de mais é sinal de que a análise falhou, não o
   usuário.
4. **Varredura de ADRs** — escaneia `docs/adrs/` e lista referências progressivas (ADR
   `obsoleto` aparece como `~~título~~`, nunca é removido).
5. **Preview e gravação** — exibe as 6 seções para confirmação antes de gravar.

**Edição** — relê o TRD, re-analisa o projeto e classifica as divergências (mudança não
refletida / entrada que não se verifica mais / área ambígua / seção ausente). A entrevista é
focada **só no delta**: para cada divergência, atualizar, manter ou ignorar. Sem divergência, a
skill informa que está sincronizado e encerra sem editar.

**Decision** — fluxo próprio e mais curto: numera o ADR, gera draft-first a partir de
`references/template-adr.md` com as premissas marcadas, trata supersedência (ADR novo com
`supersedes`, antigo vira `obsoleto`), grava e atualiza a seção Decisões Globais do TRD.

### O que é ADR (e o que não é)

Só decisão **durável, de blast radius amplo e cara de reverter** vira ADR: escolha de banco,
estratégia de auth, padrão arquitetural, biblioteca estruturante, convenção de API. Decisão
**local a uma feature e efêmera** (qual util reusar, como fiar um endpoint) **não é ADR** — mora
na "Abordagem Técnica" do `PLAN.md`, gerado pelo `preparar-execucao`. Pedido de decisão local é
avisado e redirecionado para lá.

## Limitações conhecidas

- **ADR `aceito` é imutável** — exceto o campo `status`, quando outro ADR o supersede. Revisar
  uma decisão nunca é editar o ADR: é criar um novo com `supersedes` apontando para o antigo.
  Mesma disciplina da imutabilidade do PRD `concluido`.
- **Não cria ADR fora do Modo Decision** — nos modos Criação e Edição apenas **referencia** os
  ADRs já existentes em `docs/adrs/`.
- **Não cria PRDs** (papel de `escrever-prd`) nem gera `PLAN`/`TASKS` (papel de
  `preparar-execucao`).
- **Não toma decisão de negócio** — lacuna é devolvida ao usuário.
- **Cancelar o preview não tem efeito colateral** — nada é gravado e o TRD original permanece
  intacto. Perder o TRD anterior seria pior do que refazer a entrevista.
- **TRD vazio ou corrompido** (sem seções reconhecíveis) é tratado como modo criação, com aviso
  ao usuário.
- **Referências a ADRs são preservadas por padrão** — nunca removidas sem confirmação
  explícita. ADR referenciado e não encontrado vira `*(arquivo não encontrado)*` com pergunta.
- **NFRs raramente são inferíveis** — quase sempre viram pergunta da entrevista, porque não
  costumam estar em arquivo nenhum.

### Referências da skill

- `references/template-trd.md` — estrutura canônica do TRD (6 seções).
- `references/template-adr.md` — estrutura canônica do ADR gerado no Modo Decision.
