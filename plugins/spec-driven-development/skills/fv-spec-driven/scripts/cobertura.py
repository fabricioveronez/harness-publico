#!/usr/bin/env python3
"""Tabela de cobertura US × critério de aceite × task, a partir do bundle.

Antes desta skill, o gate final cruzava apenas US × task ("USs cobertas"). Isso
diz que alguém trabalhou na US, não que o comportamento foi provado: a US contava
como coberta mesmo com um bloco `Validação:` fraco. E a classificação de um
critério em automatizável ou manual era feita por regex sobre a prosa da coluna
"como verificar" — em dois lugares diferentes, cada um reinterpretando o mesmo
texto por conta própria.

Com os critérios declarados (`CA01`, nível, automatizável, alvo) na §5a do SPEC e
referenciados pelo ID no `Validação:` de cada task, a cobertura vira contagem, e
os dois consumidores (gate final do modo Implementar e modo Validar) passam a
executar o mesmo conjunto declarado.

Uso:
    python3 cobertura.py --bundle .aidev/003-toil-api
    python3 cobertura.py --bundle .aidev/003-toil-api --json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RE_US = re.compile(r"^###\s+(US\d+)\s*:?\s*(.*)$", re.MULTILINE)
RE_TASK = re.compile(r"^##\s*\[([ Xx])\]\s*(T\d+)\s*(?:\[P\])?\s*:\s*(.*)$", re.MULTILINE)
RE_USS_COBERTAS = re.compile(r"^\s*[-*]\s*\*\*USs?\s+cobertas?:\*\*\s*(.+)$", re.MULTILINE | re.IGNORECASE)
RE_ID_US = re.compile(r"US\d+")
RE_ID_CA = re.compile(r"CA\d+")
RE_LINHA_TABELA = re.compile(r"^\|(.+)\|\s*$", re.MULTILINE)
RE_SECAO = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)


def ler(p: Path) -> str:
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def secao(texto: str, titulo_parcial: str) -> str:
    marcas = list(RE_SECAO.finditer(texto))
    for i, m in enumerate(marcas):
        if titulo_parcial.lower() in m.group(1).lower():
            fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
            return texto[m.end():fim]
    return ""


def criterios_do_spec(spec_txt: str) -> tuple[list[dict], list[str]]:
    """Lê a tabela §5a. Aceita o formato declarativo e avisa quando é o legado."""
    bloco = secao(spec_txt, "Critérios de Aceite")
    avisos, criterios = [], []
    if not bloco.strip():
        return [], ["SPEC sem seção 'Critérios de Aceite'"]

    linhas = [m.group(1) for m in RE_LINHA_TABELA.finditer(bloco)]
    for linha in linhas:
        celulas = [c.strip() for c in linha.split("|")]
        if not celulas or set("".join(celulas)) <= {"-", ":", " "}:
            continue
        if celulas[0].lower() in ("id", "critério", "criterio"):
            continue
        m = RE_ID_CA.match(celulas[0].replace("`", ""))
        if not m:
            avisos.append(
                f"linha sem ID de critério: «{celulas[0][:60]}» — "
                "formato legado; declare IDs CA01.. para cobertura verificável"
            )
            continue
        criterios.append({
            "id": m.group(0),
            "criterio": celulas[1] if len(celulas) > 1 else "",
            "nivel": (celulas[2] if len(celulas) > 2 else "").lower(),
            "automatizavel": (celulas[3] if len(celulas) > 3 else "").lower().startswith(("s", "y", "t")),
            "alvo": celulas[4].strip("`") if len(celulas) > 4 else "",
        })
    if not criterios and not avisos:
        avisos.append("tabela de critérios vazia")
    return criterios, avisos


def tasks_do_bundle(tasks_txt: str) -> list[dict]:
    marcas = list(RE_TASK.finditer(tasks_txt))
    out = []
    for i, m in enumerate(marcas):
        corpo = tasks_txt[m.end(): marcas[i + 1].start() if i + 1 < len(marcas) else len(tasks_txt)]
        uss = RE_USS_COBERTAS.search(corpo)
        bloco_val = corpo.split("**Validação:**", 1)[1] if "**Validação:**" in corpo else ""
        out.append({
            "id": m.group(2),
            "titulo": m.group(3).strip(),
            "feita": m.group(1).lower() == "x",
            "uss": RE_ID_US.findall(uss.group(1)) if uss else [],
            "cas": sorted(set(RE_ID_CA.findall(bloco_val))),
            "validacoes_marcadas": len(re.findall(r"-\s*\[[Xx]\]", bloco_val)),
            "validacoes_total": len(re.findall(r"-\s*\[[ Xx]\]", bloco_val)),
        })
    return out


def monta(bundle: Path) -> dict:
    spec_txt, tasks_txt = ler(bundle / "SPEC.md"), ler(bundle / "TASKS.md")
    if not spec_txt or not tasks_txt:
        return {"erro": f"bundle incompleto em {bundle} (falta SPEC.md ou TASKS.md)"}

    uss = [{"id": m.group(1), "titulo": m.group(2).strip()} for m in RE_US.finditer(spec_txt)]
    criterios, avisos = criterios_do_spec(spec_txt)
    tasks = tasks_do_bundle(tasks_txt)

    por_us = {u["id"]: [t["id"] for t in tasks if u["id"] in t["uss"]] for u in uss}
    por_ca = {c["id"]: [t["id"] for t in tasks if c["id"] in t["cas"]] for c in criterios}

    ids_us, ids_ca = {u["id"] for u in uss}, {c["id"] for c in criterios}
    lacunas = []
    for u in uss:
        if not por_us[u["id"]]:
            lacunas.append({"tipo": "us-sem-task", "id": u["id"], "detalhe": u["titulo"]})
    for c in criterios:
        if not por_ca[c["id"]]:
            lacunas.append({"tipo": "criterio-sem-task", "id": c["id"], "detalhe": c["criterio"]})
        if c["automatizavel"] and not c["alvo"]:
            lacunas.append({"tipo": "automatizavel-sem-alvo", "id": c["id"],
                            "detalhe": "declarado automatizável mas sem arquivo/comando alvo"})
    for t in tasks:
        for ref in t["uss"]:
            if ref not in ids_us:
                lacunas.append({"tipo": "task-referencia-us-inexistente", "id": t["id"], "detalhe": ref})
        for ref in t["cas"]:
            if ref not in ids_ca:
                lacunas.append({"tipo": "task-referencia-criterio-inexistente", "id": t["id"], "detalhe": ref})
        if not t["cas"]:
            lacunas.append({"tipo": "task-sem-criterio", "id": t["id"],
                            "detalhe": "bloco Validação não referencia nenhum CA"})

    automatizaveis = [c for c in criterios if c["automatizavel"]]
    return {
        "bundle": str(bundle),
        "uss": uss, "criterios": criterios, "tasks": tasks,
        "cobertura_us": por_us, "cobertura_criterio": por_ca,
        "resumo": {
            "uss_total": len(uss),
            "uss_cobertas": sum(1 for v in por_us.values() if v),
            "criterios_total": len(criterios),
            "criterios_cobertos": sum(1 for v in por_ca.values() if v),
            "criterios_automatizaveis": len(automatizaveis),
            "criterios_manuais": len(criterios) - len(automatizaveis),
            "tasks_total": len(tasks),
            "tasks_feitas": sum(1 for t in tasks if t["feita"]),
        },
        "lacunas": lacunas,
        "avisos": avisos,
        "comandos_sugeridos": sorted({c["alvo"] for c in automatizaveis if c["alvo"]}),
    }


def render(d: dict) -> str:
    r, linhas = d["resumo"], []
    linhas.append(f"Cobertura — {Path(d['bundle']).name}")
    linhas.append(
        f"US: {r['uss_cobertas']}/{r['uss_total']} | "
        f"Critérios: {r['criterios_cobertos']}/{r['criterios_total']} "
        f"({r['criterios_automatizaveis']} automatizáveis, {r['criterios_manuais']} manuais) | "
        f"Tasks: {r['tasks_feitas']}/{r['tasks_total']}"
    )
    linhas.append("")
    linhas.append("| US   | Tasks        | Critérios provados            | Status       |")
    linhas.append("|------|--------------|-------------------------------|--------------|")
    for u in d["uss"]:
        ts = d["cobertura_us"][u["id"]]
        cas = sorted({c for t in d["tasks"] if t["id"] in ts for c in t["cas"]})
        status = "coberta" if ts and cas else ("sem critério" if ts else "NÃO ENTREGUE")
        linhas.append(f"| {u['id']:<4} | {', '.join(ts) or '—':<12} | {', '.join(cas) or '—':<29} | {status:<12} |")

    linhas += ["", "| CA   | Nível        | Autom. | Alvo                          | Tasks    |",
               "|------|--------------|--------|-------------------------------|----------|"]
    for c in d["criterios"]:
        linhas.append(
            f"| {c['id']:<4} | {c['nivel'][:12]:<12} | {'sim' if c['automatizavel'] else 'não':<6} | "
            f"{c['alvo'][:29]:<29} | {', '.join(d['cobertura_criterio'][c['id']]) or '—':<8} |"
        )

    if d["lacunas"]:
        linhas += ["", f"Lacunas ({len(d['lacunas'])}):"]
        linhas += [f"  [{l['tipo']}] {l['id']} — {l['detalhe']}" for l in d["lacunas"]]
    else:
        linhas += ["", "Nenhuma lacuna de cobertura."]

    if d["avisos"]:
        linhas += ["", "Avisos:"] + [f"  {a}" for a in d["avisos"]]
    if d["comandos_sugeridos"]:
        linhas += ["", "Alvos automatizáveis a executar no gate:"]
        linhas += [f"  {c}" for c in d["comandos_sugeridos"]]
    return "\n".join(linhas)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", required=True, help="caminho do bundle (ex.: .aidev/003-toil-api)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    bundle = Path(args.bundle).resolve()
    if not bundle.is_dir():
        print(f"erro: bundle não encontrado: {bundle}", file=sys.stderr)
        return 2

    d = monta(bundle)
    if "erro" in d:
        print(f"erro: {d['erro']}", file=sys.stderr)
        return 2

    print(json.dumps(d, indent=2, ensure_ascii=False) if args.json else render(d))
    return 1 if d["lacunas"] else 0


if __name__ == "__main__":
    sys.exit(main())
