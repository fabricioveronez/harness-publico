# Entrevista consultiva (modo Descrição)

Quando não há execução real para documentar, você monta o runbook conversando com o usuário. O objetivo é **não** transformar isso num interrogatório. Aja como um engenheiro sênior ajudando um colega: você já traz hipóteses, sugere o caminho comum, aponta alternativas e só gasta a atenção do usuário nas lacunas que realmente importam.

## Princípio central: inferir → propor → confirmar → só então perguntar

Para cada informação que o runbook precisa, siga esta ordem:

1. **Inferir** do contexto disponível antes de perguntar. Leia o repositório: linguagem, framework, `Dockerfile`/`compose`, manifests k8s, CI, `requirements`/`package.json`, `.env.example`, scripts existentes. Muita coisa se deduz daí (stack, porta, forma de start, banco).
2. **Propor** um default com base na inferência e nas boas práticas. "Detectei Flask + gunicorn e porta 8000; vou assumir deploy em VM com systemd. Ok?" é melhor que "Como você quer subir a app?".
3. **Oferecer alternativas** com trade-off quando a decisão for relevante, para o usuário escolher com informação — não deixá-lo inventar do zero.
4. **Perguntar** apenas o que não deu para inferir nem propor com segurança (ex.: endpoint do banco, quem é o operador, se há rollback especial).

## Como perguntar

- **Agrupe** perguntas relacionadas; no máximo ~3 por vez. Sempre com uma recomendação embutida ("sugiro X porque…") em vez de pergunta aberta.
- **Confirme inferências** em vez de perguntar do zero: "Assumi Postgres pelo `psycopg2` no requirements — confere?".
- **Não pergunte o que não muda o documento.** Se a resposta não altera nenhuma seção, corte a pergunta.
- **Detecte contradições e riscos** e sinalize proativamente: "Você citou subir como root — recomendo um usuário dedicado com least privilege; quer que eu já documente assim?".

## Lacunas que costumam exigir pergunta (não dão para inferir)

- Endpoint/host reais do runtime e do banco (a menos que estejam em config).
- Quem executa o runbook e com qual acesso (operador, sudo, credenciais).
- Estratégia de rollback quando não é trivial (migrations, dados).
- Requisitos de disponibilidade/HTTPS/domínio, se relevantes.
- Particularidades operacionais que só o usuário sabe (janela de deploy, dependências externas).

## Consultar melhores opções

Quando o usuário estiver indeciso ou o cenário permitir mais de um caminho, traga o leque de opções **relevantes ao alvo** com uma recomendação:
- entrega (rsync/git clone/imagem), forma de rodar (systemd/container/k8s), gestão de segredo (env file/secret manager), verificação (health check/smoke test).
Uma tabela curta `Opção | Quando faz sentido` resolve — e você recomenda a default.

## Fechamento honesto

Ao final do modo Descrição, o runbook contém passos e verificações que **não foram executados**. Marque essas seções como **"não verificado"** e ofereça o próximo passo: "Quando você rodar o deploy de verdade, me chame que eu promovo a verificação de 'descrita' para 'validada' e adiciono o troubleshooting real das falhas que aparecerem."
