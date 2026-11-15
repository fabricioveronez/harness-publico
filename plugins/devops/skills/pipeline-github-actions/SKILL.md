---
name: pipeline-github-actions
description: "Escreve, revisa e LEVA AO VERDE pipelines do GitHub Actions — das boas práticas do YAML (triggers, permissions, OIDC, secrets, cache, concurrency, reusable workflows, pinning) até o ciclo operacional completo: preflight do repositório e das dependências externas, secrets/variables a partir de .env sem vazar valores, disparo em etapas (PR → merge → main/dispatch), acompanhamento do run, leitura de log de falha, correção, rerun e verificação de ponta a ponta do que a pipeline entregou. Use sempre que a tarefa tocar .github/workflows/ ou .github/actions/, e também quando o usuário disser 'testa a pipeline', 'roda o workflow', 'o CI/deploy falhou', 'vê o log do Actions', 'coloca os secrets no repositório', 'por que esse job não rodou/ficou skipped', 'acompanha o run', 'cria o repo e testa a pipeline', 'dispara o deploy', ou pedir para provisionar/deployar via GitHub Actions — mesmo sem citar 'GitHub Actions' explicitamente."
---

# Pipeline GitHub Actions

Uma pipeline só está pronta quando **rodou de verdade, em todos os caminhos que importam, e o que ela devia entregar foi conferido fora do GitHub**. Escrever o YAML é a menor parte; a maior parte do trabalho é preparar o terreno, disparar, ler a falha e corrigir sem queimar runs nem vazar segredo. Esta skill cobre esse ciclo inteiro.

## Princípios que valem o tempo todo

**Fale em português do Brasil.** Logs e erros chegam em inglês; a explicação, o diagnóstico e o relatório vão em pt-BR. Quando aparecer um conceito novo para a decisão (PAT de dispatch, firewall do host, environment protegido), explique o que é, por que existe e o impacto de cada alternativa *antes* de pedir a decisão — o usuário quer decidir entendendo. Para decisões de custo ou segurança, use AskUserQuestion com a opção recomendada primeiro.

**Saiba o que é do usuário e entregue pronto, sem tentar antes.** Algumas ações são bloqueadas pelo harness ou pertencem ao humano; tentar e falhar gasta tempo e confiança. Para estas, entregue já na primeira menção o comando com prefixo `!` (roda na sessão) ou o link pronto:

| Ação | Como entregar |
|---|---|
| Valor de secret que não está em disco | `! gh secret set NOME -R dono/repo` (o usuário cola o valor) — se o `!` não for interativo, o caminho na UI: Settings → Secrets and variables → Actions |
| Criar PAT (ex.: token de dispatch entre repositórios) | URL pré-preenchida de fine-grained token (ver `references/comandos-gh.md`) |
| Merge de PR | `! gh pr merge N --merge -R dono/repo` |
| Apagar repositório, branch protegida, recurso pago | Comando pronto + confirmação explícita. Se o usuário recusou uma vez, não tente de novo sem novo pedido |
| Escopo faltando no `gh` | `! gh auth refresh -h github.com -s <escopo>` |

**Segredo não passa pelo output.** Nunca rode `source`, `cat`, `head` ou `grep` sem filtro num `.env` — uma chave PEM multilinha sem aspas quebra o `source` e o shell imprime pedaços dela no erro. Use `scripts/env-para-gh.py`, que lê o arquivo e manda cada valor por stdin ao `gh` — e que também calcula a fingerprint de uma chave SSH do `.env` (`--fingerprint NOME`). Não copie valor do `.env` para arquivo temporário, nem para inspecionar. Para chamar APIs com token, passe o header por stdin (`printf 'Authorization: Bearer %s\n' "$TOK" | curl -H @- ...`). Se algo vazou, diga no relatório final e recomende rotação.

**Shell e git.** zsh: glob entre aspas, nada de `echo ===`, `--jq` em vez de `grep` em JSON. Git: `git pull` antes da branch, confirme que o commit existe antes de `push`/`gh pr create`, commits semânticos em pt-BR. Sintaxe de `gh` para cada passo: `references/comandos-gh.md`.

## O fluxo

Siga as fases em ordem. Pule a 1 e a 2 se o workflow já está escrito e validado; nunca pule a 3.

### 0. Mapear

Antes de qualquer ação, monte o mapa (vai para o relatório final):

- **Workflows × gatilhos × jobs** — para cada job, em qual evento ele roda de fato (leia os `if:`). É assim que você descobre que `plan` e `lint` só rodam em PR e que um teste por dispatch vai deixá-los `skipped`.
- **Inventário de credenciais** — `grep -rhoE '(secrets|vars)\.[A-Z0-9_]+' .github/workflows | sort -u`. Isso é a lista do que precisa existir no repositório.
- **Repositórios envolvidos** — dispatch entre repos (`repository_dispatch`, `peter-evans/repository-dispatch`) significa dois lados para preparar e dois runs para acompanhar.
- **Docs de pré-requisitos** do projeto (`docs/pre-requisitos.md` etc.), se houver — são a fonte dos passos manuais.

### 1. Escrever ou ajustar o YAML

Leia `references/boas-praticas-yaml.md` e aplique. As regras da seção **Lições de pipelines reais** de lá são as que mais evitam runs perdidos: `workflow_dispatch` com `if:` que aceita o evento, `paths` incluindo o próprio workflow, gates repetidos no apply, nenhum placeholder de configuração externa sem `# CONFIRMAR:`. Aprofunde com `anatomia-de-um-workflow.md`, `seguranca-em-pipelines.md` e `performance-e-reuso.md` quando o caso pedir.

### 2. Validar localmente

Rode os validadores da stack antes do primeiro push. Se a ferramenta não está instalada ou está em versão diferente do pin do projeto, baixe a versão certa no scratchpad em vez de pular:

- `actionlint` em todos os workflows
- Terraform: `terraform fmt -check -recursive`, `init -backend=false`, `validate` (e `terraform test` se houver)
- Ansible: `ansible-lint` e `ansible-playbook --syntax-check` com o mesmo `ANSIBLE_COLLECTIONS_PATH` que o CI usará
- Scripts: `bash -n`, `shellcheck`

Isso pega sintaxe e estrutura. Não pega uid de container, firewall, permissão de banco nem credencial errada — por isso a fase 5 existe.

### 3. Preflight — o que precisa ser verdade antes do primeiro run

Cada run gasto descobrindo uma dependência faltando é um run que uma chamada de API teria evitado. Siga `references/preflight.md` e produza um relatório **pronto × falta** antes de publicar qualquer coisa. Em resumo:

- `gh auth status` (escopos), plano da conta e visibilidade do repositório — environment com reviewer, rulesets e branch protection dependem disso em repositório privado. Se o plano vier vazio, ele é **desconhecido**, não "free": siga o que o preflight diz para esse caso.
- Repositório existe, remote configurado, branch publicada.
- Credenciais exigidas (fase 0) × `gh secret list` / `gh variable list`.
- Dependências externas **consultadas por API**, não supostas: organização/workspace do backend remoto e seu modo de execução, chave SSH cadastrada no provedor com o nome que a pipeline espera (e fingerprint batendo com a chave privada), repositórios no registry, DNS.

### 4. Secrets e variables — antes do primeiro push

O push inicial de um repositório novo não deve disparar nada: sem secrets ele gera um run vermelho (nunca planeje um run que "vai falhar sem criar nada"); com secrets ele dispara o apply sem plan revisado, criando recurso pago. Ordem segura:

1. Criar o repositório vazio e desligar o Actions: `gh api -X PUT repos/dono/repo/actions/permissions -F enabled=false`
2. Environments → secrets/variables
3. Push da `main`
4. Religar o Actions (`-F enabled=true`) e seguir para a fase 5 pelo PR

- **Escopo mínimo.** Secret usado só por jobs que declaram `environment:` vai no environment, não no repositório — assim jobs de PR não o recebem. Crie o environment antes (`gh api -X PUT repos/dono/repo/environments/<nome>`, funciona em qualquer plano sem reviewer) e use `--env-secret NOME=<ambiente>` no script.
- Com `.env` no disco: `python3 scripts/env-para-gh.py .env -R dono/repo` (dry-run por padrão: lista só nomes, destino e escopo) → mostre o resultado ao usuário → `--aplicar`.
- Sem `.env`: entregue um `! gh secret set` por secret faltando.
- Confira só com `gh secret list` / `gh variable list` (nomes e datas). A data de atualização é como você confirma que o usuário de fato regravou um secret.

### 5. Disparar em etapas

Valide um passo antes do próximo — o usuário prefere ver o primeiro estágio verde antes de seguir:

1. **PR primeiro.** Branch com os ajustes → push → `gh pr create`. Isso exercita os jobs de PR (plan, lint, testes), que nenhum outro caminho exercita. Se não houver ajuste a fazer num repositório novo, ainda assim o primeiro run de verdade deve ser um PR — o plan revisado antes do primeiro apply.
2. **Merge pelo usuário** (comando `!` pronto). Depois confirme com `gh pr view N --json state,mergeCommit`.
3. **Run da main** — encontre o run disparado pelo merge commit (pelo SHA, não pelo horário). Se o job usa `environment:` com required reviewers, o run fica parado em *waiting* até alguém aprovar — avise o usuário junto com o comando de merge e mande o link do run (`https://github.com/dono/repo/actions/runs/<id>`), senão o acompanhamento parece travado.
4. **Dispatch** quando o push não dispara (repositório novo, `paths` não casou, retry): `gh workflow run <arquivo> --ref main [-f input=valor]`.
5. **Cross-repo** — depois do run de origem, ache o run do `repository_dispatch` no repositório de destino e acompanhe-o também.

### 6. Acompanhar

Use `scripts/esperar-run.sh -R dono/repo --sha <sha> [--workflow arquivo.yml]` com `run_in_background: true` e espere a notificação: ele acha o run pelo `headSha`, acompanha até o fim e imprime a tabela de jobs. Não use `sleep` encadeado (o harness bloqueia) nem filtro por horário (um horário chutado depois do run real faz o loop nunca terminar).

### 7. Diagnosticar e corrigir

Com o run falho:

1. `scripts/log-falha.sh -R dono/repo <run-id>` — log só dos jobs falhos, sem ANSI e sem timestamp, filtrado nas linhas que importam com contexto. Se o filtro não achar nada, rode com `--tudo`.
2. Compare o sintoma com `references/catalogo-de-falhas.md`. A maioria das falhas de primeira execução cai em uma categoria conhecida.
3. Explique ao usuário: sintoma, causa raiz, correção proposta e alternativas. Espere o aval quando a correção mudar comportamento (ex.: desligar um firewall vs. abrir uma porta).
4. Escolha o caminho de retry pela causa:
   - **Causa externa** (secret regravado, recurso cadastrado na cloud): `gh run rerun <id> --failed` — repete só o job que falhou.
   - **Causa no código**: branch `fix/...` → PR → checks → merge do usuário → run da main.
   - **A mesma falha duas vezes igual**: pare de adivinhar. Proponha um bloco de diagnóstico temporário no workflow — marcado com `# DIAGNÓSTICO TEMPORÁRIO`, dentro de `::group::diagnóstico`, imprimindo estado (portas escutando, regras de firewall, status de serviço) e nunca segredo, kubeconfig ou IP sem máscara. Remova-o no mesmo commit da correção.
5. **Diff inesperado no plan é falha, não ruído.** Um `~ update in-place` que ninguém pediu no `terraform plan` do PR precisa ser explicado ou neutralizado (`lifecycle { ignore_changes = [...] }`) antes do merge — plan verde não garante apply verde, e a API do provedor pode recusar o update. Proponha também a detecção automática para a próxima vez: `terraform plan -detailed-exitcode` no job de PR, com aviso (`::warning`) e o diff no resumo quando o código de saída for 2.
6. Ao consultar a documentação de uma ferramenta (Terraform provider, K3s, cert-manager, action), use Context7.

### 8. Verificar de ponta a ponta

"O run ficou verde" não é o critério. Confira três camadas:

1. **Jobs** — `gh run view <id> --json jobs --jq '.jobs[] | "\(.name): \(.conclusion)"'`. `skipped` significa **não testado**, nunca "passou". Se um caminho relevante ficou de fora (jobs de PR num teste por dispatch), exercite-o ou declare-o no relatório.
2. **Marcadores no log** — resumo da suíte de testes, `Plan: X to add` / `Apply complete!`, `PLAY RECAP ... failed=0`, `successfully rolled out`, commit de deploy feito pelo bot.
3. **O mundo real** — o que a pipeline devia criar ou publicar existe e responde: `curl` em `/`, health e readiness; `openssl s_client` para o certificado; `nc -z` confirmando que portas temporárias fecharam; API do provedor listando os recursos; imagem com a tag certa no registry.

### 9. Relatório final

Em pt-BR, no formato de `references/relatorio-final.md`: resultado por workflow × gatilho × job, verificação externa, correções (commits), o que não foi exercitado e pendências.
