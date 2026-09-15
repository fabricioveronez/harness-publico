#!/usr/bin/env python3
"""Checa o que a decomposição pressupõe: disjunção real entre fatias e paralelismo efetivo.

As asserções de estrutura verificam que o bundle existe e está bem formado. Estas
verificam que a decomposição **serve**: que as fatias de uma onda são de fato
disjuntas (senão o merge conflita), que o paralelismo prometido existe, e que a
fonte foi coberta sem virar decisão silenciosa.

Uso: python3 paralelismo.py <projeto> [--fonte <doc-de-origem.md>]
"""
from __future__ import annotations
import argparse, itertools, json, re, sys
from pathlib import Path

MARCADORES = {"[NOVO]", "NOVO", "[novo]"}


def secao(texto: str, titulo: str) -> str:
    marcas = list(re.finditer(r"^#{2,3}\s+(.+?)\s*$", texto, re.M))
    for i, m in enumerate(marcas):
        if titulo.lower() in m.group(1).lower():
            fim = marcas[i + 1].start() if i + 1 < len(marcas) else len(texto)
            return texto[m.end():fim]
    return ""


def arquivos_afetados(plan: str) -> set[str]:
    sec = secao(plan, "Arquivos Afetados")
    return {a.strip() for a in re.findall(r"`([^`]+)`", sec)
            if a.strip() not in MARCADORES and ("/" in a or "." in a)}


def carrega(proj: Path) -> dict:
    aidev = proj / ".aidev"
    man = next(iter(aidev.glob("*-manifest.md")), None)
    if not man:
        return {"erro": "sem manifesto — decomposição de 1 fatia não tem o que checar aqui"}
    texto = man.read_text(encoding="utf-8")
    ondas = {int(m.group(1)): re.findall(r"`([\w.\-]+)`", m.group(2))
             for m in re.finditer(r"^[-*]\s*\*\*Onda\s+(\d+)\*\*[^:]*:\s*(.+)$", texto, re.M)}
    fatias = {}
    for fs in ondas.values():
        for s in fs:
            d = aidev / s
            if d.is_dir():
                fatias[s] = {
                    "arquivos": arquivos_afetados((d / "PLAN.md").read_text(encoding="utf-8")),
                    "spec": (d / "SPEC.md").read_text(encoding="utf-8"),
                }
    return {"manifesto": texto, "ondas": ondas, "fatias": fatias}


def itens_fonte(fonte: str) -> tuple[list[str], list[str], list[str]]:
    cap = [l.strip("-* ").strip() for l in secao(fonte, "Capacidades").splitlines()
           if l.strip().startswith(("-", "*")) and len(l.strip()) > 3]
    reg = [re.sub(r"^\d+\.\s*", "", l.strip()) for l in secao(fonte, "Regras de negócio").splitlines()
           if re.match(r"^\d+\.\s", l.strip())]
    pend = [m.group(1).strip() for m in
            re.finditer(r"^\*\*(.+?)\*\*\s*$", secao(fonte, "Pendências"), re.M)]
    return cap, reg, pend


def palavras_chave(frase: str, n: int = 4) -> list[str]:
    stop = {"o","a","os","as","um","uma","de","do","da","dos","das","e","que","para","em","no","na",
            "por","com","ao","à","se","não","nada","cada","sistema","precisa","permitir","ver","num"}
    ws = [w for w in re.findall(r"[a-zà-ú]{4,}", frase.lower()) if w not in stop]
    return ws[:n]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("projeto")
    ap.add_argument("--fonte", default=None)
    args = ap.parse_args()
    proj = Path(args.projeto).resolve()
    d = carrega(proj)
    if "erro" in d:
        print(json.dumps(d, ensure_ascii=False, indent=2)); return 2

    ondas, fatias = d["ondas"], d["fatias"]
    exp = []

    # 1. disjunção dentro da onda — a propriedade que o paralelismo pressupõe
    colisoes = []
    for n, fs in ondas.items():
        for a, b in itertools.combinations([f for f in fs if f in fatias], 2):
            inter = fatias[a]["arquivos"] & fatias[b]["arquivos"]
            if inter:
                colisoes.append({"onda": n, "par": [a, b], "arquivos": sorted(inter)})
    exp.append({"text": "fatias da mesma onda têm Arquivos Afetados disjuntos",
                "passed": not colisoes,
                "evidence": "0 colisões" if not colisoes else json.dumps(colisoes, ensure_ascii=False)})

    # 2. paralelismo efetivo
    pe = len(fatias) / len(ondas) if ondas else 0
    exp.append({"text": "paralelismo efetivo ≥ 1,5 (fatias por onda)",
                "passed": pe >= 1.5,
                "evidence": f"{len(fatias)} fatias em {len(ondas)} ondas = {pe:.2f}"})

    # 3./4. cobertura e pendências da fonte
    if args.fonte:
        fonte = Path(args.fonte).read_text(encoding="utf-8")
        cap, reg, pend = itens_fonte(fonte)
        corpo = " ".join(f["spec"] for f in fatias.values()).lower() + " " + d["manifesto"].lower()
        def coberto(item):
            ks = palavras_chave(item)
            return bool(ks) and sum(1 for k in ks if k in corpo) >= max(1, len(ks) // 2)
        n_cap = sum(1 for c in cap if coberto(c)); n_reg = sum(1 for r in reg if coberto(r))
        exp.append({"text": "capacidades e regras de negócio da fonte aparecem nos SPECs",
                    "passed": n_cap + n_reg >= 0.8 * (len(cap) + len(reg)),
                    "evidence": f"capacidades {n_cap}/{len(cap)}, regras {n_reg}/{len(reg)}"
                                + ("" if n_cap == len(cap) and n_reg == len(reg)
                                   else " | fora: " + "; ".join(
                                       [c[:45] for c in cap if not coberto(c)] +
                                       [r[:45] for r in reg if not coberto(r)])[:300])})
        n_pend = sum(1 for p in pend if coberto(p))
        exp.append({"text": "pendências da fonte foram preservadas (não decididas em silêncio)",
                    "passed": n_pend >= 0.5 * len(pend) if pend else True,
                    "evidence": f"{n_pend}/{len(pend)} pendências mencionadas nos artefatos"})

    ok = sum(1 for e in exp if e["passed"])
    print(f"Conteúdo — {proj.name}: {ok}/{len(exp)}\n")
    for e in exp:
        print(("  PASS " if e["passed"] else "  FAIL "), e["text"])
        print(f"         {e['evidence'][:300]}")
    return 0 if ok == len(exp) else 1


if __name__ == "__main__":
    sys.exit(main())
