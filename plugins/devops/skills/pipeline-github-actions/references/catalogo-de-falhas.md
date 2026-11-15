# Catálogo de falhas

Falhas reais de primeira execução, generalizadas. Procure pelo sintoma (texto do erro); a causa e a correção costumam se repetir entre projetos. Quando resolver uma falha nova que não está aqui, vale propor ao usuário acrescentá-la.

Índice: [GitHub e gh](#github-e-gh) · [Gatilhos e condições](#gatilhos-e-condições) · [Secrets e credenciais](#secrets-e-credenciais) · [Terraform](#terraform) · [Rede e host](#rede-e-host) · [Container e runner](#container-e-runner) · [Banco de dados](#banco-de-dados) · [Ruído](#ruído-não-exige-ação)

## GitHub e gh

**`HTTP 403: Must have admin rights ... needs the "delete_repo" scope`**
- Causa: o token do `gh` não tem o escopo.
- Correção: `! gh auth refresh -h github.com -s delete_repo` (o usuário roda). Ação destrutiva: confirme de novo antes de executar.

**`422 ... Failed to create the environment protection rule ... billing plan supports the required reviewers`**
- Causa: required reviewers (e rulesets/branch protection) não existem em repositório **privado** no plano free.
- Correção: decisão do usuário — seguir sem reviewer (o `environment:` funciona, sem proteção), tornar o repositório público ou mudar de plano. Atualize a documentação que promete o reviewer.
- Prevenção: preflight (`gh api user --jq .plan.name`).

**`gh pr merge` / aprovação bloqueada**
- Causa: o harness bloqueia merge sem revisão humana; o GitHub não deixa o autor aprovar o próprio PR.
- Correção: entregar `! gh pr merge N --merge -R dono/repo`.

## Gatilhos e condições

**Push feito, nenhum run apareceu**
- Causas: `paths` não casou (a mudança foi só no YAML do workflow e o filtro não inclui o próprio arquivo); primeiro push de repositório recém-criado; branch fora do filtro.
- Correção: `gh workflow run arquivo.yml --ref main`; incluir o workflow no `paths`.

**"Run workflow" (dispatch) cria um run sem nenhum job**
- Causa: os `if:` dos jobs só aceitam `push`/`pull_request`.
- Correção: incluir `github.event_name == 'workflow_dispatch'` no `if:`.

**Job `plan`/`lint` aparece como `-`/`skipped` num run "verde"**
- Causa: o job tem `if: github.event_name == 'pull_request'` e o teste foi por push/dispatch. Não é falha — é caminho **não testado**.
- Correção: abrir um PR de teste para exercitar, ou fazer o apply repetir os gates. Nunca relatar como "passou".

## Secrets e credenciais

**`./.env:7: command not found: OPENSSH...` (ao dar `source .env`)**
- Causa: chave PEM multilinha sem aspas. O shell executa cada linha — e imprime partes da chave no erro.
- Correção: `scripts/env-para-gh.py`. Se vazou no output, recomendar rotação da chave.

**`unauthorized: incorrect username or password` no `docker/login-action`**
- Causa: secret do registry errado — usuário diferente do login, senha no lugar do access token, espaço/quebra de linha colada junto.
- Correção: usuário regrava (`! gh secret set DOCKERHUB_TOKEN -R ...`), confirme pela data em `gh secret list`, depois `gh run rerun <id> --failed`.

**Token de dispatch: run de origem verde, nada acontece no destino**
- Causa: PAT ausente, expirado ou sem `Contents: write` no repositório de destino; `event-type` diferente do `types:` do `repository_dispatch`.
- Correção: conferir o secret no repositório de origem e o `types:` no workflow de destino; disparar o destino à mão com `gh workflow run ... -f tag=<sha>` enquanto isso.

## Terraform

**Falha em segundos no `terraform init` com backend remoto (organização/workspace não encontrados, ou HCP tentando executar remotamente)**
- Causa: nome da organização era placeholder/suposto; workspace em `execution-mode: remote` quando o plan/apply roda no runner.
- Correção: corrigir o nome no bloco `cloud {}`; mudar o workspace para `local` (API `PATCH /workspaces/<id>` ou UI). Prevenção: preflight.

**`Error: no ssh key found with name <x>` (data source de chave SSH)**
- Causa: chave não cadastrada no provedor, ou cadastrada com outro nome.
- Correção: usuário cadastra (entregue a chave **pública**: `ssh-keygen -y -f ~/.ssh/chave`); se o nome difere, ajuste a variable (`gh variable set SSH_KEY_NAME --body <nome-real>`) e rode de novo.

**Apply falha com `400 ... missing the following required fields` num recurso que o plan mostrava como `~ update in-place`**
- Causa: drift do provider — o state/ provider produz um diff (ex.: bloco `settings {}` vazio) que a API recusa. O plan do PR já mostrava, e foi tratado como "inofensivo".
- Correção: `lifecycle { ignore_changes = [<atributo>] }` (ou corrigir o atributo), plan precisa voltar a `No changes`. Regra: diff inesperado no plan bloqueia o merge.

## Rede e host

**Timeout em `nc -z IP 6443` (ou outra porta) a partir do runner, enquanto a 22 funciona; repete igual no rerun**
- Causa: firewall do host ativo na imagem base (ufw no Ubuntu de alguns provedores libera só SSH), além do firewall da cloud. Portas 80/443 podem funcionar por NAT do próprio K3s/ingress e mascarar o problema.
- Diagnóstico: bloco temporário imprimindo `ss -ltnp`, `ufw status`, IP do runner vs regra criada, regras do firewall da cloud.
- Correção (decisão do usuário): liberar a porta no ufw via configuração (Ansible) ou desativar o ufw e confiar no firewall da cloud.

**`Permission denied (publickey)` ao acessar o servidor localmente**
- Causa: chave errada / agent sem identidade.
- Correção: `ssh -i ~/.ssh/<chave-da-pipeline> ...`.

## Container e runner

**`Permission denied (os error 13)` em `node_modules`/volume ao rodar dentro de devcontainer no runner; `postCreateCommand ... failed`**
- Causa: no runner Linux, o devcontainer CLI remapeia o uid do usuário do container para o uid do runner (1001); volumes criados antes com uid 1000 ficam inacessíveis. Não aparece no macOS.
- Correção: no CI, `devcontainer up --workspace-folder . --update-remote-user-uid-default off` antes do comando. Não mude `updateRemoteUserUID` no `devcontainer.json` (quebra hosts Linux de desenvolvedores). `chown` apenas desloca o erro.

**Python local com erro de certificado SSL ao chamar API**
- Causa: Python sem CA bundle no macOS.
- Correção: use `curl`.

## Banco de dados

**`ERROR: permission denied for schema public` na migração**
- Causa: PostgreSQL 15+ — o schema `public` pertence ao dono do banco e usuários criados pela API do provedor não têm `CREATE`.
- Correção: `GRANT USAGE, CREATE ON SCHEMA public TO <usuario_app>;` de forma idempotente na configuração (Ansible/Terraform), executado com o usuário admin (credenciais via env + `::add-mask::`).

## Ruído (não exige ação)

- `Node.js 20 actions are deprecated` — aviso de runtime da action; anote como follow-up de atualização.
- `Failed to remove http...extraheader` no post-checkout após `chown` do workspace — efeito colateral do `chown`; inofensivo.
