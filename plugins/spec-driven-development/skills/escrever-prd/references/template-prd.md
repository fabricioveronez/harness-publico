# Template PRD

Estrutura padrão do PRD de feature gerado pela skill. O PRD é o **documento de negócio** da feature — cobre comportamento e regra de negócio. Detalhe técnico (stack, arquitetura, NFR global, realização) **não** mora aqui: vive no TRD (`docs/trd.md`), nos ADRs (`docs/adrs/`) e no PLAN (`./.aidev/`). Aplicável a qualquer tipo de projeto de software.

## Fronteira: o que é negócio e o que não é

A régua para decidir se algo entra no PRD tem dois eixos:

1. **Escopo** — específico desta feature (candidato a PRD) vs. global/transversal (TRD).
2. **Natureza** — o *requisito/intenção* (o quê, com que limiar, por qual razão de negócio) vs. a *realização técnica* (como construir ou sustentar).

> **PRD = requisito + razão, no escopo da feature. TRD/ADR/PLAN = realização técnica + constraint global.**

Aplicando:

| Conteúdo | Onde mora |
|---|---|
| Comportamento, regra de negócio, edge case | PRD |
| "Como de produto" (forma da solução em termos de comportamento) | PRD |
| Limiar de feature com razão de negócio (ex.: "resposta < 2s, senão duplica cobrança") | PRD (§5a) |
| Métrica de sucesso (baseline → meta) | PRD (§5b) |
| "Como técnico" (JWT, Redis, event-driven, modelo de dados) | PLAN |
| Decisão arquitetural durável (imutável) | ADR (`docs/adrs/`) |
| NFR global (p95 geral, uptime, criptografia) | TRD |
| Decomposição em tarefas | PLAN/TASKS |
| Dimensionamento/rastreio do artefato técnico (bundle, fatia, verticalização) | PLAN/TASKS — o PRD referencia, mas não dirige |

## Semântica dos campos de controle

**`status`** — ciclo de vida da feature:

- `rascunho` — em criação ou revisão, ainda não aprovado
- `pronto` — aprovado, aguardando planejamento/execução
- `em-progresso` — execução ativa (transição feita pela skill de planejamento/execução)
- `concluido` — feature entregue; **o PRD congela e vira registro histórico imutável**. Alcançado quando **todos os milestones têm o checklist de aceite aprovado**. A transição em si é feita por quem aprova/executa, **não por esta skill** (que não faz transição de estado)

Quando um PRD chega em `concluido`, ele não é mais editado. Mudanças de comportamento posteriores abrem um novo PRD que pode referenciar o original via `depends_on`.

**`depends_on`** — grafo de rastreabilidade entre PRDs:

- Lista os `prd_number` das features das quais esta depende diretamente
- Carregamento é sob demanda (progressive disclosure) — o agente só lê um PRD dependente quando o contexto da implementação exigir aquele conhecimento específico
- Deve ser mapeado durante a criação do PRD e reavaliado sempre que o escopo mudar em revisão
- Só listar dependências reais — não incluir PRDs apenas "relacionados" ou "do mesmo domínio"

---

```markdown
---
prd_number: "NNN"
status: rascunho | pronto | em-progresso | concluido
priority: baixa | média | alta | crítica
created: YYYY-MM-DD
issue: "#número (opcional)"
depends_on: [] # lista de PRDs dos quais esta feature depende
references: [] # links para docs, issues, ADRs, PRDs relacionados, recursos externos
---

# PRD NNN: [Título descritivo da feature]

## 1. Contexto

[Descrição de negócio que situa a feature. O foco é o problema e o estado atual
do ponto de vista do produto/usuário — não o detalhe de stack. Incluir:]

- **Produto/área**: [em qual produto ou área de negócio esta feature se insere]
- **Estado atual**: [o que o usuário consegue ou não fazer hoje, como o fluxo funciona hoje]
- **Problema**: [qual dor esta feature resolve, quem é afetado, qual o impacto de não resolver]

> **Contexto técnico** (stack, arquitetura, padrões) vive no TRD (`docs/trd.md`),
> carregado automaticamente na implementação. Aqui basta um ponteiro quando relevante —
> não duplicar stack no PRD.

## 2. Solução Proposta

### Visão de produto

[3-5 bullets descrevendo a abordagem em termos de **comportamento e valor** —
o "como de produto", não a arquitetura. Ex.: "resolver abandono de checkout com
pagamento 1-clique e cartão salvo", não "via PaymentIntents + lock no Redis".]

### Decisões de produto

1. [Decisão de produto com justificativa curta — ex.: "convite expira em 7 dias"]
2. [Decisão de produto com justificativa curta]

> Decisão **arquitetural** (durável, técnica) não entra aqui — registre como ADR
> (`docs/adrs/`) via `escrever-trd` Modo Decision e referencie em §8 se relevante.

### Fora do escopo

- [O que NÃO será feito e por quê]
- [O que NÃO será feito e por quê]

## 3. Funcionalidades

### US01: [Título objetivo]

Como [persona], quero [ação], para [benefício].

**Rules:**
- [Regra de negócio ou comportamento esperado]
- [Limite, restrição ou condição]

**Edge cases:**
- [Situação anômala] → [comportamento esperado]
- [Situação anômala] → [comportamento esperado]

### US02: [Título objetivo]

Como [persona], quero [ação], para [benefício].

**Rules:**
- [Regra de negócio ou comportamento esperado]

**Edge cases:**
- [Situação anômala] → [comportamento esperado]

[Repetir para cada funcionalidade identificada. Cada US deve ter pelo menos uma
Rule e um Edge case. Detalhe técnico de implementação não entra na US — vai no PLAN.]

## 4. Fluxo de Negócio

[Diagrama de **jornada ou processo de negócio** — os pontos de decisão são regras
de negócio, não componentes de software. Útil quando a feature tem ramificação de
regra que o texto dos Edge cases não deixa clara.]

```
Reembolso solicitado
   │
   ▼
Pedido tem < 7 dias?
   ├── sim ──▶ Reembolso automático ──▶ Notifica usuário
   └── não ──▶ Fila de aprovação manual ──▶ Aprovado? ──┬── sim ──▶ Reembolso
                                                        └── não ──▶ Nega + justifica
```

[Seção opcional. Topologia técnica (componentes/serviços, modelo de dados) **não**
entra aqui — fica no "Diagrama de Implementação" do PLAN.]

## 5. Critérios de Aceite

### 5a. Critérios de aceite da feature

Critérios **funcionais e não-funcionais específicos desta feature**, cada um como
limiar observável. NFR específico da feature (tempo de resposta, disponibilidade,
capacidade) entra aqui quando tem razão de negócio — registre o limiar **e o porquê**.
NFR global do projeto (p95 geral, uptime, criptografia) mora no TRD, não aqui.

| Critério | Razão de negócio | Como verificar (observável) |
|----------|------------------|-----------------------------|
| [ex.: confirmação de pagamento responde < 2s] | [acima disso o usuário reenvia e duplica a cobrança] | [como testar de fora] |
| [ex.: fluxo X funciona para persona Y] | — | [como testar] |

### 5b. Métricas de sucesso

| Métrica | Baseline (fonte) | Meta | Prazo | Mín. aceitável | Responsável |
|---------|-------------------|------|-------|-----------------|-------------|
| [nome] | [valor atual + de onde vem o dado] | [valor alvo] | [data ou período] | [threshold abaixo do qual a entrega falhou] | [quem mede] |

**Regras:**
- Baseline sem fonte confiável deve ser marcado como "A levantar" com responsável e prazo para obtenção
- Mín. aceitável define o ponto de corte entre sucesso e fracasso — sem ele, a meta é aspiracional, não um critério de aceite

## 6. Milestones

### Milestone 1: [Verbo + Substantivo]

**Por que é um marco:** [o que o usuário ganha; por que se anuncia como conquista.]

**Funcionalidades:** US01, US02

**Checklist de aceite** (marcado pelo Aprovador após a implementação):
- [ ] [critério observável de §5a, filtrado pelas USs deste marco]
- [ ] [critério observável de §5a, filtrado pelas USs deste marco]

**Aprovador:** [quem dá o OK — papel ou pessoa]

### Milestone 2: [Verbo + Substantivo]

**Por que é um marco:** [uma frase.]

**Funcionalidades:** US03

**Checklist de aceite** (marcado pelo Aprovador após a implementação):
- [ ] [critério observável de §5a, filtrado pelas USs deste marco]

**Aprovador:** [quem dá o OK — papel ou pessoa]

[Um milestone é um **marco de produto**: um conjunto coeso de funcionalidades que entrega
algo ao usuário — algo que se anuncia como conquista, não uma fatia de execução. Definido por
**quais USs cobre**, por uma **justificativa de por que é um marco** (auto-avaliação: se sai
forçada, é tarefa disfarçada ou dois marcos espremidos) e por um **checklist de aceite**
(critérios de §5a filtrados pelas USs, marcáveis pelo Aprovador). **Sem número mínimo**; o teto
de ~6 é sinal de que talvez sejam várias features (ver §2a). A decomposição em tarefas técnicas
(passos, validação, ordem de execução) e o dimensionamento do artefato de execução são do
PLAN/TASKS, gerados por `preparar-execucao` — não detalhar nem dirigir isso aqui.]

## 7. Riscos e Dependências

| Risco | Impacto | Mitigação | Status |
|-------|---------|-----------|--------|
| [risco de negócio, produto ou adoção] | Alto/Médio/Baixo | [plano de mitigação] | Pendente/Monitorando/Mitigado |

**Dependências:**

| Dependência | Tipo | Status | Impacto se bloqueado |
|-------------|------|--------|----------------------|
| [outra feature/PRD, equipe, decisão de produto] | Interna/Externa | [estado atual] | [quais milestones são afetados] |

[Dependência técnica de infra/serviço com SLA ou rate limit é contexto técnico
global → TRD. Aqui ficam dependências no nível de negócio/entrega.]

## 8. Referências

- [Descrição do recurso](link) — [por que é relevante]
- [Descrição do recurso](link) — [por que é relevante]

[Links para documentação, issues, PRDs relacionados, ADRs que embasam a feature,
designs, ou qualquer recurso externo relevante para o negócio da feature.]

## 9. Registro de Decisões

- **[YYYY-MM-DD]:** [Decisão de produto tomada]. Motivo: [por que essa escolha foi feita].

[Registra decisões **de produto** e premissas de negócio significativas. Decisão
técnica/arquitetural vai para ADR, não aqui. Seção viva durante `rascunho`, `pronto`
e `em-progresso`; congela junto com o PRD quando o status vira `concluido`.]
```
