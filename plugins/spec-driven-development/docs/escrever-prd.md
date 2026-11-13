# escrever-prd

Cria e edita dois artefatos de produto com fluxos separados por progressive disclosure:

- **Epic** — visão de alto nível para research, direção, capacidades candidatas e milestones
  de resultado.
- **PRD** — especificação autocontida do comportamento e das regras de uma feature.

A skill seleciona um único fluxo por execução. Criar uma Epic não gera seus PRDs;
decompor uma Epic apenas apresenta candidatos em conversa; criar um PRD posterior exige uma
nova solicitação explícita.

## Quando usar Epic

Use para uma iniciativa, MVP, visão ou resultado amplo que pode envolver várias capacidades.
A Epic pode existir sem nenhum PRD e permanece útil enquanto a decomposição ainda muda.

O documento registra:

- problema, público e evidências;
- resultados e métricas agregadas;
- fronteira;
- capacidades candidatas `Cxx` e seu grau de clareza;
- milestones de resultado `Mxx`;
- sequenciamento, decisões e questões abertas.

Local padrão: `docs/epics/E###-nome-em-kebab-case.md`. O ciclo é
`explorando → planejada → em-progresso → concluida`; toda transição precisa ser solicitada e
uma Epic concluída é imutável.

## Quando usar PRD

Use quando a demanda já representa uma feature autocontida. O PRD contém contexto, solução de
produto, fora do escopo, User Stories, Rules, Edge cases, fluxo de negócio quando necessário,
critérios de aceite, métricas, riscos, dependências, referências e decisões.

Local padrão: `docs/prds/NNN-nome-em-kebab-case.md`. O ciclo continua
`rascunho | pronto | em-progresso | concluido`.

PRDs novos não possuem milestones. Os critérios recebem IDs estáveis `ACxx` e um checkbox de
aprovação; todos devem estar aprovados para a feature ser considerada concluída. A skill não
promove o status automaticamente.

## Granularidade

- Várias features autocontidas com um resultado comum formam uma possível Epic.
- Features sem resultado agregador são candidatas a PRDs separados.
- Rules, expiração, rate limit, exceções e controles que apenas tornam uma feature correta
  permanecem no mesmo PRD.
- Dependência entre features não impede o corte; dependências diretas vivem em `depends_on`.

Quando houver mais de um PRD possível, a skill apresenta o corte e espera o usuário escolher
um. Ela não cria documentos em sequência.

## Relação opcional

Um PRD criado posteriormente pode registrar:

```yaml
origin_epic: "E001"
origin_capability: "C01"
```

Esses campos indicam proveniência e só aparecem quando a origem foi fornecida explicitamente.
Não são dependências, não sincronizam status e não provocam atualização da Epic. A Epic não
mantém lista obrigatória de PRDs.

## Compatibilidade

- PRDs existentes com milestones permanecem no formato legado.
- Ao editá-los, a skill preserva milestones, IDs, checklists e semântica de conclusão.
- Nenhum milestone novo é adicionado e nenhuma migração implícita acontece.
- PRDs e Epics concluídos são imutáveis; mudanças posteriores abrem novo artefato.

## Limites

- Stack, arquitetura e NFR global ficam no TRD.
- Decisão técnica durável vira ADR.
- PLAN/TASKS cuidam da decomposição e ordem técnica.
- Decomposição de Epic não cria arquivos.
- Uma execução nunca cria ou edita Epic e PRD juntos.

## Exemplos

```text
Crie uma Epic para reduzir abandono no onboarding.

Analise a Epic E001 e proponha possíveis PRDs, sem criar arquivos.

Crie o PRD da capacidade C02 da Epic E001.

Crie um PRD para login por magic link.

Ajuste o PRD 003 para cobrir reembolso parcial.
```

## Referências internas

- `references/fluxo-epic.md` e `references/template-epic.md` — fluxo e formato de Epic.
- `references/fluxo-prd.md` e `references/template-prd.md` — fluxo e formato de PRD.
