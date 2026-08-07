#!/usr/bin/env python3
"""Estado do ./.aidev/ e do git, em JSON, com o modo sugerido.

Este script é o roteador de modo da skill fv-spec-driven. Ele existe porque
decidir a fase do ciclo depende de cruzar seis sinais (status, contagem de [X],
pausas abertas, grafo needs, coerência manifesto<->fatias e estado do git) em N
fatias — uma contagem que a leitura em prosa erra em silêncio quando o bundle
cresce.

Uso:
    python3 bundle_state.py                 # varre ./.aidev/
    python3 bundle_state.py --root /caminho
    python3 bundle_state.py --slug 003-toil # limita a um conjunto
    python3 bundle_state.py --resumo        # texto curto em vez de JSON
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ARQUIVOS_BUNDLE = ("SPEC.md", "PLAN.md", "TASKS.md")

RE_TASK = re.compile(r"^##\s*\[([ Xx])\]\s*(T\d+)\s*(\[P\])?\s*:", re.MULTILINE)
RE_NEEDS = re.compile(r"^\s*[-*]\s*\*\*needs:\*\*\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)
RE_PAUSA = re.compile(r"^>\s*Pausa em\s+([\d\-: ]+):\s*([a-z\-]+)", re.MULTILINE)
RE_LINHA_FATIA = re.compile(r"^\|\s*`?([\w.\-]+)`?\s*\|(.*)\|\s*$", re.MULTILINE)
RE_ONDA = re.compile(r"^[-*]\s*\*\*Onda\s+(\d+)\*\*[^:]*:\s*(.+)$", re.MULTILINE)
RE_ID_CRASE = re.compile(r"`([\w.\-]+)`")


# --------------------------------------------------------------------------- io


def ler(caminho: Path) -> str:
    try:
        return caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def frontmatter(texto: str) -> dict:
    """Parser mínimo de frontmatter YAML plano (key: value). Sem dependência externa."""
    if not texto.startswith("---"):
        return {}
    fim = texto.find("\n---", 3)
    if fim == -1:
        return {}
    dados = {}
    for linha in texto[3:fim].splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or ":" not in linha:
            continue
        chave, _, valor = linha.partition(":")
        dados[chave.strip()] = valor.strip().strip("'\"")
    return dados


# ------------------------------------------------------------------------- git


def git(root: Path, *args: str) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=30,
        )
        return proc.returncode, (proc.stdout or "") + (proc.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return 1, ""


def estado_git(root: Path, aidev_rel: str) -> dict:
    code, _ = git(root, "rev-parse", "--is-inside-work-tree")
    if code != 0:
        return {"is_repo": False}

    _, branch = git(root, "branch", "--show-current")
    code, porcelain = git(root, "status", "--porcelain")
    sujos, untracked_bundle = [], []
    for linha in porcelain.splitlines():
        if len(linha) < 4:
            continue
        marca, caminho = linha[:2], linha[3:].strip().strip('"')
        sujos.append({"marca": marca.strip(), "caminho": caminho})
        if marca.strip() == "??" and caminho.startswith(aidev_rel):
            untracked_bundle.append(caminho)

    # O worktree nasce do HEAD: bundle não rastreado não existe dentro dele.
    code, _ = git(root, "ls-files", "--error-unmatch", aidev_rel)
    bundle_commitado = code == 0

    return {
        "is_repo": True,
        "branch": branch.strip(),
        "clean": not sujos,
        "arquivos_sujos": sujos,
        "bundle_untracked": untracked_bundle,
        "bundle_commitado": bundle_commitado,
    }


# ------------------------------------------------------------------- parsing md


def parse_tasks(texto: str) -> dict:
    tasks = []
    marcas = list(RE_TASK.finditer(texto))
    for i, m in enumerate(marcas):
        inicio = m.end()
        fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
        corpo = texto[inicio:fim]

        needs_m = RE_NEEDS.search(corpo)
        needs_txt = needs_m.group(1).strip() if needs_m else "—"
        needs = [] if needs_txt in ("—", "-", "") else [
            n.strip() for n in re.split(r"[,\s]+", needs_txt) if n.strip().startswith("T")
        ]

        pausas = [
            {"quando": p.group(1).strip(), "motivo": p.group(2).strip()}
            for p in RE_PAUSA.finditer(corpo)
        ]

        tasks.append(
            {
                "id": m.group(2),
                "feita": m.group(1).lower() == "x",
                "paralela": bool(m.group(3)),
                "needs": needs,
                "pausas": pausas,
            }
        )
    return {
        "tasks": tasks,
        "total": len(tasks),
        "feitas": sum(1 for t in tasks if t["feita"]),
    }


def secao_md(texto: str, titulo_parcial: str) -> str:
    """Conteúdo de uma seção `## Titulo` até o próximo `##`."""
    marcas = list(re.finditer(r"^##\s+(.+?)\s*$", texto, re.MULTILINE))
    for i, m in enumerate(marcas):
        if titulo_parcial.lower() in m.group(1).lower():
            fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
            return texto[m.end():fim]
    return ""


def parse_manifesto(texto: str) -> dict:
    """Lê só a tabela da seção `## Fatias`.

    O manifesto tem outras tabelas — critérios de aceite do conjunto, rollup de
    marcos, fechamento. Varrer o arquivo inteiro faria cada linha delas virar uma
    'fatia' inexistente, e o conjunto seria reportado como incoerente, travando a
    orquestração de qualquer decomposição gerada pelo template completo.
    """
    fatias, ondas = [], {}
    bloco_fatias = secao_md(texto, "Fatias") or texto
    dentro_tabela = False
    for m in RE_LINHA_FATIA.finditer(bloco_fatias):
        primeiro = m.group(1).strip()
        resto = [c.strip() for c in m.group(2).split("|")]
        if primeiro.lower().startswith("fatia") or set(primeiro) <= {"-", ":"}:
            dentro_tabela = True
            continue
        if not dentro_tabela or len(resto) < 3:
            continue
        needs_txt = resto[-2] if len(resto) >= 2 else "—"
        needs = [n for n in RE_ID_CRASE.findall(needs_txt)] or (
            [] if needs_txt.strip() in ("—", "-", "") else
            [n.strip() for n in needs_txt.split(",") if n.strip()]
        )
        fatias.append({"slug": primeiro, "needs": needs})

    for m in RE_ONDA.finditer(texto):
        ondas[int(m.group(1))] = RE_ID_CRASE.findall(m.group(2))

    return {"fatias": fatias, "ondas": ondas}


# ------------------------------------------------------------------ agregação


def estado_fatia(dados_tasks: dict) -> str:
    total, feitas = dados_tasks["total"], dados_tasks["feitas"]
    if total and feitas == total:
        return "concluida"
    tem_pausa = any(t["pausas"] and not t["feita"] for t in dados_tasks["tasks"])
    return "pausada" if tem_pausa else "pendente"


def carrega_bundle(dir_bundle: Path) -> dict:
    faltando = [a for a in ARQUIVOS_BUNDLE if not (dir_bundle / a).is_file()]
    spec = frontmatter(ler(dir_bundle / "SPEC.md"))
    plan = frontmatter(ler(dir_bundle / "PLAN.md"))
    tasks_txt = ler(dir_bundle / "TASKS.md")
    tk = frontmatter(tasks_txt)
    dados_tasks = parse_tasks(tasks_txt)

    return {
        "slug": dir_bundle.name,
        "dir": str(dir_bundle),
        "arquivos_faltando": faltando,
        "status": spec.get("status", "?"),
        "status_plan": plan.get("status", "?"),
        "status_tasks": tk.get("plan_status", "?"),
        "prd": spec.get("prd", "none"),
        "tasks_total": dados_tasks["total"],
        "tasks_feitas": dados_tasks["feitas"],
        "estado": estado_fatia(dados_tasks),
        "pausas_abertas": [
            {"task": t["id"], **t["pausas"][-1]}
            for t in dados_tasks["tasks"]
            if t["pausas"] and not t["feita"]
        ],
        "_tasks": dados_tasks["tasks"],
    }


def checa_incoerencias(conjunto: dict, bundles: dict) -> list:
    out = []
    for b in bundles.values():
        if b["arquivos_faltando"]:
            out.append({
                "tipo": "bundle-incompleto",
                "detalhe": f"{b['slug']}: falta {', '.join(b['arquivos_faltando'])}",
            })
        statuses = {b["status"], b["status_plan"], b["status_tasks"]} - {"?"}
        if len(statuses) > 1:
            out.append({
                "tipo": "status-divergente",
                "detalhe": f"{b['slug']}: SPEC/PLAN/TASKS em {sorted(statuses)}",
            })
        if b["status"] == "concluido" and b["tasks_feitas"] < b["tasks_total"]:
            out.append({
                "tipo": "concluido-com-task-aberta",
                "detalhe": f"{b['slug']}: {b['tasks_feitas']}/{b['tasks_total']} tasks",
            })
        ids = {t["id"] for t in b["_tasks"]}
        for t in b["_tasks"]:
            for n in t["needs"]:
                if n not in ids:
                    out.append({
                        "tipo": "needs-inexistente",
                        "detalhe": f"{b['slug']}/{t['id']} precisa de {n}, que não existe",
                    })

    if conjunto.get("manifesto"):
        declaradas = {f["slug"] for f in conjunto["fatias_manifesto"]}
        no_disco = set(bundles)
        for ausente in sorted(declaradas - no_disco):
            out.append({
                "tipo": "fatia-sem-diretorio",
                "detalhe": f"manifesto lista {ausente}, sem bundle no disco",
            })
        for extra in sorted(no_disco - declaradas):
            out.append({
                "tipo": "fatia-fora-do-manifesto",
                "detalhe": f"{extra} existe no disco e não está no manifesto",
            })
        for f in conjunto["fatias_manifesto"]:
            for n in f["needs"]:
                if n not in declaradas:
                    out.append({
                        "tipo": "needs-de-fatia-inexistente",
                        "detalhe": f"{f['slug']} precisa de {n}, ausente do manifesto",
                    })
        abertas = [s for s, b in bundles.items() if b["estado"] != "concluida"]
        if conjunto.get("status_manifesto") == "concluido" and abertas:
            out.append({
                "tipo": "manifesto-concluido-com-fatia-aberta",
                "detalhe": f"fatias abertas: {', '.join(sorted(abertas))}",
            })
    return out


def ondas_elegiveis(conjunto: dict, bundles: dict) -> list:
    """Fatia elegível = pendente e com todas as needs concluídas."""
    concluidas = {s for s, b in bundles.items() if b["estado"] == "concluida"}
    elegiveis, bloqueadas = [], []
    for f in conjunto["fatias_manifesto"]:
        b = bundles.get(f["slug"])
        if not b or b["estado"] == "concluida":
            continue
        pendencias = [n for n in f["needs"] if n not in concluidas]
        if pendencias:
            bloqueadas.append({"slug": f["slug"], "esperando": pendencias})
        elif b["estado"] == "pendente":
            elegiveis.append(f["slug"])
    return elegiveis, bloqueadas


def sugere_modo(conjuntos: list, git_info: dict) -> tuple[str, str]:
    if not conjuntos:
        return "preparar", "não há bundle em ./.aidev/ — o ciclo começa pela preparação"

    for c in conjuntos:
        if c["incoerencias"]:
            return "preparar", (
                f"estado incoerente em {c['base']} "
                f"({c['incoerencias'][0]['tipo']}) — reconcilie antes de executar"
            )

    for c in conjuntos:
        if c.get("manifesto"):
            if git_info.get("is_repo") and not git_info.get("bundle_commitado"):
                return "preparar", (
                    "há manifesto mas o bundle não está commitado — "
                    "o worktree nasce do HEAD e não enxergaria os arquivos"
                )
            if c["ondas_elegiveis"]:
                return "orquestrar", (
                    f"{len(c['ondas_elegiveis'])} fatia(s) elegível(is) em {c['base']}: "
                    f"{', '.join(c['ondas_elegiveis'])}"
                )

    abertas = [
        b for c in conjuntos for b in c["bundles"]
        if b["estado"] in ("pendente", "pausada")
    ]
    if abertas:
        b = abertas[0]
        if b["estado"] == "pausada":
            return "implementar", (
                f"{b['slug']} pausada em {b['pausas_abertas'][0]['task']} "
                f"({b['pausas_abertas'][0]['motivo']}) — retomar"
            )
        return "implementar", f"{b['slug']} com {b['tasks_total'] - b['tasks_feitas']} task(s) aberta(s)"

    nao_fechados = [
        b for c in conjuntos for b in c["bundles"] if b["status"] != "concluido"
    ]
    if nao_fechados:
        return "validar", (
            f"todas as tasks concluídas em {len(nao_fechados)} bundle(s); "
            "falta validar e fechar"
        )
    return "nenhum", "todos os bundles fechados — ciclo completo"


# ------------------------------------------------------------------------ main


def coleta(root: Path, filtro_slug: str | None) -> dict:
    aidev = root / ".aidev"
    git_info = estado_git(root, ".aidev")

    if not aidev.is_dir():
        modo, motivo = ("preparar", "não existe ./.aidev/ neste projeto")
        return {
            "root": str(root), "aidev_existe": False, "git": git_info,
            "conjuntos": [], "modo_sugerido": modo, "motivo_modo": motivo,
        }

    dirs = sorted(d for d in aidev.iterdir() if d.is_dir() and not d.name.startswith("."))
    manifestos = sorted(aidev.glob("*-manifest.md"))

    conjuntos, usados = [], set()
    for man in manifestos:
        base = man.name[: -len("-manifest.md")]
        if filtro_slug and filtro_slug not in (base, man.name):
            continue
        texto = ler(man)
        parsed = parse_manifesto(texto)
        fm = frontmatter(texto)
        membros = [d for d in dirs if d.name == base or d.name.startswith(base + "-")]
        usados.update(d.name for d in membros)
        bundles = {d.name: carrega_bundle(d) for d in membros}

        conj = {
            "base": base,
            "manifesto": str(man),
            "status_manifesto": fm.get("status", "aberto"),
            "prd": fm.get("prd", "none"),
            "fatias_manifesto": parsed["fatias"],
            "ondas_declaradas": parsed["ondas"],
            "bundles": list(bundles.values()),
        }
        conj["incoerencias"] = checa_incoerencias(conj, bundles)
        eleg, bloq = ondas_elegiveis(conj, bundles)
        conj["ondas_elegiveis"], conj["bloqueadas"] = eleg, bloq
        conjuntos.append(conj)

    for d in dirs:
        if d.name in usados:
            continue
        if filtro_slug and filtro_slug != d.name:
            continue
        b = carrega_bundle(d)
        conj = {
            "base": d.name, "manifesto": None, "status_manifesto": None,
            "prd": b["prd"], "fatias_manifesto": [], "ondas_declaradas": {},
            "bundles": [b], "ondas_elegiveis": [], "bloqueadas": [],
        }
        conj["incoerencias"] = checa_incoerencias(conj, {d.name: b})
        conjuntos.append(conj)

    for c in conjuntos:
        for b in c["bundles"]:
            b.pop("_tasks", None)

    modo, motivo = sugere_modo(conjuntos, git_info)
    return {
        "root": str(root), "aidev_existe": True, "git": git_info,
        "conjuntos": conjuntos, "modo_sugerido": modo, "motivo_modo": motivo,
    }


def resumo_texto(estado: dict) -> str:
    linhas = [f"Modo sugerido: {estado['modo_sugerido']} — {estado['motivo_modo']}"]
    g = estado["git"]
    if g.get("is_repo"):
        linhas.append(
            f"Git: {g['branch']} | working tree {'limpo' if g['clean'] else 'sujo'} "
            f"| bundle {'commitado' if g['bundle_commitado'] else 'NÃO commitado'}"
        )
    for c in estado["conjuntos"]:
        tipo = "conjunto" if c["manifesto"] else "bundle único"
        linhas.append(f"\n{tipo}: {c['base']}")
        for b in c["bundles"]:
            pausa = f" [{b['pausas_abertas'][0]['motivo']}]" if b["pausas_abertas"] else ""
            linhas.append(
                f"  {b['slug']:<40} {b['estado']:<10} "
                f"{b['tasks_feitas']}/{b['tasks_total']} tasks  status={b['status']}{pausa}"
            )
        if c["ondas_elegiveis"]:
            linhas.append(f"  onda elegível: {', '.join(c['ondas_elegiveis'])}")
        for bl in c["bloqueadas"]:
            linhas.append(f"  bloqueada: {bl['slug']} espera {', '.join(bl['esperando'])}")
        for inc in c["incoerencias"]:
            linhas.append(f"  INCOERÊNCIA [{inc['tipo']}] {inc['detalhe']}")
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="raiz do projeto alvo (default: .)")
    ap.add_argument("--slug", default=None, help="limita a um conjunto/bundle")
    ap.add_argument("--resumo", action="store_true", help="texto curto em vez de JSON")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"erro: {root} não é um diretório", file=sys.stderr)
        return 2

    estado = coleta(root, args.slug)
    print(resumo_texto(estado) if args.resumo else json.dumps(estado, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
