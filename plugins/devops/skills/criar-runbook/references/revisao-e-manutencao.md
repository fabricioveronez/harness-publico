# Revisão e manutenção de runbook existente

Runbook é documento **vivo**. As operações de **atualizar** e **revisar/auditar** existem para que ele não vire ficção — a maior armadilha de um runbook é parecer confiável enquanto já não bate com a realidade.

## Atualizar (uma mudança aconteceu)

Gatilho: mudou algo no deploy/operação (novo passo, nova dependência, nova variável, nova falha recorrente, mudança de alvo).

1. Localize as **seções afetadas** — não reescreva o documento inteiro.
2. Aplique a mudança de forma cirúrgica, mantendo o estilo do restante.
3. Se a mudança veio de uma **falha real** resolvida, adicione a entrada correspondente no **Troubleshooting** (sintoma → causa → correção) — é o tipo de conteúdo que mais envelhece bem.
4. Preserve a coerência: se um passo mudou, confira se **verificação** e **rollback** ainda fazem sentido.

## Revisar/Auditar (o runbook ainda é verdade?)

Rode uma checagem ativa comparando o documento com a realidade atual do serviço. Procure especificamente por:

| Verificação | O que caçar | Ação |
|---|---|---|
| **Staleness** | Comandos, versões, caminhos, endpoints que não batem mais com o serviço real | Atualizar ou marcar como a confirmar |
| **Lacunas** | Falta rollback? Falta verificação executável? Passo implícito não escrito? | Preencher a seção faltante |
| **Segredo vazado** | Senha/token/chave escritos no documento (ou em exemplos) | Remover, trocar por placeholder + ponteiro para secret/config; alertar o usuário para rotacionar se já foi commitado |
| **Escopo invadido** | Passos de **provisionamento de infra** dentro do runbook de deploy; acoplamento à ferramenta de IaC | Mover para pré-requisito ou remover; manter o foco no processo-alvo |
| **Verificação não-executável** | "Confira se está no ar" em vez de um comando | Trocar por comando copy-paste que prova sucesso |
| **Troubleshooting genérico** | Entradas vagas que não ajudam | Substituir por falhas reais/conhecidas ou remover |

## Como entregar a revisão

Não aplique um monte de mudanças silenciosamente. Apresente os achados (o que está desatualizado / faltando / arriscado) e **proponha as edições**, agrupadas por severidade. Aplique as correções e diga ao usuário, em uma lista curta, o que mudou e por quê — especialmente qualquer **segredo removido** ou **escopo corrigido**, que têm impacto de segurança/clareza.

## Gestão de múltiplos runbooks

Quando há vários serviços, mantenha um runbook por serviço (`docs/runbook-<servico>.md`). Se o usuário gerir muitos, sugira um índice curto (`docs/README.md` ou uma seção) listando serviço → runbook → última revisão, para dar visibilidade de o que existe e o que pode estar velho.
