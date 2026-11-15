# Preflight — antes do primeiro run

Objetivo: cada item abaixo é uma falha de primeira execução que já aconteceu e que uma consulta teria evitado. Rode o que se aplica à pipeline em questão e entregue ao usuário um relatório **pronto × falta** antes de criar repositório, gravar secret ou dar push.

## 1. GitHub: conta, token e repositório

| Checagem | Comando | O que evita |
|---|---|---|
| Escopos do token | `gh auth status` | 403 em `gh repo delete` (falta `delete_repo`), em workflow (`workflow`) |
| Plano da conta | `gh api user --jq .plan.name` | 422 ao criar environment com required reviewers — no plano **free**, reviewers, rulesets e branch protection **não existem em repositório privado** |
| Visibilidade | `gh repo view dono/repo --json visibility,defaultBranchRef` | Mesmo motivo acima; e se o repositório existe |
| Remote local | `git remote -v` | Push para lugar errado / "no git remotes found" |
| Branch publicada | `git log --oneline origin/main..HEAD` | Achar que a pipeline vai rodar com commits que nem subiram |
| Rulesets | `gh api repos/dono/repo/rulesets` | Push bloqueado do bot de deploy (precisa de bypass para o GitHub Actions) |

**Plano vazio.** `.plan` costuma vir vazio quando o token não tem escopo `user`/`read:user`. Vazio significa **desconhecido**, nunca "free". Nesse caso: entregue `! gh auth refresh -h github.com -s read:user` e repita, ou pergunte o plano ao usuário. Enquanto não souber, trate reviewer/ruleset/branch protection em repositório privado como "possivelmente indisponível" e não crie nada que dependa deles.

Se o plano não suporta o que o workflow pede (ex.: `environment` com reviewer), explique a limitação e as alternativas ao usuário **antes** de criar qualquer coisa — o `environment:` no job continua funcionando, só sem proteção.

## 2. Credenciais exigidas × existentes

```bash
# exigidas pelo YAML
grep -rhoE '(secrets|vars)\.[A-Z0-9_]+' .github/workflows | sort -u
# existentes (só nomes/datas)
gh secret list -R dono/repo
gh variable list -R dono/repo
```

`GITHUB_TOKEN` é automático — não entra na lista. Se o workflow dispara outro repositório, o token de dispatch (PAT) vive no repositório **de origem** e precisa de permissão no **de destino**.

## 3. Dependências externas — consulte, não suponha

Use a credencial que a pipeline usará (lida do `.env` sem imprimir, header via stdin). Exemplos dos casos que já falharam:

**Backend remoto do Terraform (HCP Terraform / Terraform Cloud)**
- A organização do bloco `cloud {}`/`backend "remote"` existe para o token? `GET https://app.terraform.io/api/v2/organizations/<org>`
- O workspace existe e o `execution-mode` é o esperado? Se o plan/apply roda no runner, precisa ser `local`; em `remote`, o HCP tenta executar e não tem as variáveis.
```bash
TOK=$(sed -n 's/^TF_API_TOKEN=//p' .env | tr -d "\"'")
printf 'Authorization: Bearer %s\n' "$TOK" | curl -sS -H @- \
  https://app.terraform.io/api/v2/organizations/ORG/workspaces/WS | jq '.data.attributes["execution-mode"]'
```

**Chave SSH no provedor de nuvem**
- Existe chave com o **nome exato** que a pipeline busca (`data "..._ssh_key"`)?
- A fingerprint dela bate com a da chave privada que vai no secret?
```bash
# chave no .env: o script deriva a pública e as fingerprints sem imprimir a privada
python3 scripts/env-para-gh.py .env -R dono/repo --fingerprint SSH_PRIVATE_KEY
# chave em arquivo
ssh-keygen -y -f ~/.ssh/chave | ssh-keygen -l -E md5 -f -
# compare com a listagem da API do provedor (ex.: DigitalOcean GET /v2/account/keys)
```
Se a derivação falhar, a chave tem passphrase ou formato quebrado — uma pipeline não roda com chave com passphrase. Reporte ao usuário; não tente de novo por outro caminho.
Se o nome cadastrado difere, prefira ajustar a variable da pipeline a pedir para o usuário renomear.

**Registry de imagens** — o repositório de imagem existe ou será criado no primeiro push? É público (sem `imagePullSecret`)?

**DNS** — `dig +short host A` e `dig +short dominio CAA` se a pipeline emite certificado.

**Imagem base / host** — se a pipeline acessa portas do servidor (SSH, 6443), lembre que a imagem pode vir com firewall do host ativo (ufw no Ubuntu) além do firewall da cloud.

## 4. Placeholders

```bash
grep -rnE 'CONFIRMAR|TODO|changeme|example|minha-org' terraform/ ansible/ .github/ 2>/dev/null
```
Todo valor de configuração externa que foi suposto entra no relatório como "confirmar com o usuário".

## 5. Relatório

```markdown
## Preflight — dono/repo

| Item | Estado | Ação |
|---|---|---|
| Repositório | ✅ privado, plano free | — |
| Environment com reviewer | ❌ não suportado no plano | decidir: seguir sem reviewer / tornar público |
| Secrets (5 exigidos) | ⚠️ 3 de 5 | `! gh secret set X -R ...` |
| Organização HCP `foo` | ❌ não existe para o token | corrigir `versions.tf` |
| Chave SSH `projeto` na cloud | ✅ fingerprint bate | — |
```
