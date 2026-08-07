# Template — MEMORY

Memória viva do projeto: decisões, lições, bloqueios e ideias diferidas que
atravessam features. Não substitui SPEC nem TRD — é insumo para features futuras
e contexto de retomada.

## Onde escrever

| Contexto | Arquivo |
|---|---|
| execução normal (bundle único) | `docs/MEMORY.md` |
| dentro de um worktree de fatia | `docs/.memory/{base}-{fatia}.md` |

O caminho por fatia existe porque `docs/MEMORY.md` seria o único arquivo
compartilhado por todas as fatias de uma onda — não-disjunto por construção — e
conflitaria em todo merge, fazendo a orquestração acusar corte ruim por algo que o
próprio fluxo causou. `scripts/memory_fold.py` consolida ao fim da onda.

**A memória entra no commit da task.** Fora do commit, ela deixa o working tree
sujo e a invocação seguinte pausa com `working-tree-sujo`; num worktree,
`git worktree remove` recusa sair sujo e a limpeza da onda quebra.

## Estrutura

```markdown
# MEMORY — [Nome do Projeto]

Memória de projeto. Consolidada pela skill `fv-spec-driven` ao fim de cada onda
de execução e ao fim de cada cadeia de tasks.

---

## Sessão atual

**Feature em andamento:** [slug do bundle, ou "—"]
**Última task concluída:** [TNN ou "—"]
**Motivo da pausa:** [vocabulário controlado, ou "—"]
**Atualizado em:** YYYY-MM-DD

---

## Decisões

Escolhas de arquitetura e abordagem com impacto **além** desta feature.

- **[YYYY-MM-DD] [slug]** — [decisão]. Motivo: [justificativa].

---

## Lições

O que repetir ou evitar em features futuras.

- **[YYYY-MM-DD]** — [lição].

---

## Deferidos

Ideias que surgiram fora do escopo. Cada uma pode virar PRD.

- **[slug-de-origem]** — [ideia detectada].

---

## Bloqueios resolvidos

Bloqueios que travaram a execução e como saíram. Evita repetir a investigação.

- **[YYYY-MM-DD] [motivo-de-pausa]** — [bloqueio]. Resolução: [como saiu].
```

## Regras

- **`Sessão atual` é singleton.** Na consolidação de uma onda, `memory_fold.py`
  mantém uma linha por fatia **pausada** (é contexto de retomada) e descarta as
  concluídas — N fatias não cabem num slot só.
- **`Decisões` acumula indefinidamente.** Nunca apague. Registre só o que tem
  impacto futuro; detalhe de implementação polui e afoga o que importa.
- **Datas absolutas** (`YYYY-MM-DD`). Nada de "ontem" ou "semana passada" — o
  arquivo precisa ser legível meses depois.
- **A consolidação deduplica por texto normalizado**, então duas fatias que
  registram a mesma decisão geram uma linha só, e rodar o fold duas vezes não
  duplica nada.
