# Template — Relatório de orquestração

Formato canônico da saída da skill `orquestrar-execucao` ao devolver controle.
Compacto e fixo, sem narração extensa, sem emoji. Emitido ao fim de cada
invocação (passo 7 do fluxo).

## Estrutura

```
Orquestração: {base}  (manifesto: ./.aidev/{base}-manifest.md)
Base: <branch/commit de partida>

Ondas executadas nesta invocação: <ex.: onda 1>
Mergeado na base: <fatias mergeadas, ou "nenhuma">

Fatias:
| Fatia                  | Onda | Estado                        | Tasks    |
|------------------------|------|-------------------------------|----------|
| 003-auth-login         | 1    | concluída                     | 5/5 [X]  |
| 003-auth-recuperacao   | 1    | pausada (lacuna-spec)         | 2/4 [X]  |
| 003-auth-2fa           | 2    | bloqueada (needs 003-auth-login) | 0/3   |

Próxima ação sugerida: <1 linha>
Lembrete: validação e fechamento do ciclo são da `validar-implementacao`.
```

## Vocabulário de estado (por fatia)

- **concluída** — todas as tasks `[X]`, branch mergeada na base.
- **pausada (motivo)** — o `implementar-task` pausou; `motivo` usa o vocabulário
  controlado do `implementar-task` (`esgotamento-ciclos`, `lacuna-spec`,
  `regressao-fora-escopo`, `infra-erro-fatal`, `flaky-detectado`,
  `incoerencia-estrutural`, `falha-pre-existente`, `falha-commit`,
  `interrupcao-manual`). Progresso commitado foi mergeado.
- **bloqueada (por qual fatia)** — não elegível porque uma dependência (`needs`)
  não concluiu.
- **pendente** — elegível mas ainda não executada nesta invocação (ex.: onda
  futura já liberada mas fora do escopo da rodada).
- **erro-orquestracao** — falha ao criar worktree / disparar (não é falha de
  código da fatia); ver sugestão de limpeza de órfãos.

## Regras de preenchimento

- Uma linha por fatia, na ordem das ondas.
- A coluna **Tasks** mostra `concluídas/total [X]` lido do `TASKS.md` da fatia.
- **Próxima ação** aponta o gargalo real: sanar a pausa de uma fatia (e qual
  skill usar), rodar `validar-implementacao` nas concluídas, ou reconciliar via
  `preparar-execucao` se houve conflito de merge / incoerência.
- Nunca omitir o lembrete de que a validação é da `validar-implementacao`.
