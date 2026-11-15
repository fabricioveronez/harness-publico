#!/usr/bin/env bash
# Mostra o log dos jobs que falharam, sem cores e sem timestamp, filtrado nas linhas que importam.
#
# Uso:
#   log-falha.sh -R dono/repo <run-id> [--contexto 12] [--tudo]
#
#   --tudo      imprime o log falho inteiro (limpo), sem filtro — use quando o filtro não achar nada
#   --contexto  linhas antes/depois de cada ocorrência (padrão 12 depois, 3 antes)
set -euo pipefail

REPO="" ID="" CTX=12 TUDO=0
while [ $# -gt 0 ]; do
  case "$1" in
    -R) REPO="$2"; shift 2 ;;
    --contexto) CTX="$2"; shift 2 ;;
    --tudo) TUDO=1; shift ;;
    *) ID="$1"; shift ;;
  esac
done
[ -n "$REPO" ] && [ -n "$ID" ] || { echo "uso: log-falha.sh -R dono/repo <run-id>" >&2; exit 2; }

# formato do --log: "<job>\t<step>\t<timestamp> <linha>"
limpo=$(gh run view "$ID" -R "$REPO" --log-failed \
  | perl -pe 's/\xEF\xBB\xBF//g; s/\e\[[0-9;]*m//g; s/\^\[\[[0-9;]*m//g' \
  | awk -F'\t' '
      { l=$3; sub(/^[0-9-]+T[0-9:.]+Z ?/, "", l) }
      # descarta o eco do script de cada step (##[group]Run ... ##[endgroup]): é código, não saída
      l ~ /^##\[group\]Run / { eco=1; next }
      eco && l ~ /^##\[endgroup\]/ { eco=0; next }
      eco { next }
      { printf "%s | %s | %s\n", $1, $2, l }')

if [ -z "$limpo" ]; then
  echo "sem log de falha (run ainda em andamento, cancelado ou sem jobs falhos)."
  gh run view "$ID" -R "$REPO" | sed -n '/JOBS/,/ANNOTATIONS/p'
  exit 0
fi

if [ "$TUDO" = 1 ]; then
  printf '%s\n' "$limpo"
  exit 0
fi

padrao='error|denied|fail|unauthorized|forbidden|not found|timed? ?out|exit code|##\[error\]|fatal|panic|refused|no such'
erros=$(printf '%s\n' "$limpo" | grep -E '##\[error\]' || true)
if [ -n "$erros" ]; then
  echo "== linhas ##[error]"
  printf '%s\n' "$erros"
  echo
  echo "== contexto"
fi
saida=$(printf '%s\n' "$limpo" | grep -n -iE -B3 -A"$CTX" "$padrao" || true)
if [ -z "$saida" ]; then
  echo "(filtro não encontrou nada — últimas 60 linhas)"
  printf '%s\n' "$limpo" | tail -60
else
  printf '%s\n' "$saida" | head -300
fi
