# revisao-documento-tecnico

Revisa documentos técnicos (PRDs, specs, RFCs) antes da implementação para identificar inconsistências, definições em aberto, conflitos entre seções e imprecisões técnicas. Investiga o código existente, documentos relacionados e tecnologias referenciadas para validar se o que o documento descreve é viável e coerente com o estado atual do sistema. Apresenta os achados em tabela única ordenada por criticidade (Bloqueante, Alto, Médio, Baixo) com sugestão concreta e acionável para cada ponto.

## Pré-requisitos e configuração

- Documento técnico (PRD, spec, RFC) disponível no projeto ou fornecido pelo usuário
- Acesso ao código-fonte do projeto para validar o contexto real das afirmações do documento

## Dependências externas

- **MCP context7** (opcional) — validar APIs e SDKs de bibliotecas/frameworks
- **MCP docs-langchain** (opcional) — validar docs de LangChain
- **WebSearch** (opcional) — validar contra documentação oficial, issues conhecidas e comportamento real em produção

Nenhuma dessas dependências é obrigatória — a revisão funciona com o conhecimento do próprio modelo, mas a qualidade aumenta quando há validação externa das afirmações técnicas.

## Skills relacionadas

- **escrever-prd** — revisão é o passo natural após o PRD ser escrito e antes da implementação
- **brainstorm** — use brainstorm para madurar a ideia antes de formalizar o documento e rodar a revisão

## Exemplos de uso

```
Revisa o PRD 003 antes de eu começar a implementar

Esse documento tem alguma coisa faltando?

Valida se o spec da feature de notificações está consistente

Analisa o RFC de migração do banco — está pronto pra codar?

Checa inconsistências entre o PRD 001 e o 002

Verifica se o documento de arquitetura bate com o código atual
```

## Limitações conhecidas

- A revisão termina no Passo 4 (tabela de achados) — sugestões detalhadas (Passo 5) e aplicação das correções (Passo 6) só acontecem quando o usuário solicita explicitamente
- Qualidade da revisão depende do contexto disponível — quanto mais código, docs relacionados e dependências existirem no projeto, mais precisos são os achados
- Afirmações sobre APIs/SDKs externos só são validadas com certeza quando há MCP de documentação disponível ou WebSearch — caso contrário, o modelo indica incerteza no achado
- Não reescreve o documento por conta própria — aponta os problemas e aguarda decisão do usuário
- Não sugere mudanças de formatação ou estilo — foco é conteúdo técnico
- Documentos com `status: concluído` não são alvo de revisão — mudanças posteriores devem abrir novo PRD
