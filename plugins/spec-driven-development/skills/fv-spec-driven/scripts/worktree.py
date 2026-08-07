#!/usr/bin/env python3
"""Isolamento por git worktree para a execução paralela de fatias.

Cada fatia de uma onda roda num worktree próprio, na branch `exec/{base}-{fatia}`.
O motivo não é organização: o modo Implementar commita a cada task, e várias
fatias no mesmo working tree disputariam index e HEAD mesmo com arquivos
disjuntos.

`criar` recusa começar se o bundle não estiver commitado. Isso não é zelo — o
worktree é um check-out do HEAD, então um bundle apenas gravado em disco (e
portanto untracked) simplesmente não existe lá dentro, e a instância de
Implementar daquela fatia abriria um `./.aidev/` vazio.

Uso:
    python3 worktree.py criar   --base 003-toil --fatias api,ui
    python3 worktree.py mergear --base 003-toil --fatias api,ui
    python3 worktree.py limpar  --base 003-toil --fatias api,ui
    python3 worktree.py orfaos  --base 003-toil
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def git(root: Path, *args: str) -> tuple[int, str, str]:
    """Só o newline final é removido — `status --porcelain` codifica estado na
    coluna 1, então um lstrip aqui deslocaria o caminho de toda primeira linha."""
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)
    return proc.returncode, proc.stdout.rstrip("\n"), proc.stderr.strip()


def caminho_wt(root: Path, base: str, fatia: str) -> Path:
    return (root.parent / ".aidev-wt" / f"{base}-{fatia}").resolve()


def branch_de(base: str, fatia: str) -> str:
    return f"exec/{base}-{fatia}"


def slug_fatia(base: str, fatia: str) -> str:
    return fatia if fatia.startswith(base) else f"{base}-{fatia}"


def checa_precondicoes(root: Path, base: str) -> list[str]:
    problemas = []
    code, _, _ = git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return [f"{root} não é um repositório git"]

    _, porcelain, _ = git(root, "status", "--porcelain")
    if porcelain:
        alheios = [l[3:] for l in porcelain.splitlines()]
        problemas.append(
            "working tree sujo antes de criar worktrees: "
            + ", ".join(alheios[:8])
            + (" …" if len(alheios) > 8 else "")
        )

    code, _, _ = git(root, "ls-files", "--error-unmatch", ".aidev")
    if code != 0:
        problemas.append(
            "o bundle em ./.aidev/ não está commitado — o worktree nasce do HEAD "
            "e não enxergaria SPEC/PLAN/TASKS. Commite o bundle antes de orquestrar."
        )
    return problemas


def cmd_criar(root: Path, base: str, fatias: list[str], dry: bool) -> dict:
    problemas = checa_precondicoes(root, base)
    if problemas:
        return {"ok": False, "erro": "pré-condições não atendidas", "problemas": problemas}

    _, head, _ = git(root, "rev-parse", "--short", "HEAD")
    head = head.strip()
    criados, falhas = [], []
    for fatia in fatias:
        slug = slug_fatia(base, fatia)
        destino, branch = caminho_wt(root, base, fatia), branch_de(base, fatia)
        bundle = root / ".aidev" / slug
        if not bundle.is_dir():
            falhas.append({"fatia": slug, "erro": f"bundle ausente: .aidev/{slug}"})
            continue
        if destino.exists():
            falhas.append({"fatia": slug, "erro": f"caminho já ocupado: {destino} (rode `orfaos`)"})
            continue
        code, _, _ = git(root, "rev-parse", "--verify", branch)
        if code == 0:
            falhas.append({"fatia": slug, "erro": f"branch já existe: {branch} (rode `orfaos`)"})
            continue
        if dry:
            criados.append({"fatia": slug, "worktree": str(destino), "branch": branch, "dry_run": True})
            continue
        destino.parent.mkdir(parents=True, exist_ok=True)
        code, out, err = git(root, "worktree", "add", str(destino), "-b", branch)
        if code != 0:
            falhas.append({"fatia": slug, "erro": err or out})
        else:
            criados.append({
                "fatia": slug, "worktree": str(destino), "branch": branch,
                "bundle_no_worktree": str(destino / ".aidev" / slug),
            })
    return {"ok": not falhas, "base_head": head, "criados": criados, "falhas": falhas}


def cmd_mergear(root: Path, base: str, fatias: list[str], dry: bool) -> dict:
    """Merge sequencial ao fim da onda. Conflito para tudo — é sinal de corte não-disjunto."""
    mergeados, conflitos, falhas = [], [], []
    for fatia in fatias:
        slug, branch = slug_fatia(base, fatia), branch_de(base, fatia)
        code, _, _ = git(root, "rev-parse", "--verify", branch)
        if code != 0:
            falhas.append({"fatia": slug, "erro": f"branch inexistente: {branch}"})
            continue
        if dry:
            mergeados.append({"fatia": slug, "branch": branch, "dry_run": True})
            continue
        code, out, err = git(root, "merge", "--no-ff", branch, "-m", f"merge(exec): {slug}")
        if code == 0:
            mergeados.append({"fatia": slug, "branch": branch})
            continue
        _, conflitantes, _ = git(root, "diff", "--name-only", "--diff-filter=U")
        git(root, "merge", "--abort")
        conflitos.append({
            "fatia": slug,
            "arquivos": [c for c in conflitantes.splitlines() if c],
            "detalhe": (err or out).splitlines()[:3],
        })
        break  # conflito interrompe a onda: o corte precisa ser reconciliado

    resultado = {"ok": not conflitos and not falhas, "mergeados": mergeados, "falhas": falhas}
    if conflitos:
        resultado["conflitos"] = conflitos
        resultado["acao"] = (
            "conflito de merge = decomposição não era disjunta. Worktrees preservados. "
            "Reconcilie o corte no modo Preparar; não resolva o conflito à mão."
        )
        if any("MEMORY" in a for c in conflitos for a in c["arquivos"]):
            resultado["nota"] = (
                "conflito em MEMORY.md indica que uma fatia escreveu na memória "
                "consolidada em vez de docs/.memory/{fatia}.md — ver memory_fold.py"
            )
    return resultado


def cmd_limpar(root: Path, base: str, fatias: list[str], forcar: bool, dry: bool) -> dict:
    removidos, mantidos = [], []
    for fatia in fatias:
        slug, destino, branch = slug_fatia(base, fatia), caminho_wt(root, base, fatia), branch_de(base, fatia)
        if dry:
            removidos.append({"fatia": slug, "dry_run": True})
            continue
        args = ["worktree", "remove", str(destino)] + (["--force"] if forcar else [])
        code, out, err = git(root, *args)
        if code != 0 and destino.exists():
            mantidos.append({
                "fatia": slug, "worktree": str(destino), "erro": err or out,
                "dica": "worktree sujo: a fatia deixou arquivo não commitado. "
                        "Verifique antes de forçar — --forcar descarta o que estiver lá.",
            })
            continue
        code_b, _, err_b = git(root, "branch", "-d", branch)
        removidos.append({
            "fatia": slug,
            "worktree_removido": True,
            "branch_removida": code_b == 0,
            "branch_nota": None if code_b == 0 else (err_b or "branch mantida: não totalmente mergeada"),
        })
    git(root, "worktree", "prune")
    return {"ok": not mantidos, "removidos": removidos, "mantidos": mantidos}


def cmd_orfaos(root: Path, base: str | None) -> dict:
    _, lista, _ = git(root, "worktree", "list", "--porcelain")
    worktrees = [l.split(" ", 1)[1] for l in lista.splitlines() if l.startswith("worktree ")]
    _, branches, _ = git(root, "branch", "--list", "exec/*", "--format=%(refname:short)")
    branches = [b for b in branches.splitlines() if b]
    if base:
        worktrees = [w for w in worktrees if f"{base}-" in w or w.endswith(base)]
        branches = [b for b in branches if b.startswith(f"exec/{base}")]
    _, mergeadas, _ = git(root, "branch", "--merged", "--format=%(refname:short)")
    mergeadas = set(mergeadas.splitlines())
    return {
        "ok": True,
        "worktrees": [w for w in worktrees if ".aidev-wt" in w],
        "branches_exec": [
            {"branch": b, "ja_mergeada": b in mergeadas,
             "seguro_apagar": b in mergeadas}
            for b in branches
        ],
        "nota": "branch não mergeada carrega trabalho — confirme com o usuário antes de apagar",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="raiz do repositório base")
    ap.add_argument("--dry-run", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    for nome, ajuda in [
        ("criar", "cria um worktree por fatia da onda"),
        ("mergear", "mergeia as branches da onda de volta na base, em sequência"),
        ("limpar", "remove worktrees e branches já mergeadas"),
    ]:
        p = sub.add_parser(nome, help=ajuda)
        p.add_argument("--base", required=True)
        p.add_argument("--fatias", required=True, help="lista separada por vírgula")
        if nome == "limpar":
            p.add_argument("--forcar", action="store_true", help="descarta conteúdo não commitado")

    o = sub.add_parser("orfaos", help="lista worktrees e branches exec/* de execuções anteriores")
    o.add_argument("--base", default=None)

    args = ap.parse_args()
    root = Path(args.root).resolve()
    fatias = [f.strip() for f in getattr(args, "fatias", "").split(",") if f.strip()]

    if args.cmd == "criar":
        r = cmd_criar(root, args.base, fatias, args.dry_run)
    elif args.cmd == "mergear":
        r = cmd_mergear(root, args.base, fatias, args.dry_run)
    elif args.cmd == "limpar":
        r = cmd_limpar(root, args.base, fatias, args.forcar, args.dry_run)
    else:
        r = cmd_orfaos(root, args.base)

    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0 if r.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
