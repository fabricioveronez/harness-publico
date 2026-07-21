# revisao-documento-tecnico

Revisa documentos técnicos antes da implementação para identificar inconsistências, definições
em aberto, conflitos entre seções e imprecisões técnicas — e, quando a evidência permitir,
**resolvê-las** em vez de devolver toda decisão ao usuário. Vale para qualquer documento
técnico: PRD, spec, RFC, TRD, `PLAN.md`, `TASKS.md` ou bundles `.aidev/`; o processo é
genérico e a forma da avaliação emerge do documento revisado.

A skill investiga o contexto real (código existente, documentos relacionados, dependências e a
documentação oficial das tecnologias citadas) antes de analisar o documento. Essa investigação
não serve só para *encontrar* problemas: cada achado é resolvido com **evidência citável**
(`arquivo:linha`, documento, URL) e vira uma recomendação única. A régua é sempre a mesma —
perguntar o que a evidência já responde desperdiça o tempo do usuário; inferir o que a
evidência não cobre inventa requisito.

Os achados saem em **uma única tabela**, ordenada por criticidade (Bloqueante, Alto, Médio,
Baixo), com uma coluna `Resolução` que separa o que a skill aplica em lote (`Auto`) do que
aguarda o usuário (`Sua decisão`).

## Pré-requisitos e configuração

- Um documento técnico disponível no projeto ou fornecido pelo usuário.
- Acesso ao código-fonte do projeto — é ele que dá a evidência para a resolução por inferência.
  Quanto mais código, docs relacionados e dependências existirem, mais precisos os achados.

## Dependências externas

- **MCP context7** (opcional) — validar APIs e SDKs de bibliotecas/frameworks.
- **MCP docs-langchain** (opcional) — validar docs de LangChain.
- **WebSearch** (opcional) — validar contra documentação oficial, issues conhecidas e
  comportamento real em produção.

Nenhuma é obrigatória — a revisão funciona com o conhecimento do próprio modelo, mas a validação
de tecnologias externas é declaradamente obrigatória no processo (Passo 2c): sem MCP ou
WebSearch, o modelo indica a incerteza no achado em vez de afirmar.

## Skills relacionadas

Correções são aplicadas **pelo dono de cada artefato**, identificado durante a revisão:

- **escrever-prd** — dona do PRD. Revisão é o passo natural depois de escrever o PRD e antes de
  preparar a execução.
- **preparar-execucao** — dona do `SPEC.md`, `PLAN.md` e `TASKS.md`. Correção em cadeia derivada
  (PRD → SPEC → PLAN/TASKS) é aplicada no upstream e propagada pela reconciliação dela, que já
  protege os invariantes (IDs de task, marcações `[X]`).
- **escrever-trd** — dona do TRD e dos ADRs.
- **brainstorm** — madurar a ideia antes de formalizar o documento e rodar a revisão.

Documento **sem skill dona** (spec avulsa, RFC) é editado diretamente pela própria revisão.

## Exemplos de uso

```
Revisa o PRD 003 antes de eu começar a implementar

Esse documento tem alguma coisa faltando?

Valida se o spec da feature de notificações está consistente

Analisa o RFC de migração do banco — está pronto pra codar?

Checa inconsistências entre o PRD 001 e o 002

Revisa o plano e valida as tasks do bundle .aidev/003-pagamentos

Verifica se o TRD bate com o código atual
```

### Como funciona (resumo)

1. **Leitura** — o documento inteiro antes de qualquer análise.
2. **Investigação do contexto real** — documentos relacionados (`depends_on`, `references`),
   código existente e **validação obrigatória** das tecnologias citadas via MCP/WebSearch.
3. **Esqueleto de avaliação** — quatro perguntas estruturantes respondidas para *este*
   documento: qual o **upstream** (a fonte de verdade contra a qual ele se mede), quais
   **invariantes** nenhuma correção pode violar, **quem é o dono da edição**, e quais **modos de
   falha** importam. Apresentado em 3–5 linhas como checkpoint barato, para o usuário corrigir a
   lente antes da revisão profunda.
4. **Revisão e resolução por inferência** — cada achado é resolvido com fonte citada antes de
   ser reportado; sem evidência, vira proposta concreta ("recomendo X por [razão], confirma?"),
   nunca pergunta em branco.
5. **Classificação e apresentação** — a tabela única de achados, com a oferta de aplicação:
   "itens **Auto** aplico em lote — vete os que discordar".

Depois disso, na **pós-revisão**, as correções aprovadas são aplicadas pelo dono do artefato.

### Fronteiras de decisão

| Zona | O que entra | Como é aplicado |
|---|---|---|
| **Autonomia** | Achados com evidência rastreável no repo/docs/documentação oficial; imprecisões técnicas com resposta objetiva (campo de API inexistente, nome genérico, mitigação já nativa do SDK) | Aplicado **em lote**, com direito a veto |
| **Usuário** | Decisão de produto sem rastro; contradição com decisão já registrada; contrato de interface com outros componentes; **qualquer achado Bloqueante**; correção que altera o **upstream** do documento | Confirmação individual |

O lote não espera as pendências da zona do usuário — pendência de produto não trava correção
técnica evidenciada.

## Limitações conhecidas

- **Nada é aplicado antes do checkpoint** — a autonomia começa depois de a tabela ser
  apresentada e o lote receber aval; nunca antes.
- **Criticidade Bloqueante nunca se auto-resolve** — por mais evidente que seja a correção.
- **Não altera o upstream por conta própria** — achado no PLAN que exige mudar o PRD é sempre
  decisão humana, e a edição volta para a skill dona.
- **Não infere sem fonte citável** — inferência sem evidência é invenção de requisito, pior que
  perguntar. Afirmações sobre APIs/SDKs externos só são validadas com certeza quando há MCP de
  documentação ou WebSearch; caso contrário, o achado indica a incerteza.
- **Não sugere mudanças de formatação ou estilo** — o foco é conteúdo técnico.
- **Não força crítica** — se o documento está claro e consistente, não inventa problema; e
  silêncio não é erro (o que não precisa estar no documento não vira achado).
- **Não opina sobre decisão já tomada e registrada** — o foco é o que ainda está indefinido.
