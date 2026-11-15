# Comandos `gh` — referência rápida

Comandos já usados em pipelines reais. `-R dono/repo` em todos quando houver mais de um repositório em jogo — esquecer o `-R` e consultar o repositório errado é um erro fácil em fluxo cross-repo.

## Repositório

```bash
gh repo create dono/repo --private              # cria vazio
git remote add origin git@github.com:dono/repo.git && git push -u origin main
gh repo list --limit 500 --json nameWithOwner,visibility \
  --jq '.[] | select(.nameWithOwner|test("nome";"i"))'   # localizar (não use grep em JSON)
gh api repos/dono/repo/rulesets                 # rulesets da branch
```

Apagar repositório é do usuário: entregue `! gh repo delete dono/repo --yes` (exige escopo `delete_repo`: `! gh auth refresh -h github.com -s delete_repo`).

## Secrets e variables

```bash
gh secret list -R dono/repo                     # nomes + data de atualização
gh variable list -R dono/repo
gh variable get NOME -R dono/repo
printf '%s' "$VALOR" | gh secret set NOME -R dono/repo     # valor por stdin, nunca por argumento
gh variable set NOME -R dono/repo --body valor
```

Para um `.env` inteiro: `scripts/env-para-gh.py`.

## Token de dispatch entre repositórios (PAT fine-grained)

O `GITHUB_TOKEN` de um run só vale no próprio repositório — para disparar `repository_dispatch` em outro, é preciso um PAT. Criar token é do usuário; entregue a URL pré-preenchida (ele só confere e escolhe o repositório de destino):

```
https://github.com/settings/personal-access-tokens/new?name=<nome>&description=<texto-url-encoded>&target_name=<dono>&expires_in=90&contents=write
```

Permissão mínima: **Contents: Read and write** apenas no repositório de destino. Depois: `! gh secret set NOME_DO_TOKEN -R dono/repo-origem`.

## Disparar

```bash
gh workflow list -R dono/repo
gh workflow run arquivo.yml -R dono/repo --ref main
gh workflow run deploy.yml -R dono/repo -f tag=<sha>       # com input
gh pr create --base main --head minha-branch --title "..." --body "$(cat <<'EOF'
...
EOF
)"
```

## Encontrar o run

```bash
SHA=$(git rev-parse HEAD)
gh run list -R dono/repo --json databaseId,headSha,event,workflowName,status \
  --jq ".[] | select(.headSha==\"$SHA\")"
gh run list -R dono/repo --workflow deploy.yml --event repository_dispatch --limit 3
```

Filtre pelo SHA, não por horário. Para esperar aparecer e acompanhar: `scripts/esperar-run.sh`.

## Acompanhar

```bash
gh run watch <id> -R dono/repo --exit-status --interval 20 >/dev/null 2>&1; echo "exit=$?"
gh run view <id> -R dono/repo | sed -n '/JOBS/,/ANNOTATIONS/p'          # resumo dos jobs
gh run view <id> -R dono/repo --json jobs --jq '.jobs[] | "\(.name): \(.conclusion)"'
gh pr checks N -R dono/repo
```

`gh run watch` bloqueia: rode com `run_in_background: true`.

## Logs

```bash
gh run view <id> -R dono/repo --log-failed | sed 's/\x1b\[[0-9;]*m//g' | cut -f3- \
  | grep -n -iE -B2 -A12 'error|denied|fail|unauthorized|exit code|##\[error\]'
gh run view <id> -R dono/repo --log | grep -E 'Apply complete|Plan:|PLAY RECAP|rolled out' -A2
gh run view <id> -R dono/repo --log | sed -n '/::group::diagn/,/::endgroup::/p'
```

Ou `scripts/log-falha.sh`.

## Rerun

```bash
gh run rerun <id> -R dono/repo --failed      # só os jobs que falharam (causa externa corrigida)
gh run rerun <id> -R dono/repo               # run inteiro
```

## PR e merge

```bash
gh pr view N -R dono/repo --json state,mergedAt,mergeCommit
gh pr view N --json files --jq '.files[].path'
```

Merge é do usuário: `! gh pr merge N --merge -R dono/repo`. O GitHub não deixa o autor aprovar o próprio PR — uma revisão feita por subagente vira comentário (`gh pr comment`), não aprovação.

## Verificação externa

```bash
curl -sS -o /dev/null -w '%{http_code} ssl_verify=%{ssl_verify_result}\n' https://host/
curl -sS https://host/api/health
echo | openssl s_client -connect host:443 -servername host 2>/dev/null | openssl x509 -noout -issuer -enddate
nc -z -G 5 IP 22 && echo aberta || echo fechada        # macOS: -G timeout
dig +short host A
```
