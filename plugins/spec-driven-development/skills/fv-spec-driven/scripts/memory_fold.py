#!/usr/bin/env python3
"""Consolida a memória por fatia em docs/MEMORY.md, de forma idempotente.

Por que existe. Durante a execução paralela, cada fatia roda num worktree próprio
e escreve memória. Se todas escrevessem em `docs/MEMORY.md`, esse seria o único
arquivo NÃO-disjunto entre fatias — e o merge da onda conflitaria sempre, com o
orquestrador culpando o corte da decomposição por algo que o próprio framework
causou. Se nenhuma escrevesse, o worktree terminaria sujo e `git worktree remove`
falharia.

A saída: cada fatia escreve em `docs/.memory/{fatia}.md` (caminho disjunto, merge
trivial) e a onda consolida aqui, num passo separado do merge de branch.

Seções acumulativas (Decisões, Lições, Deferidos, Bloqueios resolvidos) são
unidas com deduplicação — rodar duas vezes não duplica nada. `Sessão atual` é
singleton por natureza: N fatias, um slot. A política é manter uma linha por
fatia que ficou pausada (é contexto de retomada) e descartar as concluídas.

Uso:
    python3 memory_fold.py                      # consolida docs/.memory/*.md
    python3 memory_fold.py --manter-fontes      # não apaga os arquivos por fatia
    python3 memory_fold.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ACUMULATIVAS = ["Decisões", "Lições", "Deferidos", "Bloqueios resolvidos"]
SINGLETON = "Sessão atual"
ORDEM = [SINGLETON] + ACUMULATIVAS

CABECALHO = """# MEMORY — {projeto}

Memória de projeto. Consolidada pela skill `fv-spec-driven` ao fim de cada onda
de execução e ao fim de cada cadeia de tasks.
"""


def secoes(texto: str) -> dict[str, list[str]]:
    """Quebra um markdown em {titulo_h2: [linhas]}. Conteúdo antes do 1º h2 é ignorado."""
    out, atual = {}, None
    for linha in texto.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", linha)
        if m:
            atual = m.group(1).strip()
            out.setdefault(atual, [])
            continue
        if atual is not None:
            out[atual].append(linha)
    return out


RE_BULLET = re.compile(r"^\s*[-*]\s+\S")


def itens(linhas: list[str]) -> list[str]:
    """Só as linhas de bullet, normalizadas — prosa de instrução e régua `---` ficam de fora.

    O bullet exige separador (`- texto`), o que naturalmente exclui a régua
    horizontal `---` que separa as seções do arquivo consolidado. Sem isso, um
    re-fold engoliria a própria régua como item e a duplicaria a cada rodada.
    """
    return [l.rstrip() for l in linhas if RE_BULLET.match(l)]


def chave(item: str) -> str:
    return re.sub(r"\s+", " ", item.strip().lstrip("-*").strip()).lower()


def eh_placeholder(item: str) -> bool:
    """Bullets do template ('- **[YYYY-MM-DD]** — [decisão]') não entram na consolidação."""
    corpo = item.strip().lstrip("-*").strip()
    return corpo.startswith("[") and corpo.endswith("]") or "[YYYY-MM-DD]" in corpo


def consolida(destino_txt: str, fontes: dict[str, str], projeto: str) -> tuple[str, dict]:
    base = secoes(destino_txt) if destino_txt.strip() else {}
    stats = {"adicionados": {}, "ignorados_duplicados": 0, "sessoes": []}

    acumulado: dict[str, list[str]] = {}
    for sec in ACUMULATIVAS:
        vistos, saida = set(), []
        for item in itens(base.get(sec, [])):
            if eh_placeholder(item):
                continue
            k = chave(item)
            if k not in vistos:
                vistos.add(k)
                saida.append(item)
        antes = len(saida)
        for fatia in sorted(fontes):
            for item in itens(secoes(fontes[fatia]).get(sec, [])):
                if eh_placeholder(item):
                    continue
                k = chave(item)
                if k in vistos:
                    stats["ignorados_duplicados"] += 1
                    continue
                vistos.add(k)
                saida.append(item)
        acumulado[sec] = saida
        stats["adicionados"][sec] = len(saida) - antes

    # Sessão atual: uma linha por fatia com pausa aberta.
    sessao = []
    for fatia in sorted(fontes):
        bloco = secoes(fontes[fatia]).get(SINGLETON, [])
        texto = "\n".join(bloco)
        pausa = re.search(r"\*\*Motivo da pausa:\*\*\s*(.+)", texto)
        task = re.search(r"\*\*Última task concluída:\*\*\s*(.+)", texto)
        motivo = (pausa.group(1).strip() if pausa else "—")
        if motivo in ("—", "-", ""):
            continue
        sessao.append(
            f"- **{fatia}** — pausada em {motivo}. "
            f"Última task concluída: {task.group(1).strip() if task else '—'}."
        )
        stats["sessoes"].append(fatia)

    partes = [CABECALHO.format(projeto=projeto).rstrip(), ""]
    partes += ["---", "", f"## {SINGLETON}", ""]
    partes += sessao if sessao else ["Nenhuma fatia pausada."]
    for sec in ACUMULATIVAS:
        partes += ["", "---", "", f"## {sec}", ""]
        partes += acumulado[sec] if acumulado[sec] else ["_(vazio)_"]
    return "\n".join(partes).rstrip() + "\n", stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=".", help="raiz do projeto alvo")
    ap.add_argument("--origem", default="docs/.memory", help="diretório das memórias por fatia")
    ap.add_argument("--destino", default="docs/MEMORY.md", help="arquivo consolidado")
    ap.add_argument("--manter-fontes", action="store_true", help="não remove os arquivos por fatia")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    origem, destino = root / args.origem, root / args.destino

    if not origem.is_dir():
        print(json.dumps({
            "ok": True, "nada_a_fazer": True,
            "motivo": f"{args.origem} não existe — nenhuma memória por fatia a consolidar",
        }, indent=2, ensure_ascii=False))
        return 0

    arquivos = sorted(p for p in origem.glob("*.md") if p.is_file())
    if not arquivos:
        print(json.dumps({"ok": True, "nada_a_fazer": True, "motivo": f"{args.origem} vazio"},
                         indent=2, ensure_ascii=False))
        return 0

    fontes = {p.stem: p.read_text(encoding="utf-8") for p in arquivos}
    destino_txt = destino.read_text(encoding="utf-8") if destino.is_file() else ""
    novo, stats = consolida(destino_txt, fontes, root.name)

    removidos = []
    if not args.dry_run:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(novo, encoding="utf-8")
        if not args.manter_fontes:
            for p in arquivos:
                p.unlink()
                removidos.append(str(p.relative_to(root)))
            try:
                origem.rmdir()
            except OSError:
                pass

    print(json.dumps({
        "ok": True,
        "dry_run": args.dry_run,
        "destino": str(destino.relative_to(root)),
        "fatias_consolidadas": sorted(fontes),
        "itens_novos_por_secao": stats["adicionados"],
        "duplicados_ignorados": stats["ignorados_duplicados"],
        "fatias_pausadas_em_sessao_atual": stats["sessoes"],
        "fontes_removidas": removidos,
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
