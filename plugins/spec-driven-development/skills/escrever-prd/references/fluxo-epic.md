# Fluxo Epic

Leia esta referência somente depois de o `SKILL.md` selecionar **Epic**. Este fluxo cria,
edita, analisa ou propõe a decomposição de uma Epic de alto nível. Ele nunca cria PRDs.

## Papel da Epic

Uma Epic preserva a direção de um resultado amplo enquanto research e planejamento ainda
podem mudar sua decomposição. Ela registra problema, evidências, resultados, capacidades
candidatas, milestones de resultado e incertezas. Capacidade candidata não é compromisso de
virar PRD: pode desaparecer, juntar-se a outra ou originar vários PRDs posteriormente.

## Operação

Identifique uma operação antes de continuar:

- **Criar** — o usuário descreve uma nova Epic ou não referencia arquivo existente.
- **Editar** — o usuário aponta uma Epic por número, nome ou arquivo.
- **Analisar** — o usuário quer crítica, leitura ou avaliação; não escreva arquivos.
- **Decompor** — o usuário pede possíveis PRDs ou a quebra da Epic; responda na conversa e
  não modifique nenhum arquivo.

### Edição e status

Leia a Epic referenciada em `./docs/epics/` ou no caminho informado. Preserve
`epic_number`, nome do arquivo e IDs `Cxx` e `Mxx` já atribuídos.

Estados válidos:

```text
explorando → planejada → em-progresso → concluida
```

- Criação começa sempre em `explorando`.
- Toda transição exige pedido explícito do usuário; nunca derive status da completude do texto.
- Transições seguem a ordem acima e não pulam etapas.
- `concluida` é imutável. Nova direção ou resultado posterior abre outra Epic e referencia a
  anterior.

## Criação e edição

1. Leia [`template-epic.md`](template-epic.md).
2. Inspecione `./docs/epics/`, referências fornecidas e contexto de projeto relevante.
3. Gere o documento completo no nível de decisão disponível. Marque inferências como
   `*(premissa — confirme ou corrija)*` e mantenha lacunas conscientes em Questões abertas.
4. Não transforme capacidades candidatas em User Stories, rules, edge cases ou tarefas.
5. Apresente o draft e refine somente a Epic.
6. Após aprovação, salve e encerre. Informe explicitamente que nenhum PRD foi criado.

### Numeração e arquivo

- Liste `./docs/epics/` e encontre o maior prefixo `E###`.
- A primeira Epic é `E001`; as seguintes incrementam a parte numérica.
- Nome: `E###-[nome-em-kebab-case].md`.
- Local padrão: `./docs/epics/`; respeite outro caminho informado.
- Crie o diretório se necessário.

### IDs estáveis

- Capacidades usam `C01`, `C02` etc.
- Milestones usam `M01`, `M02` etc.
- Em edição, IDs existentes nunca são renumerados. Novos itens recebem o próximo número livre.

## Research e planejamento

O estado `explorando` admite evidências incompletas, alternativas e questões abertas. Não
fabrique evidência para preencher a seção. Registre a fonte e a data para fato externo
consultado; informação não verificada fica como premissa ou questão.

Uma Epic `planejada` deve ter, no mínimo:

- problema e público afetado claros;
- resultado e fronteira definidos;
- métricas ou método de avaliação definidos;
- capacidades candidatas com clareza explícita;
- milestones formulados como resultados observáveis;
- questões bloqueantes resolvidas ou assumidas conscientemente pelo usuário.

O usuário decide e solicita a transição. A skill avalia os itens acima e aponta ausências,
mas não promove o status sozinha.

## Milestones de resultado

Um milestone da Epic descreve uma mudança observável no resultado, não uma fase técnica, uma
sprint ou a conclusão de documentos. Cada `Mxx` contém:

- resultado que passa a ser verdadeiro;
- evidência que demonstrará seu alcance;
- capacidades candidatas relacionadas por `Cxx`;
- checkbox de alcance, atualizado somente a pedido do usuário.

Milestones não referenciam PRDs obrigatoriamente. A Epic pode ser criada e planejada antes de
qualquer PRD existir.

## Clareza das capacidades

Use um dos valores:

- `clara` — pronta para ser considerada em uma especificação posterior;
- `research` — falta evidência ou compreensão do problema;
- `spike` — uma pergunta de viabilidade só pode ser respondida experimentando;
- `design` — a experiência precisa ser desenhada antes da especificação;
- `decisão` — há trade-off de produto ainda não resolvido;
- `aberta` — baixa clareza, ainda sem próximo passo definido.

`clara` não significa “PRD criado” nem autoriza criá-lo.

## Decomposição sem escrita

Quando o usuário pedir decomposição:

1. Leia a Epic completa e apenas as referências necessárias.
2. Apresente uma tabela `Capacidade | Possível artefato | Clareza | Próximo passo`.
3. Explique agrupamentos, cortes e incertezas sem atribuir números de PRD.
4. Não altere a Epic, não crie mapa separado e não escreva em `docs/prds/`.
5. Encerre informando que a proposta não criou artefatos.

## Relação posterior com PRDs

A Epic não mantém lista obrigatória nem backlink de PRDs. Um PRD criado em outra execução pode
registrar `origin_epic` e `origin_capability` como proveniência opcional. Essa proveniência não
é `depends_on`, não acopla status e não autoriza atualizar a Epic.

