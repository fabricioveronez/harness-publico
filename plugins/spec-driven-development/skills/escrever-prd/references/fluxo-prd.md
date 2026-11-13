# Fluxo PRD

Leia esta referência somente depois de o `SKILL.md` selecionar **PRD**. Este fluxo cria ou
edita um documento autocontido de comportamento e regras de negócio para uma feature.

## Papel do PRD

O PRD é a fonte humana da intenção da feature e controla seu ciclo de vida por `status` e
`depends_on`. A implementação deriva SPEC/PLAN/TASKS do PRD; stack, arquitetura, padrões e NFR
global vêm do TRD e dos ADRs.

PRDs com `status: concluido` são registros históricos imutáveis. Mudança posterior abre um
novo PRD e pode referenciar o anterior.

## Operação

- **Criação** — feature nova sem referência a PRD existente.
- **Edição** — referência a PRD por número, nome ou arquivo.

Na edição:

1. Leia o PRD em `./docs/prds/` ou no caminho informado.
2. Interrompa se `status: concluido`.
3. Preserve `prd_number`, nome, status e IDs existentes.
4. Se o documento já possui seção Milestones, trate-o como **PRD legado**: preserve integralmente
   milestones, IDs, checklists e sua semântica de conclusão. Não crie milestones adicionais e
   não migre o formato sem solicitação explícita.

## Granularidade

Um PRD cobre uma feature. Rules, expiração, rate limit, tratamento de erro e outros controles
que apenas tornam a feature correta permanecem no mesmo documento.

Se partes autocontidas compartilham um resultado amplo, retorne ao roteamento e proponha Epic.
Se são demandas sem resultado agregador real, proponha PRDs separados e aguarde o usuário
selecionar um. Nunca gere todos em sequência.

## Draft

1. Leia [`template-prd.md`](template-prd.md).
2. Gere todas as seções aplicáveis imediatamente.
3. Marque rules, edge cases, critérios, exclusões e outras inferências com
   `*(premissa — confirme ou corrija)*`.
4. Apresente o draft para revisão pontual.

### Funcionalidades

- Cada funcionalidade é uma User Story com ID estável `US01`, `US02` etc.
- Formato: “Como [persona], quero [ação], para [benefício]”.
- Cada US contém ao menos uma Rule e um Edge case.
- Edge case: `[situação anômala] → [comportamento esperado]`.
- Detalhe de realização técnica não entra na US.

### Critérios de aceite

- Cada critério novo recebe ID estável `AC01`, `AC02` etc.
- Critérios funcionais e NFR específicos da feature devem ser observáveis.
- NFR de feature registra limiar e razão de negócio. NFR global fica no TRD.
- Evite “funcionar bem” ou “boa performance”; use valor verificável ou marque a premissa.
- O checkbox de cada `ACxx` é a evidência canônica de aceite em PRDs novos.
- Um PRD novo pode chegar a `concluido` somente quando todos os `ACxx` estiverem aprovados,
  mas esta skill não promove o status automaticamente.

### Fluxo de negócio

Inclua diagrama de jornada/processo somente quando ramificações de regra não ficarem claras
nas USs e edge cases. Topologia de componentes, serviços e dados pertence ao artefato técnico.

### Fora do escopo e decisões

- Fora do escopo é obrigatório; inferências ficam marcadas.
- Registro de Decisões contém decisões de produto e premissas de negócio significativas.
- Decisão arquitetural durável é sinalizada para ADR e apenas referenciada no PRD.

## Proveniência opcional

Quando o usuário fornecer explicitamente uma Epic e uma capacidade de origem, registre:

```yaml
origin_epic: "E001"
origin_capability: "C01"
```

Omitir os campos quando não houver origem explícita. Eles indicam proveniência, não
dependência.

Se o pedido citar apenas `E###/Cxx` sem repetir o conteúdo necessário, leia seletivamente na
Epic referenciada a direção compartilhada, a fronteira e a capacidade `Cxx`. Isso é contexto
explicitamente solicitado, não varredura automática. Não carregue capacidades irmãs, não leia
PRDs derivados e não altere a Epic. Se a capacidade ainda não definir uma feature especificável,
faça uma pergunta bloqueante em vez de inventar requisitos.

## Dependências entre PRDs

Antes da revisão final:

1. Liste os PRDs existentes no caminho de destino.
2. Identifique somente dependências diretas: comportamento, entidade, interface ou regra de
   outro PRD pressuposta por esta feature.
3. Preencha `depends_on` com os `prd_number` correspondentes.
4. Registre no Registro de Decisões o critério de cada dependência.

Não use `depends_on` para Epic de origem, documentos relacionados ou itens apenas do mesmo
domínio. Reavalie dependências se o escopo mudar durante o refinamento.

## Salvamento

### Criação

1. Encontre o maior prefixo `NNN` em `./docs/prds/`; comece por `001`.
2. Nomeie `NNN-[nome-em-kebab-case].md`.
3. Use `./docs/prds/` salvo caminho informado e crie o diretório se necessário.
4. Preencha `prd_number` e salve sempre com `status: rascunho`.

### Edição

Sobrescreva o arquivo original preservando identificadores e status. Novas USs e critérios
recebem o próximo ID sequencial livre. PRD legado mantém seus milestones existentes.

Depois de salvar, encerre. Não ofereça criação automática de outro PRD; apenas informe que um
novo ciclo explícito pode tratar outra feature.
