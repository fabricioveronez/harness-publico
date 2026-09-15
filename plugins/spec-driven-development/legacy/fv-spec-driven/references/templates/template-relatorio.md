# Template — Relatórios

Formato de saída dos modos Orquestrar e Validar. Compacto e fixo: sem narração
extensa, sem emoji.

---

## Relatório de orquestração

```
Modo: orquestrar
Conjunto: {base}  (manifesto: ./.aidev/{base}-manifest.md)
Base: <branch> @ <commit curto>

Ondas executadas nesta invocação: <ex.: onda 1>
Mergeado na base: <fatias, ou "nenhuma">
Memória consolidada: <sim (N fatias) | nada a consolidar>

| Fatia               | Onda | Estado                              | Tasks   |
|---------------------|------|-------------------------------------|---------|
| 003-toil-sync       | 1    | concluída                           | 5/5     |
| 003-toil-painel     | 1    | pausada (lacuna-spec, T03)          | 2/4     |
| 003-toil-runner     | 2    | bloqueada (needs 003-toil-sync)     | 0/3     |

Próxima ação sugerida: <1 linha, apontando o gargalo real>
```

### Vocabulário de estado

| Estado | Significa |
|---|---|
| **concluída** | todas as tasks `[X]`, branch mergeada |
| **pausada (motivo, TNN)** | o modo Implementar pausou; progresso commitado foi mergeado |
| **bloqueada (por qual fatia)** | `needs` não concluiu |
| **pendente** | elegível, ainda não executada nesta invocação |
| **erro-orquestracao** | falha ao criar worktree ou disparar — não é falha de código |

O relatório termina no estado da implementação. Fechar o ciclo é do modo Validar —
não prometa fechamento aqui.

---

## Relatório de validação

```
Modo: validar
Bundle: .aidev/{slug}
Estado: <coerente e fechado | divergências tratadas | pausado por divergência grande | validação parcial>

Cobertura: <N/M USs · N/M critérios>  (automatizáveis: N · manuais: N)

Critérios executados:
| CA   | Nível       | Resultado              |
|------|-------------|------------------------|
| CA01 | integração  | OK                     |
| CA02 | e2e         | FALHA                  |
| CA03 | manual      | verificação sugerida   |

Divergências:
| # | Classe  | Onde        | O que o contrato diz → o que o código faz | Tratamento          |
|---|---------|-------------|-------------------------------------------|---------------------|
| 1 | pequena | SPEC US01   | campo `sobrenome` → `apelido`             | SPEC ajustado       |
| 2 | grande  | US03/Rule 2 | redireciona /login → retorna 500          | gap de código       |

Fechamento: <bundle concluído | conjunto aguardando N fatia(s): a, b | não fechado>
Próxima ação sugerida: <1 linha>
```

### Regras

- **A linha `Fechamento` nunca é omitida.** Com manifesto, ela nomeia as fatias que
  faltam — é o que evita a impressão de que a feature acabou quando só uma fatia
  fechou.
- **Divergência grande em aberto impede fechamento.** Não há fechamento parcial
  com pendência.
- **Critério com `FALHA` é divergência grande automática** — apareça nas duas
  tabelas.
