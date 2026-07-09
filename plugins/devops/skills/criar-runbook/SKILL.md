---
name: criar-runbook
description: "Cria, atualiza e revisa runbooks de deploy e operação — o documento operacional que descreve, passo a passo, como subir, operar e reverter uma aplicação/serviço. Funciona em dois modos: a partir de um processo REALMENTE executado (extrai passos dos comandos/scripts e o troubleshooting das falhas observadas) ou a partir de descrição, conduzindo uma entrevista CONSULTIVA (infere do contexto, sugere defaults, aponta alternativas e preenche lacunas). Use esta skill sempre que o usuário quiser documentar um deploy/processo operacional, criar/atualizar/revisar um runbook, 'documentar como subir a aplicação', 'passar esse processo pro time', gerar doc de operação, deploy guide ou playbook de deploy — mesmo sem usar a palavra 'runbook'. Ative também logo após concluir um deploy/provisionamento quando fizer sentido registrar o processo, e ao manter um runbook existente (atualizar após mudanças, auditar staleness/lacunas/segredos vazados)."
---

# Criar Runbook

Assistente de **ciclo de vida de runbooks de deploy/ops**: cria, atualiza e revisa o documento operacional que permite a **outra pessoa** subir, operar e reverter um serviço de forma repetível — sem depender de conhecimento tácito.

Você não é um preenchedor de template. Aja como um **assistente consultivo**: infira o que der do contexto (repo, artefatos, stack), **proponha** defaults e alternativas com trade-offs, **confirme** inferências e pergunte só o que for lacuna real. O valor está em reduzir o esforço do usuário e elevar a qualidade — não em despejar um formulário.

## O que este documento é (e não é)

Um runbook de deploy/ops documenta **um processo operacional** de um serviço: como entregá-lo, verificá-lo, operá-lo e revertê-lo. Ele **não** documenta o provisionamento da infraestrutura — a infra é **pré-requisito**, fora do escopo. Misturar as duas coisas é o erro mais comum e deixa o runbook confuso e falsamente acoplado à ferramenta de provisionamento.

## Três operações

Identifique qual o usuário quer (na dúvida, pergunte em uma linha):

| Operação | Quando | O que fazer |
|---|---|---|
| **Criar** | Não existe runbook do serviço | Escolha o modo de entrada (abaixo) e monte o documento |
| **Atualizar** | Algo mudou (novo passo, nova dependência, nova falha) | Refletir a mudança nas seções afetadas, sem reescrever o resto |
| **Revisar/Auditar** | Verificar se o runbook ainda bate com a realidade | Ver `references/revisao-e-manutencao.md` |

## Dois modos de entrada (para "Criar")

**Detecte o modo antes de escrever.** Se há um processo já executado ou artefatos reais (script de deploy, histórico de comandos, pipeline, a própria sessão em que o deploy rodou), use **Grounded**. Senão, use **Descrição**.

### Modo Grounded (a partir de execução real) — preferir sempre que possível
É o que produz runbook de maior qualidade, porque documenta a **realidade observada**, não a teoria.
- Extraia os **passos** dos comandos/scripts efetivamente rodados (ex.: um `deploy.sh`, comandos SSH, um pipeline).
- Extraia o **troubleshooting** das **falhas realmente encontradas** durante a execução (o erro X que aconteceu e como foi resolvido) — isso é ouro e nenhum template gera.
- A seção de **verificação** vira os comandos que de fato comprovaram sucesso (health check, escrita/leitura no banco, status do serviço).

### Modo Descrição (entrevista consultiva) — quando nada rodou ainda
Conduza a entrevista descrita em `references/entrevista-consultiva.md`. Em resumo: infira do contexto, proponha defaults, ofereça alternativas, confirme, e pergunte só as lacunas reais até fechar as seções-núcleo.
- **Honestidade:** marque como **"não verificado"** as seções que vieram só de descrição e não puderam ser testadas. Não finja que o não-executado foi validado.

## Princípios inegociáveis

Aplique sempre, nos dois modos — explique ao usuário quando um deles mudar o documento:

1. **Escopo enxuto.** Documente só o processo-alvo. Infra (rede, cluster, banco provisionado, DNS) é **pré-requisito**, citada como condição de entrada — não como passo. Não mencione nem dependa da ferramenta que provisionou a infra.
2. **Segredos fora do documento.** Nunca escreva senha/token/chave no runbook. Use placeholders (`<DB_PASSWORD>`) e aponte para um arquivo de config gitignored ou um secret manager. Em operação real, valores **não-sensíveis** do ambiente podem ser concretos; segredos, nunca.
3. **Verificação executável.** A seção de verificação deve ser **copy-paste** e provar sucesso ponta-a-ponta (não "verifique se está no ar", e sim o comando que comprova).
4. **Rollback sempre presente.** Como reverter/parar com segurança. Se não há rollback trivial (ex.: migrations), diga isso explicitamente.
5. **Cite só o necessário.** Pré-requisitos = o que o operador realmente precisa ter/saber. Nada de encher com genérico.

## Fluxo de trabalho

1. **Enquadrar**: operação (criar/atualizar/revisar) + serviço-alvo. Detectar o alvo do deploy (VM+systemd, container, Kubernetes, serverless, PaaS) — isso molda os passos, não a estrutura.
2. **Coletar**: modo Grounded (ler artefatos/execução) ou Descrição (entrevista consultiva).
3. **Montar** com a anatomia canônica (`references/anatomia-runbook.md`), adaptada ao alvo. Aplicar os princípios.
4. **Salvar**: por padrão em `docs/` do projeto, como `docs/RUNBOOK.md` (ou `docs/runbook-<servico>.md` quando houver mais de um serviço). Se o usuário pedir outro padrão/local, seguir o dele.
5. **Fechar**: apontar seções "não verificadas" (se houver) e sugerir o próximo passo (ex.: rodar a verificação de verdade para promover de "descrito" a "verificado").

## Onde aprofundar

Carregue sob demanda:

| Cenário | Reference |
|---|---|
| Montando o documento — quais seções, o que vai em cada uma, como adaptar ao alvo (VM/container/k8s/serverless) | `references/anatomia-runbook.md` |
| Modo Descrição — como inferir, sugerir, apontar alternativas e conduzir a entrevista sem virar formulário | `references/entrevista-consultiva.md` |
| Atualizar ou auditar um runbook existente — detectar staleness, lacunas, segredo vazado, escopo invadindo provisionamento | `references/revisao-e-manutencao.md` |
