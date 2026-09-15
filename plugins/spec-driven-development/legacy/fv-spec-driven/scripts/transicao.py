#!/usr/bin/env python3
"""Promove status de bundle, manifesto e PRD — com as guardas de fechamento.

É o único caminho permitido para mudar status no ciclo fv-spec-driven. Editar o
frontmatter na mão contorna a guarda mais cara do fluxo:

    PRD e manifesto só fecham quando a última fatia fecha.

Com N fatias a validação roda uma vez por fatia. Fechar o PRD no primeiro
fechamento trancaria as fatias irmãs — PRD `concluido` é imutável, e com ele o
modo Implementar aborta e o modo Preparar recusa reconciliar. A feature ficaria
no meio, sem saída a não ser abrir um PRD novo.

Uso:
    python3 transicao.py bundle 003-toil-api --para pronto
    python3 transicao.py bundle 003-toil-api --para em-execucao
    python3 transicao.py bundle 003-toil-api --para concluido     # dispara a guarda
    python3 transicao.py prd 003-toil --para pronto
    python3 transicao.py estado 003-toil                          # inspeciona sem alterar
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ESTADOS_BUNDLE = ["rascunho", "pronto", "em-execucao", "concluido"]
ESTADOS_PRD = ["rascunho", "pronto", "em-progresso", "concluido"]

CAMPO_POR_ARQUIVO = {"SPEC.md": "status", "PLAN.md": "status", "TASKS.md": "plan_status"}

RE_TASK = re.compile(r"^##\s*\[([ Xx])\]\s*T\d+", re.MULTILINE)


def ler(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def campo_frontmatter(texto: str, campo: str) -> str | None:
    if not texto.startswith("---"):
        return None
    fim = texto.find("\n---", 3)
    if fim == -1:
        return None
    m = re.search(rf"^{re.escape(campo)}\s*:\s*(.+?)\s*$", texto[3:fim], re.MULTILINE)
    return m.group(1).strip().strip("'\"") if m else None


def escreve_campo(caminho: Path, campo: str, valor: str, dry: bool) -> tuple[bool, str]:
    """Reescreve `campo` no frontmatter preservando o resto do arquivo byte a byte."""
    texto = ler(caminho)
    if not texto:
        return False, f"{caminho.name}: arquivo ausente ou vazio"
    if not texto.startswith("---"):
        return False, f"{caminho.name}: sem frontmatter"
    fim = texto.find("\n---", 3)
    if fim == -1:
        return False, f"{caminho.name}: frontmatter não fechado"

    head, corpo = texto[3:fim], texto[fim:]
    padrao = re.compile(rf"^({re.escape(campo)}\s*:\s*)(.+?)(\s*)$", re.MULTILINE)
    if not padrao.search(head):
        return False, f"{caminho.name}: campo '{campo}' não existe no frontmatter"

    anterior = padrao.search(head).group(2).strip()
    novo_head = padrao.sub(lambda m: f"{m.group(1)}{valor}{m.group(3)}", head, count=1)
    if not dry:
        caminho.write_text("---" + novo_head + corpo, encoding="utf-8")
    return True, f"{caminho.name}: {campo} {anterior} → {valor}"


# --------------------------------------------------------------- localizadores


def dir_bundle(root: Path, slug: str) -> Path:
    return root / ".aidev" / slug


def manifesto_de(root: Path, slug: str) -> Path | None:
    """Acha o manifesto cujo prefixo casa com o slug da fatia (o mais longo vence)."""
    aidev = root / ".aidev"
    if not aidev.is_dir():
        return None
    candidatos = [
        m for m in aidev.glob("*-manifest.md")
        if slug == m.name[: -len("-manifest.md")]
        or slug.startswith(m.name[: -len("-manifest.md")] + "-")
    ]
    return max(candidatos, key=lambda m: len(m.name), default=None)


def fatias_do_manifesto(root: Path, manifesto: Path) -> list[str]:
    base = manifesto.name[: -len("-manifest.md")]
    aidev = root / ".aidev"
    return sorted(
        d.name for d in aidev.iterdir()
        if d.is_dir() and (d.name == base or d.name.startswith(base + "-"))
    )


def caminho_prd(root: Path, slug_prd: str) -> Path | None:
    if not slug_prd or slug_prd == "none":
        return None
    for cand in (
        root / "docs" / "prds" / f"{slug_prd}.md",
        root / "docs" / f"{slug_prd}.md",
        root / f"{slug_prd}.md",
    ):
        if cand.is_file():
            return cand
    achados = list((root / "docs" / "prds").glob(f"{slug_prd}*.md")) if (root / "docs" / "prds").is_dir() else []
    return achados[0] if achados else None


def bundle_concluido(d: Path) -> bool:
    """Concluído = status concluido E nenhuma task [ ] aberta."""
    spec = campo_frontmatter(ler(d / "SPEC.md"), "status")
    if spec != "concluido":
        return False
    marcas = RE_TASK.findall(ler(d / "TASKS.md"))
    return all(m.lower() == "x" for m in marcas) if marcas else True


# -------------------------------------------------------------------- comandos


def cmd_bundle(root: Path, slug: str, para: str, dry: bool) -> dict:
    if para not in ESTADOS_BUNDLE:
        return {"ok": False, "erro": f"estado inválido: {para} (use {ESTADOS_BUNDLE})"}

    d = dir_bundle(root, slug)
    if not d.is_dir():
        return {"ok": False, "erro": f"bundle não encontrado: {d}"}

    acoes, problemas = [], []

    if para == "concluido":
        marcas = RE_TASK.findall(ler(d / "TASKS.md"))
        abertas = [m for m in marcas if m.lower() != "x"]
        if abertas:
            problemas.append(
                f"{len(abertas)} de {len(marcas)} tasks ainda abertas — "
                "fechar bundle com task [ ] é incoerência estrutural"
            )
            return {"ok": False, "erro": "; ".join(problemas)}

    for arquivo, campo in CAMPO_POR_ARQUIVO.items():
        ok, msg = escreve_campo(d / arquivo, campo, para, dry)
        (acoes if ok else problemas).append(msg)

    resultado = {
        "ok": not problemas,
        "bundle": slug,
        "para": para,
        "acoes": acoes,
        "problemas": problemas,
    }

    if para != "concluido":
        return resultado

    # ---- guarda de fechamento do conjunto
    man = manifesto_de(root, slug)
    if not man:
        prd_slug = campo_frontmatter(ler(d / "SPEC.md"), "prd") or "none"
        resultado["conjunto"] = "sem manifesto (decomposição de 1 fatia)"
        resultado.update(_fecha_prd(root, prd_slug, dry))
        return resultado

    irmas = fatias_do_manifesto(root, man)
    abertas = [f for f in irmas if not bundle_concluido(root / ".aidev" / f)]
    resultado["conjunto"] = {
        "manifesto": man.name,
        "fatias": irmas,
        "abertas": abertas,
    }

    if abertas:
        resultado["prd"] = {
            "fechado": False,
            "motivo": (
                f"guarda de fechamento: {len(abertas)} fatia(s) ainda aberta(s) "
                f"({', '.join(abertas)}). PRD e manifesto permanecem abertos — "
                "fechá-los agora trancaria as fatias restantes."
            ),
        }
        resultado["manifesto_fechado"] = False
        return resultado

    ok, msg = escreve_campo(man, "status", "concluido", dry)
    resultado["manifesto_fechado"] = ok
    resultado["acoes"].append(msg if ok else f"manifesto: {msg}")
    prd_slug = campo_frontmatter(ler(man), "prd") or campo_frontmatter(ler(d / "SPEC.md"), "prd") or "none"
    resultado.update(_fecha_prd(root, prd_slug, dry))
    return resultado


def _fecha_prd(root: Path, slug_prd: str, dry: bool) -> dict:
    if not slug_prd or slug_prd == "none":
        return {"prd": {"fechado": False, "motivo": "bundle sem PRD (prd: none)"}}
    p = caminho_prd(root, slug_prd)
    if not p:
        return {"prd": {"fechado": False, "motivo": f"PRD '{slug_prd}' não localizado"}}
    ok, msg = escreve_campo(p, "status", "concluido", dry)
    return {"prd": {"fechado": ok, "arquivo": str(p), "detalhe": msg}}


def cmd_prd(root: Path, slug_prd: str, para: str, dry: bool) -> dict:
    if para not in ESTADOS_PRD:
        return {"ok": False, "erro": f"estado inválido: {para} (use {ESTADOS_PRD})"}
    if para == "concluido":
        return {
            "ok": False,
            "erro": (
                "fechar PRD diretamente é proibido — use `bundle <slug> --para concluido`, "
                "que só fecha o PRD quando a última fatia fecha"
            ),
        }
    p = caminho_prd(root, slug_prd)
    if not p:
        return {"ok": False, "erro": f"PRD '{slug_prd}' não localizado em docs/prds/"}
    atual = campo_frontmatter(ler(p), "status")
    if atual == "concluido":
        return {"ok": False, "erro": f"{p.name} está concluido — PRD concluído é imutável"}
    ok, msg = escreve_campo(p, "status", para, dry)
    return {"ok": ok, "prd": str(p), "detalhe": msg}


def cmd_estado(root: Path, slug: str) -> dict:
    man = manifesto_de(root, slug)
    if man:
        irmas = fatias_do_manifesto(root, man)
        return {
            "manifesto": man.name,
            "status_manifesto": campo_frontmatter(ler(man), "status"),
            "prd": campo_frontmatter(ler(man), "prd"),
            "fatias": {f: {
                "status": campo_frontmatter(ler(root / ".aidev" / f / "SPEC.md"), "status"),
                "concluida": bundle_concluido(root / ".aidev" / f),
            } for f in irmas},
            "pode_fechar_conjunto": all(bundle_concluido(root / ".aidev" / f) for f in irmas),
        }
    d = dir_bundle(root, slug)
    if not d.is_dir():
        return {"erro": f"nem manifesto nem bundle para '{slug}'"}
    return {
        "bundle": slug,
        "status": campo_frontmatter(ler(d / "SPEC.md"), "status"),
        "prd": campo_frontmatter(ler(d / "SPEC.md"), "prd"),
        "concluida": bundle_concluido(d),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="raiz do projeto alvo")
    ap.add_argument("--dry-run", action="store_true", help="mostra o que faria, sem escrever")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bundle", help="promove o status de um bundle (SPEC+PLAN+TASKS)")
    b.add_argument("slug")
    b.add_argument("--para", required=True, choices=ESTADOS_BUNDLE)

    p = sub.add_parser("prd", help="promove o status de um PRD (fechamento é proibido aqui)")
    p.add_argument("slug")
    p.add_argument("--para", required=True, choices=ESTADOS_PRD)

    e = sub.add_parser("estado", help="inspeciona sem alterar")
    e.add_argument("slug")

    args = ap.parse_args()
    root = Path(args.root).resolve()

    if args.cmd == "bundle":
        r = cmd_bundle(root, args.slug, args.para, args.dry_run)
    elif args.cmd == "prd":
        r = cmd_prd(root, args.slug, args.para, args.dry_run)
    else:
        r = cmd_estado(root, args.slug)

    if args.dry_run:
        r["dry_run"] = True
    print(json.dumps(r, indent=2, ensure_ascii=False))
    return 0 if r.get("ok", True) and "erro" not in r else 1


if __name__ == "__main__":
    sys.exit(main())
