#!/usr/bin/env bash
# Espera o run de um commit aparecer, acompanha até terminar e imprime a tabela de jobs.
#
# Uso:
#   esperar-run.sh -R dono/repo --sha <sha> [--workflow arquivo.yml] [--event push] [--espera 300]
#   esperar-run.sh -R dono/repo --id <run-id>
#
# Rode com run_in_background: true. Sai com o código do run (0 = success).
# Filtra pelo headSha — nunca por horário — para não esperar para sempre por um run que já existe.
set -euo pipefail

REPO="" SHA="" WF="" EVENT="" ID="" ESPERA=300
while [ $# -gt 0 ]; do
  case "$1" in
    -R) REPO="$2"; shift 2 ;;
    --sha) SHA="$2"; shift 2 ;;
    --workflow) WF="$2"; shift 2 ;;
    --event) EVENT="$2"; shift 2 ;;
    --id) ID="$2"; shift 2 ;;
    --espera) ESPERA="$2"; shift 2 ;;
    *) echo "argumento desconhecido: $1" >&2; exit 2 ;;
  esac
done
[ -n "$REPO" ] || { echo "faltou -R dono/repo" >&2; exit 2; }

if [ -z "$ID" ]; then
  [ -n "$SHA" ] || { echo "informe --sha ou --id" >&2; exit 2; }
  # aceita SHA curto
  args=(run list -R "$REPO" --limit 30 --json databaseId,headSha,workflowName,event,status)
  [ -n "$WF" ] && args+=(--workflow "$WF")
  [ -n "$EVENT" ] && args+=(--event "$EVENT")
  inicio=$(date +%s)
  until ID=$(gh "${args[@]}" --jq "[.[] | select(.headSha | startswith(\"$SHA\"))][0].databaseId // empty" 2>/dev/null) && [ -n "$ID" ]; do
    if [ $(( $(date +%s) - inicio )) -ge "$ESPERA" ]; then
      echo "nenhum run para o SHA $SHA em ${ESPERA}s (workflow=${WF:-qualquer} event=${EVENT:-qualquer})."
      echo "Causas comuns: paths não casou, primeiro push do repo, if: sem o evento. Tente gh workflow run."
      exit 3
    fi
    sleep 5
  done
fi

echo "run $ID — https://github.com/$REPO/actions/runs/$ID"
set +e
gh run watch "$ID" -R "$REPO" --exit-status --interval 20 >/dev/null 2>&1
rc=$?
set -e

gh run view "$ID" -R "$REPO" --json workflowName,event,headSha,conclusion,jobs \
  --jq '"\(.workflowName) [\(.event)] \(.headSha[0:7]) → \(.conclusion)",
        (.jobs[] | "  \(.conclusion // .status | if . == "skipped" then "skipped (NÃO TESTADO)" else . end)\t\(.name)")'
exit $rc
