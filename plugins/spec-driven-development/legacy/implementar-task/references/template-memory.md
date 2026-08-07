# Template MEMORY.md

Template canônico para `docs/MEMORY.md`. Criado pela skill `implementar-task`
na primeira pausa ou conclusão de feature, quando o arquivo ainda não existe.

O MEMORY.md é a memória viva do projeto — persiste decisões, bloqueios e
lições entre features e sessões. Não substitui PRDs nem TRD; é insumo para
features futuras.

---

## Estrutura do arquivo

```markdown
# MEMORY — [Nome do Projeto]

Memória de projeto. Atualizada pela skill `implementar-task` a cada pausa
e conclusão de feature.

---

## Sessão atual

**Feature em andamento:** [slug do PRD ou "—" quando ocioso]
**Última task concluída:** [TNN ou "—"]
**Motivo da pausa:** [vocabulário controlado ou "—"]
**Atualizado em:** YYYY-MM-DD

---

## Decisões

Escolhas de arquitetura e abordagem com impacto além da feature atual.
Registrar: a decisão, o motivo e o contexto em que foi tomada.

- **[YYYY-MM-DD] [slug-do-prd]** — [decisão tomada]. Motivo: [justificativa].
- **[YYYY-MM-DD] [slug-do-prd]** — [decisão tomada]. Motivo: [justificativa].

---

## Lições

O que não repetir (ou repetir) em features futuras. Registrar após conclusão
de features com aprendizados relevantes.

- **[YYYY-MM-DD]** — [lição aprendida].

---

## Deferidos

Ideias que surgiram durante a implementação mas estavam fora do escopo.
Cada item pode virar um PRD futuro.

- **[slug-de-origem]** — [ideia ou comportamento detectado fora do escopo].

---

## Bloqueios resolvidos

Bloqueios técnicos ou de informação que travaram a execução e como foram
resolvidos. Útil para evitar repetição.

- **[YYYY-MM-DD] [motivo-de-pausa]** — [descrição do bloqueio]. Resolução: [como foi resolvido].
```

---

## Regras de preenchimento

- **`## Sessão atual`** é limpa (`—`) após conclusão de feature. Contém
  informação apenas quando há feature em andamento ou pausada.
- **`## Decisões`** acumula indefinidamente — nunca apagar registros.
  Registrar apenas decisões com impacto em features futuras, não detalhes
  de implementação.
- **`## Lições`** é preenchida pela skill ao concluir o gate final. O
  usuário pode editar para refinar o texto.
- **`## Deferidos`** é preenchida durante execução quando a skill detecta
  escopo inesperado. O usuário decide o destino de cada item.
- **`## Bloqueios resolvidos`** é preenchida quando uma pausa é resolvida
  e a execução retoma com sucesso.
- Datas em formato `YYYY-MM-DD`. Sem data relativa ("ontem", "na semana
  passada") — o arquivo deve ser interpretável meses depois.
