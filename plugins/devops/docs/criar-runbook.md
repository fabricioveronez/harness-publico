# criar-runbook

Cria, atualiza e revisa **runbooks de deploy/ops** — o documento operacional que descreve, passo a passo, como subir, operar e reverter uma aplicação/serviço, de forma que outra pessoa consiga executar sem conhecimento tácito.

## Modos
- **Grounded** (preferido): documenta um processo **realmente executado** — extrai passos dos comandos/scripts e o troubleshooting das **falhas observadas**.
- **Descrição**: entrevista **consultiva** (infere do contexto, propõe defaults, aponta alternativas, preenche lacunas); marca seções como "não verificado".

## Princípios
Escopo enxuto (infra = pré-requisito, fora do escopo), segredos fora do documento (placeholders + config/secret), verificação executável (copy-paste), rollback sempre presente.

## Saída
Por padrão em `docs/RUNBOOK.md` (ou `docs/runbook-<servico>.md`); o usuário pode definir outro padrão/local.

## Ciclo de vida
Além de criar, **atualiza** (mudança pontual) e **revisa/audita** (staleness, lacunas, segredo vazado, escopo invadindo provisionamento).

Ver `skills/criar-runbook/` (SKILL.md + references: `anatomia-runbook.md`, `entrevista-consultiva.md`, `revisao-e-manutencao.md`).
