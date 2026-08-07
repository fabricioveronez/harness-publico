# Modo Implementar — executar as tasks do bundle

Executa o `TASKS.md` de um bundle em cadeia automática. Para cada task elegível:
roda os passos, executa o bloco `Validação:`, e marca `[X]` se tudo passar. Em
falha, tenta corrigir em até 5 ciclos; se esgotar ou bater em lacuna do contrato,
pausa, registra nota e devolve controle.

O `SPEC.md` é o **contexto primário**. O PRD (quando existe) e o TRD são abertos
**sob demanda** — o PRD para o *porquê* de uma regra, o TRD para contexto técnico.

## 1. Abrir o bundle

Resolva o slug (argumento, ou `bundle_state.py` quando houver só um candidato).
Leia `SPEC.md`, `PLAN.md` e `TASKS.md` **integralmente**.

Valide o PRD **só quando `prd:` aponta um slug**:

- `concluido` → **abortar**. PRD concluído é imutável.
- `rascunho` → peça confirmação explícita; sem ela, aborte.
- `pronto` → promova via `transicao.py prd {slug} --para em-progresso`.
- `em-progresso` → siga.

Com `prd: none`, pule — o SPEC é a fonte de verdade.

Cheque a coerência estrutural: `prd:` consistente entre os três arquivos, IDs de
task sequenciais, todo `needs:` apontando ID existente, toda task com `Passos:` e
`Validação:` não-vazios, toda US citada existindo no SPEC, todo `CA` citado
existindo na tabela de critérios. Incoerência → pausa `incoerencia-estrutural` e
reconciliação no modo Preparar.

Localize `Comando de teste:` no PLAN. Se vier `Sem suíte de testes detectada`,
marque `sem_suite = true` e pule as otimizações de teste — o bloco `Validação:`
continua sendo o gate, e o commit por task continua saindo.

Cheque o working tree (`git status --porcelain`):

- **limpo** → siga;
- **sujo com mudanças fora do escopo da próxima task** → pausa `working-tree-sujo`.
  O usuário decide (commit à parte, stash, descarte) e reinvoca;
- **sujo só com arquivos do escopo** (retomada após pausa que deixou edição
  parcial) → siga; o commit da task consolida.

## 2. Avaliar skills relevantes

Antes da primeira task, infira os domínios do bundle a partir de "Arquivos
Afetados" e "Contexto Técnico Global" do PLAN (stack, framework, ferramentas de
teste) e carregue as skills do catálogo atual que claramente cobrem esse trabalho
— boas práticas da linguagem, padrão de testes, um serviço citado.

Resolva isso **em execução-time, a cada invocação**, e não grave a lista em lugar
nenhum. Uma lista gravada envelhece contra o catálogo, que muda por conta própria.
E como cada subagente de uma onda paralela roda este passo no **seu** bundle, cada
um carrega o que o seu escopo precisa, sem depender de acordar no contexto certo.

Se nada casar, siga sem carga adicional. É sugestão, não trava.

## 3. Linha de base verde

Com `sem_suite = false`, rode a suíte completa antes da próxima task. Vermelho →
pausa `falha-pre-existente`. Falha que já existia contamina o diagnóstico dos
ciclos de correção — você passaria 5 ciclos consertando algo que não quebrou aqui.

Promova o bundle na primeira task da cadeia:

```bash
python3 scripts/transicao.py bundle {slug} --para em-execucao
```

## 4. Selecionar a próxima task

Elegível = task `[ ]` cujo `needs:` está todo `[X]`, ou é `—`.

- Nenhuma elegível → gate final (passo 8).
- Grupo de tasks `[P]` elegíveis → execute o grupo antes das dependentes; cada uma
  gera seu próprio commit. Se qualquer uma do grupo pausa, a cadeia pausa — não
  inicie dependentes de grupo incompleto.
- Task simples → siga.

## 5. Executar os passos

Para cada passo `[ ]`, na ordem: execute a ação, marque `[X]`. Com suíte, tente
inferir o teste associado ao passo (cascata na seção 1 de
`heuristicas-execucao.md`) e rode só ele — verde segue, vermelho vai direto ao
loop de correção. Sem casamento, siga sem rodar nada.

Se a execução exigir uma **decisão de negócio que o contrato não cobre**, pare
naquele passo (sem marcá-lo) e vá para a pausa. Não preencha em silêncio, não
assuma intenção, e **não infira regra de negócio a partir do código existente** —
código é implementação de uma decisão; a decisão mora no contrato.

## 6. Validar a task

Execute cada item do bloco `Validação:`. Os itens referenciam critérios por ID
(`CA01`); o nível e o alvo estão declarados na tabela §5a do SPEC, então não há o
que interpretar — rode o alvo.

Todos `[X]` → marque o título da task, **crie o commit** e volte ao passo 4.
Algum falha → loop de correção. Não marque, não commite.

## 7. Loop de correção (5 ciclos)

Um ciclo = analisar erro → aplicar correção → re-executar a validação que falhou
com filtro seletivo (seção 2 de `heuristicas-execucao.md`).

- **Verde no seletivo** → rode a suíte completa **uma vez** como gate. Verde: marque
  o item e siga. Vermelho: `regressao-fora-escopo`, **sem consumir ciclo**, pausa.
- **Vermelho no seletivo** → consome 1 ciclo. Esgotou os 5 → pausa
  `esgotamento-ciclos`.

Cada ciclo começa lendo o erro atual e os diffs das tentativas anteriores **na
mesma task**. Não repita correção já tentada. Se perceber que está variando a
mesma estratégia só na estética (renomear, reorganizar sem mudar lógica), é loop
estéril — pause com `esgotamento-ciclos` antes do 5º ciclo. Insistir custa mais
que devolver o controle.

Detecções que **não consomem ciclo**, porque não são problema do código da task:

| Sinal | Motivo da pausa |
|---|---|
| comando ausente, timeout do runner, permissão negada | `infra-erro-fatal` |
| validação alternando passa/falha em ≥2 ciclos com mesmo input | `flaky-detectado` |
| a correção exigiria editar PLAN/TASKS estruturalmente | `incoerencia-estrutural` |

## 8. Gate final

Quando não há mais task elegível:

```bash
python3 scripts/cobertura.py --bundle .aidev/{slug}
```

Ele cruza US × critério × task e lista os alvos automatizáveis. Execute esses
alvos e reporte `OK | FALHA | ERRO_DE_EXECUÇÃO`; liste os critérios manuais como
verificação sugerida ao usuário.

US sem task associada, ou task sem critério referenciado, é lacuna de planejamento
— reporte antes de considerar a cadeia concluída.

Atualize a memória (passo 10) e devolva o controle. **O gate não fecha nada**: a
promoção para `concluido` é do modo Validar, que carrega a guarda do conjunto.

## 9. Pausa

Todo motivo vem do vocabulário controlado — nunca texto livre. É o que permite ao
relatório e à retomada serem lidos por máquina:

`esgotamento-ciclos` · `lacuna-spec` · `interrupcao-manual` ·
`regressao-fora-escopo` · `infra-erro-fatal` · `flaky-detectado` ·
`incoerencia-estrutural` · `falha-pre-existente` · `falha-commit` ·
`working-tree-sujo`

Protocolo: preserve todos os `[X]`; **não** marque o título; capture o snapshot de
drift (seção 4 de `heuristicas-execucao.md`); registre o bloco no `TASKS.md`
conforme `templates/template-nota-pausa.md` — notas são **acumulativas**, nunca
sobrescreva a anterior; atualize a memória; pause a cadeia inteira.

### Lacuna no contrato

Lacuna é: Rule que referencia comportamento ausente do SPEC, Edge case que
contradiz o estado real do código, ou validação que exige decisão de negócio não
documentada. **Não** é preferência estilística nem dúvida técnica menor — só
quando continuar exigiria inventar regra de negócio.

Ao detectar, pause com `lacuna-spec` e ofereça: com PRD, ajustar via
`escrever-prd` e reconciliar; sem PRD, ajustar o SPEC no modo Preparar;
reconciliar PLAN+TASKS quando a lacuna afeta escopo; ou decidir inline, com a
premissa registrada na nota (`> Premissa registrada inline: ...`).

Este modo **não edita** SPEC nem PRD para suprir lacuna, em nenhuma hipótese.

## 10. Memória

Onde escrever depende de onde você está rodando:

| Contexto | Arquivo |
|---|---|
| bundle único, execução normal | `docs/MEMORY.md` |
| dentro de um worktree de fatia (onda paralela) | `docs/.memory/{base}-{fatia}.md` |

O caminho por fatia é o que mantém as fatias disjuntas — `docs/MEMORY.md` seria o
único arquivo compartilhado por todas, e conflitaria em todo merge de onda. A
consolidação acontece depois, no modo Orquestrar, via `memory_fold.py`.

**A memória entra no commit da task.** Isso não é detalhe: memória escrita e não
commitada deixa o working tree sujo, e a invocação seguinte pausa com
`working-tree-sujo` por um arquivo que o próprio fluxo criou — um laço que só sai
com commit manual. Num worktree, o efeito é pior: `git worktree remove` recusa
sair sujo e a limpeza da onda quebra.

Estrutura em `templates/template-memory.md`. Registre em `## Decisões` só o que
tem impacto além desta feature; detalhe de implementação polui.

## 11. Retomada

Detectada automaticamente quando o bundle já tem progresso.

1. Aplique a detecção de drift (seção 4 de `heuristicas-execucao.md`). Drift no
   SPEC ou no PRD **interrompe antes de tudo** — reconcilie primeiro.
2. Carregue a memória; `## Sessão atual` dá o contexto da pausa sem reler tudo.
3. Mostre as notas de pausa anteriores como contexto. Nunca as apague.
4. Pergunte se retoma do ponto exato ou revisa o contrato antes.
5. Confirmado: re-execute a linha de base verde e siga do passo 4.
6. Se todas as tasks já estão `[X]`, vá direto ao gate final.

## Commit por task

Toda task com passos, validações e título `[X]` gera **um** commit:

```
<tipo>(<slug>): <título em minúsculo> [T{NN}]
```

Tipo vem do campo `**Nível:**` (tabela na seção 5 de `heuristicas-execucao.md`);
sem casamento, `chore` explícito e um aviso — chute silencioso polui o histórico.

Entram no commit: a interseção entre "Arquivos Afetados" do PLAN e o que foi
efetivamente modificado, **mais tudo que o próprio fluxo escreveu** — o
`TASKS.md`, o arquivo de memória, e o `SPEC.md`/`PLAN.md` quando houve transição
de status nesta invocação.
Nunca `git add -A`. Nunca `--no-verify` ou `--no-gpg-sign` — hook que falha é
sinal real.

**Falha no commit** → pausa `falha-commit`: reverta o `[X]` do **título** (a
consolidação não aconteceu), mantenha os `[X]` de passos e validações (o trabalho
foi feito), registre o comando e o stderr do hook, e **não** tente recommitar. Se
o hook rejeitou, alguém precisa olhar.

## Saída ao usuário

```
Modo: implementar
Estado: <task TNN | cadeia concluída | pausa em TNN>
Motivo: <vocabulário controlado, quando aplicável>
Próxima ação sugerida: <1 linha>
```

Sem narração extensa, sem emoji.

## Fora deste modo

Não edita SPEC/PRD/TRD, não muda a estrutura de PLAN/TASKS (só marca `[X]` e
adiciona notas), não promove para `concluido`, não faz auditoria ampla de
qualidade no fechamento, e não impõe TDD — usa teste como sinal quando existe,
sem ditar estilo.
