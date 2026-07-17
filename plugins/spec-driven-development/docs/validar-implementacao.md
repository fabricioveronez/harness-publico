# validar-implementacao

Fecha o ciclo spec-driven: valida se o código entregue é coerente com o contrato e ajusta o drift entre documento e código. Carrega o `SPEC.md` do bundle `./.aidev/{slug}/` (US Rules, Edge cases, critérios de aceite §5a) e, quando existe, o PRD como fonte de verdade; confere se cada US foi coberta, cada Rule/Edge case honrada e cada critério verificável passa. Ao achar divergência, **avalia primeiro impacto e tamanho**: pequena (textual/local) ela ajusta sozinha no documento com o PRD como autoridade; grande (comportamento que contradiz o contrato, US não entregue, mudança que mexeria no PRD) ela **pausa e pergunta ao usuário** antes de tocar em qualquer coisa. Ao terminar sem divergência grande em aberto, promove o `status` para `concluido` no frontmatter do trio (e o PRD para `concluído` quando existe).

## Pré-requisitos e configuração

- Um bundle `./.aidev/{slug}/` gerado por `preparar-execucao` e implementado por `implementar-task` (idealmente com todas as tasks `[X]` — a skill aceita validação parcial se o usuário pedir).
- Quando o `SPEC.md` tem `prd:` apontando um slug, o PRD correspondente em `./docs/prds/` é carregado como fonte de verdade. Com `prd: none`, o `SPEC.md` é a fonte de verdade.
- O `Comando de teste:` do PLAN é usado para rodar a linha de base e os critérios de aceite executáveis.

## Dependências externas

- Test runner do projeto (para rodar a linha de base e os critérios executáveis; opcional, como na `implementar-task`).
- `git` (para localizar arquivos afetados e o estado da implementação).

## Skills relacionadas

- **implementar-task** — roda antes; entrega o código e deixa o bundle no disco. Gaps de código encontrados na validação voltam para ela.
- **preparar-execucao** — recebe a delegação de rework **estrutural** (task nova, task obsoleta) e reprojeta o SPEC quando o PRD muda.
- **escrever-prd** — dona do PRD; divergência cujo ajuste correto é no PRD volta para ela (a validação nunca edita o corpo do PRD).

## Exemplos de uso

```
Valida a implementação da feature de autenticação

Fecha o ciclo do PRD 003

Confere se o código bate com a spec

Checa drift entre o que foi construído e o contrato

Finaliza o ciclo spec-driven de pagamentos
```

## Limitações conhecidas

- **Não edita código** — gap de implementação (código que contradiz o contrato) é reportado e volta para `implementar-task`, não corrigido aqui.
- **Não reestrutura PLAN/TASKS** — task nova ou obsoleta é delegada à `preparar-execucao` (modo reconciliação).
- **Não edita o corpo do PRD** — só promove o `status` do PRD para `concluído` no fechamento; ajuste de conteúdo do PRD volta para `escrever-prd`.
- **Divergência grande nunca é ajustada em silêncio** — a skill pausa e pede confirmação antes de qualquer alteração de contrato de impacto semântico ou estrutural.
- **Fechamento é terminal e por status** — só promove para `concluido` com zero divergência grande em aberto; o bundle permanece no lugar (`./.aidev/{slug}/`), congelado pelo status como registro do que foi construído. Não move nem apaga arquivos.
