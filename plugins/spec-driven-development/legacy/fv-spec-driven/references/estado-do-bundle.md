# Estado do bundle — máquina de estados e transições

Este arquivo é a autoridade sobre **em que estado cada artefato pode estar** e
**quem promove cada transição**. Antes desta skill, o ciclo tinha quatro donos
diferentes e três transições sem dono nenhum — o resultado era vocabulário de
status declarado nos templates e nunca escrito, e um PRD que fechava cedo demais
e trancava as fatias irmãs.

Transição de status **não é feita por edição direta de frontmatter**. Use:

```bash
python3 scripts/transicao.py --help
```

O script carrega as guardas descritas aqui. Editar o YAML na mão contorna a guarda
mais importante do ciclo (fechamento do conjunto) sem nenhum aviso.

## Os quatro artefatos com estado

| Artefato | Campo | Valores |
|---|---|---|
| `SPEC.md` | `status` | `rascunho` → `pronto` → `em-execucao` → `concluido` |
| `PLAN.md` | `status` | idem |
| `TASKS.md` | `plan_status` | idem (espelha o PLAN) |
| `{base}-manifest.md` | `status` | `aberto` → `concluido` |
| PRD (externo) | `status` | `rascunho` → `pronto` → `em-progresso` → `concluido` |

Os três arquivos do bundle andam **juntos**, sempre. Estado divergente entre eles
é incoerência estrutural, não um estado válido — `bundle_state.py` reporta.

## Quem promove o quê

| Transição | Modo | Quando |
|---|---|---|
| bundle → `pronto` | Preparar | ao gravar o bundle com o corte aprovado |
| PRD `rascunho` → `pronto` | Preparar | ao aprovar o corte, **com aval do usuário** |
| bundle → `em-execucao` | Implementar | antes da primeira task da cadeia |
| PRD `pronto` → `em-progresso` | Implementar | antes da primeira task da cadeia |
| bundle → `concluido` | Validar | sem divergência grande em aberto |
| manifesto → `concluido` | Validar | quando **todas** as fatias estão `concluido` |
| PRD → `concluido` | Validar | junto com o manifesto, nunca antes |

Duas dessas linhas não existiam e são a razão de este arquivo existir.

**`rascunho → pronto` do PRD.** Ficava órfã: `escrever-prd` salva sempre em
`rascunho` e delega a promoção a "skills de planejamento"; nenhuma promovia. Na
prática todo PRD ficava em rascunho para sempre, e o usuário levava um alerta na
preparação e uma confirmação na implementação, em todo ciclo. O modo Preparar
agora fecha isso: quando o corte é aprovado, o PRD foi lido e revisado o
suficiente para deixar de ser rascunho. Peça o aval — é status do artefato de
outra skill — mas ofereça a promoção em vez de deixar o usuário editar YAML na mão.

**`pronto → em-execucao` do bundle.** Ninguém escrevia. O vocabulário existia nos
três templates e nenhum valor intermediário era usado, então não havia como
distinguir "preparado mas não começado" de "em execução" sem abrir o `TASKS.md` e
contar `[X]`. O modo Implementar agora promove antes da primeira task.

## A guarda de fechamento

É a regra mais importante do arquivo, e a que mais custa quando falha.

> **PRD e manifesto só fecham quando a última fatia fecha.**

Com uma decomposição de N fatias, a validação roda **uma vez por fatia**. Se o
fechamento do PRD acontecesse junto com o fechamento do primeiro bundle:

- PRD `concluido` é **imutável** por princípio — `escrever-prd` não o evolui.
- O modo Implementar **aborta** com PRD `concluido`.
- O modo Preparar **recusa reconciliar** com PRD `concluido`.

Ou seja: bastaria a fatia 1 fechar para as fatias 2..N ficarem impedidas de
retomar, reconciliar ou corrigir gap. A saída documentada seria abrir um PRD novo
— para uma feature que estava no meio.

`transicao.py --fechar-bundle {slug}` fecha o bundle e então **verifica o
manifesto**. Se ainda há fatia aberta, ele fecha só o bundle e reporta quais
faltam. Se era a última, fecha o manifesto e o PRD na mesma operação.

Sem manifesto (decomposição de 1 fatia), fechar o bundle fecha o PRD direto —
não há conjunto a esperar.

## Estados derivados (não moram em frontmatter)

Nem tudo que o ciclo precisa saber é status. Estes são **calculados** a partir do
`TASKS.md` e do manifesto por `bundle_state.py`, e por isso nunca dessincronizam:

| Estado derivado | Como sai |
|---|---|
| fatia **concluída** | todas as tasks `[X]` |
| fatia **pausada** | há bloco `> Pausa em ...` aberto na última task tocada |
| fatia **pendente** | há task `[ ]` e nenhuma pausa aberta |
| fatia **bloqueada** | pendente, mas alguma `needs:` não concluiu |
| **onda elegível** | fatias pendentes cujas `needs` estão todas concluídas |

A tentação de gravar isso em frontmatter é forte e é um erro: seria um segundo
lugar para a mesma verdade, e o `TASKS.md` já é o registro que a execução atualiza
a cada task. Estado derivado se calcula; estado de ciclo de vida se grava.

## Incoerências que travam o ciclo

`bundle_state.py` reporta e **nenhum modo deve prosseguir** por cima delas — o
caminho é sempre reconciliar (modo Preparar):

- `status` divergente entre `SPEC.md`, `PLAN.md` e `TASKS.md` do mesmo bundle.
- Manifesto listando fatia sem diretório, ou diretório de fatia fora do manifesto.
- `needs:` (de task ou de fatia) apontando ID inexistente.
- Bundle `concluido` com task `[ ]` aberta.
- Manifesto `concluido` com fatia não-`concluido`.
- PRD `concluido` com bundle vivo apontando para ele.
