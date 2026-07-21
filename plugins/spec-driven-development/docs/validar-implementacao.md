# validar-implementacao

Fecha o ciclo spec-driven: valida se o código entregue é coerente com o contrato e ajusta o
drift entre documento e código. Carrega o `SPEC.md` do bundle `./.aidev/{slug}/` (US Rules, Edge
cases, critérios de aceite §5a) e, quando existe, o PRD como fonte de verdade; confere se cada
US foi coberta, cada Rule/Edge case honrada e cada critério verificável passa — e também se a
**projeção SPEC↔PRD continua fiel**. Ao achar divergência, **avalia primeiro impacto e
tamanho**: pequena (textual/local) ela ajusta sozinha no documento com o PRD como autoridade;
grande (comportamento que contradiz o contrato, US não entregue, SPEC muito defasado do PRD,
mudança que mexeria no PRD) ela **pausa e pergunta ao usuário** antes de tocar em qualquer
coisa. Ao terminar sem divergência grande em aberto, promove o `status` para `concluido` no
frontmatter do bundle (e o PRD para `concluido` quando existe).

## Pré-requisitos e configuração

- Um bundle `./.aidev/{slug}/` gerado por `preparar-execucao` e implementado por
  `implementar-task` (idealmente com todas as tasks `[X]` — a skill aceita validação parcial se
  o usuário pedir).
- **Um bundle por invocação.** A skill recebe um slug. Numa decomposição multi-fatia, isso
  significa **uma invocação por fatia** — não há validação agregada do manifesto.
- **Linha de base verde.** A suíte é rodada antes da análise; vermelho pré-existente contamina o
  julgamento, então a skill **reporta e para** antes de validar coerência.
- Quando o `SPEC.md` tem `prd:` apontando um slug, o PRD correspondente em `./docs/prds/` é
  carregado como fonte de verdade. Com `prd: none`, o `SPEC.md` é a fonte de verdade.
- O `Comando de teste:` do PLAN é usado para rodar a linha de base e os critérios de aceite
  executáveis.

## Dependências externas

- Test runner do projeto (para rodar a linha de base e os critérios executáveis; opcional, como
  na `implementar-task`).
- `git` (para localizar arquivos afetados e o estado da implementação).

## Skills relacionadas

- **implementar-task** — roda antes; entrega o código e deixa o bundle no disco. Gaps de código
  encontrados na validação voltam para ela.
- **orquestrar-execucao** — quando houve execução paralela, ela termina na implementação e
  aponta para esta skill; cada fatia concluída é validada separadamente.
- **preparar-execucao** — recebe a delegação de rework **estrutural** (task nova, task obsoleta)
  e reprojeta o SPEC quando o PRD muda.
- **escrever-prd** — dona do PRD; divergência cujo ajuste correto é no PRD volta para ela (a
  validação nunca edita o corpo do PRD).

## Exemplos de uso

```
Valida a implementação da feature de autenticação

Fecha o ciclo do PRD 003

Confere se o código bate com a spec

Checa drift entre o que foi construído e o contrato

Finaliza o ciclo spec-driven de pagamentos
```

### O que é promovido no fechamento

| Arquivo | Campo | Vira |
|---|---|---|
| `SPEC.md` | `status` | `concluido` |
| `PLAN.md` | `status` | `concluido` |
| `TASKS.md` | `plan_status` | `concluido` |
| PRD (quando existe) | `status` | `concluido` |

## Limitações conhecidas

- **Não edita código** — gap de implementação (código que contradiz o contrato) é reportado e
  volta para `implementar-task`, não corrigido aqui.
- **Não reestrutura PLAN/TASKS** — task nova ou obsoleta é delegada à `preparar-execucao` (modo
  reconciliação).
- **Não edita o corpo do PRD** — só promove o `status` do PRD no fechamento; ajuste de conteúdo
  do PRD volta para `escrever-prd`.
- **Divergência grande nunca é ajustada em silêncio** — a skill pausa e pede confirmação antes
  de qualquer alteração de contrato de impacto semântico ou estrutural.
- **Fechamento é terminal e por status** — só promove para `concluido` com zero divergência
  grande em aberto; o bundle permanece no lugar (`./.aidev/{slug}/`), congelado pelo status como
  registro do que foi construído. Não move nem apaga arquivos.

### Referências da skill

- `references/heuristicas-validacao.md` — classificação de divergências (pequena × grande) e
  critérios de cobertura.
- `references/template-relatorio.md` — formato do relatório de validação e do veredito de
  fechamento.
