---
name: preparar-projeto-agentico
description: |
  Prepara um projeto que já existe para ser operado por agentes de codificação: analisa o repositório, cria e
  VALIDA os scripts de operação (up, down, test, exec) e só então escreve um AGENTS.md enxuto que aponta para
  esses scripts, com ponte para CLAUDE.md. Tem também o modo auditar, que confronta um AGENTS.md existente com
  o repositório real e devolve mentira, peso morto, buraco e endereço errado. Use SEMPRE que o usuário falar em
  "criar/escrever/melhorar o AGENTS.md", "gerar o CLAUDE.md do projeto", "meu AGENTS.md está inflado ou
  desatualizado", "o /init gerou um monte de lixo", "revisar as regras do projeto", "criar os scripts de uso ou
  de operação do projeto", "ensinar o agente a operar essa aplicação", "o agente fica tateando e instalando
  coisa na minha máquina", ou ao entrar num repositório que ainda não tem contexto para agentes — mesmo que ele
  não use as palavras AGENTS.md, CLAUDE.md ou "scripts".
---

# Preparar projeto para desenvolvimento agêntico

Um repositório não diz ao agente como ser operado. Sem isso ele tateia: erra o diretório, instala dependência
no host, roda o teste fora do ambiente do projeto. O desfecho pior não é quebrar — é **acertar pelo caminho
errado**: teste verde, máquina suja, e ninguém percebe.

Esta skill fecha esse buraco em duas camadas encadeadas: **scripts que provaram funcionar** e um **AGENTS.md
curto que aponta para eles** em vez de repetir comando.

## O que esta skill não é

Não é um gerador de AGENTS.md. Existe evidência de que arquivo de guidance escrito sem curadoria **piora** o
agente — ele enche o contexto, dilui as regras que importam e faz o modelo dar mais passos para chegar no
mesmo lugar. Um arquivo bonito com trinta fatos que o agente descobriria lendo o repositório é pior que
arquivo nenhum, porque custa contexto em toda sessão e não previne erro nenhum.

O valor está no processo com portão, não no template. Duas consequências que atravessam a skill inteira:

- **Todo fato precisa de endereço no repositório.** Nada entra por convenção de linguagem ou de framework.
- **O que foi cortado é entregável.** Quem só entrega o arquivo esconde as decisões; quem entrega o arquivo
  mais a lista endereçada do que ficou de fora entrega uma revisão.

## Modos

| Modo | Quando | O que faz |
|---|---|---|
| `auditar` | já existe `AGENTS.md` ou `CLAUDE.md` no repositório | confronta o que está escrito com o repositório real e devolve o diagnóstico |
| `criar` | não existe nada, ou o existente é descartável | monta os scripts, valida, escreve o arquivo do zero |

Na dúvida, comece por `auditar` — é ele que revela se o que existe tem salvação. Um `AGENTS.md` que só tem
boilerplate de ferramenta (bloco gerado, badge, aviso de wiki) conta como "não existe": preserve o bloco
gerado e trate o resto como `criar`.

O usuário pode pedir um modo direto. Respeite.

## Escopo de escrita

Esta é a regra que mais vai ser testada durante a execução, porque violar ela é sempre o caminho mais curto:

| Pode escrever | Não pode tocar |
|---|---|
| `scripts/` | qualquer arquivo versionado fora da coluna da esquerda |
| `AGENTS.md` e a ponte `CLAUDE.md` | código, config de teste, `package.json`/`pyproject`/`go.mod` |
| `.env` (a partir do exemplo) e `.gitignore` | `docker-compose.yml`, `Dockerfile`, devcontainer, CI |
| — | `README.md` (ele é **entrada**, nunca saída) |

**Estado de ambiente é livre.** Subir container, criar banco, baixar imagem, gerar artefato ignorado pelo git
— tudo liberado, porque é efêmero e é exatamente o que o `down` desfaz. A fronteira é o repositório, não a
máquina.

Se consertar um script exigiria alterar o projeto, **pare**. Isso não é script mal escrito, é achado do
projeto — vai para a lista de achados e o usuário decide.

---

## Fase A — Análise

Produz a **ficha de evidências**, que é o insumo de tudo que vem depois. Sem ela a skill vira template com
etapas.

Leia, nesta ordem de prioridade: configuração de dependências, orquestração (compose, devcontainer, Makefile,
Taskfile), arquivos de ambiente (`.env*`), configuração de testes, estrutura de pastas do código, CI, e o
`README`.

O `README` entra como **pista, não como fato**. Ele envelhece pior que código e costuma ter marketing junto.
Se ele afirma `npm start` e o `package.json` não tem esse script, isso não é fato — é achado.

A ficha registra `fato → onde foi lido`:

```
porta da aplicação    = 8080            ← docker-compose.yml:11
banco                 = postgres 15     ← docker-compose.yml:20
runner de teste       = ausente         ← package.json: scripts.test é placeholder
schema do banco       = criado no boot  ← src/models/db.js: sequelize.sync()
ambiente de execução  = compose         ← não há devcontainer; Dockerfile em src/
credencial de dev     = no compose      ← docker-compose.yml:13-17 (em claro)
```

**Fato sem linha na ficha não pode aparecer no `AGENTS.md`.** Ele vai para a lista "não consegui confirmar" do
relatório. É esse acoplamento que torna "todo fato sai da leitura" verificável em vez de aspiracional.

### Ambiente: pergunte duas coisas, não uma

O formato mais comum não é um ambiente, são dois — compose sobe o banco, o gerenciador de linguagem roda o
teste. Quem trata como singular escreve `exec` errado e erra calado, porque `exec psql` e `exec pytest`
querem lugares diferentes.

- **Onde as dependências vivem**: compose, devcontainer, serviço externo, nenhuma.
- **Onde o código executa**: devcontainer, container da própria app, venv/uv, node local, host puro.

Precedência quando houver mais de um candidato: **o ambiente é onde os testes já rodam hoje**. Devcontainer
ganha de compose, compose ganha de gerenciador de linguagem, gerenciador ganha do host — mas só com evidência
na ficha. Sem evidência é host, e isso vira linha do relatório, não chute.

Detalhe por stack e por tipo de ambiente: `references/ambientes.md`.

---

## Fase B — Scripts

Escreva os scripts **antes** do documento. Se o `AGENTS.md` nascer primeiro, o bloco de comandos se enche de
comando cru — que envelhece separado do projeto e diverge calado. Nascendo depois, ele vira ponteiro, e a
cadeia fica assim:

```
AGENTS.md  →  scripts/  →  ambiente (compose · devcontainer · venv)  →  imagem/serviço
```

Cada camada conhece só a de baixo. Trocar a pilha inteira não move uma linha do `AGENTS.md`.

### O conjunto

O default é `up`, `down`, `test`, `exec`. Não é lei — é o que satisfaz o critério em quase todo projeto:

> Um script existe quando o agente vai precisar daquilo com frequência **e** errar tem custo.

- `up` e `down` — ciclo de vida.
- `test` — a rotina. Não é conveniência: ele carrega o detalhe de execução que ninguém adivinha (de qual
  diretório os imports resolvem, qual arquivo de ambiente vale).
- `exec` — a válvula. **É ele que fecha a regra.** Sem `exec`, a primeira necessidade não prevista devolve o
  agente para o host, e todo o resto do trabalho evapora. Regra com buraco se contorna; regra exaustiva se
  obedece.

Um quinto entra quando a ficha mostra operação recorrente de invocação não adivinhável: reset de banco que
não tem migração, seed, o gate de lint/typecheck que o projeto não tem. Aplique o mesmo teste antes de
aceitar: **tirar esse script faria o agente errar?** Cada script novo é mais uma linha permanente no
`AGENTS.md` e mais uma superfície para envelhecer.

O escopo é desenvolvimento agêntico. `deploy`, staging e produção ficam de fora.

### Como o script precisa ser

Script consumido por agente é diferente de script consumido por humano:

- **Idempotente** — ele não lembra do estado entre sessões e vai subir o que já está de pé. `up` rodado duas
  vezes não pode falhar.
- **Não-interativo** — pergunta na tela trava a sessão inteira. Isso inclui `down`: ele derruba sempre, sem
  confirmação. A defesa contra a destruição não é técnica, é a linha proibitiva no `AGENTS.md`.
- **Erro acionável** — a mensagem de falha é a documentação. É ela que substitui a linha de regra que você
  não escreveu.
- **Saída enxuta** — log de build despejado na sessão queima orçamento de contexto e não ajuda ninguém.

---

## Fase C — Portão de validação

**O `AGENTS.md` não nasce enquanto o contrato não provar que funciona.** Arquivo perfeito apontando para
script quebrado é pior que arquivo nenhum: ele dá confiança onde não devia.

Validar não é conferir código de saída zero. Cada script falha de um jeito diferente:

| Script | O que provar | A armadilha |
|---|---|---|
| `up` | roda duas vezes seguidas sem falhar | é o único limpo |
| `test` | **alcançou o runner**, a partir do diretório onde os imports resolvem | suíte vermelha ≠ script errado |
| `exec` | executou **dentro** do ambiente | `exit 0` não prova nada — um `exec` que caiu no host devolve 0 alegremente |
| `down` | derrubou de fato | destrutivo por desenho; valide por último |

Para o `exec`, use um comando que só responde certo lá dentro: `hostname`, uma variável que só existe no
ambiente, um caminho que não existe no host. `exec true` é validação de teatro.

Para o `test`, o critério é ter chegado no runner. Se a suíte do projeto está vermelha ou não existe, isso é
fato para a ficha e linha da lista de achados — não é falha do portão.

### Quando falha: quem emitiu o erro?

Este é o critério mecânico que impede o agente de racionalizar a favor do portão verde. A fronteira é o
momento em que o controle passa para o código do repositório:

| Emissor | Veredito | Exemplo |
|---|---|---|
| shell, wrapper de ambiente, runtime — **antes** de alcançar o código do projeto | script errado → **conserte e repita** | `command not found`, diretório errado, container não subiu, flag errada no runner, `.env` apontado para o arquivo com typo |
| o código do projeto ou o runner reportando resultado | projeto → **devolva como achado** | falha de asserção, exceção da aplicação, migração faltando, import quebrado do próprio código, suíte inexistente |

Antes da fronteira, o script não cumpriu o que prometeu. Depois dela, cumpriu — e o que apareceu é fato do
projeto, que é justamente o que deve ser preservado, não maquiado.

**Nunca conserte o projeto para passar no próprio portão.** Skill que faz isso está otimizando a métrica
errada e não deixa rastro auditável.

Registre o comando exatamente como foi executado com sucesso. **É esse comando que vai para o `AGENTS.md`** —
não o que o agente imagina que ele seria.

---

## Fase D — Documento

Detalhe dos seis blocos, do critério de entrada linha a linha e das quatro classes da auditoria:
`references/agents-md.md`. Leia antes de escrever ou auditar o arquivo.

O essencial:

- **Seis blocos, nesta ordem**: sobre o projeto · arquitetura e stack · estrutura do projeto · comandos de
  build e teste · convenções de código · políticas e limites.
- **Teto de 200 linhas.** É teto, nunca meta. Estourar não dá erro — degrada a obediência: a regra que
  importa se perde no ruído e deixa de ser seguida.
- **Critério de entrada**: entra o que o agente não descobre lendo o repositório e cuja ausência faz ele
  errar. O teste por linha é *"tirar isso faria o agente errar?"*. Se não faria, corte.
- **Aponte, não copie.** Informação que já existe em outro arquivo ganha o caminho dele, não uma cópia.
- **Comandos = ponteiros para `scripts/`.** Comando copiado para dentro da regra envelhece separado do
  projeto.

### A ponte para o CLAUDE.md

O `AGENTS.md` é o canônico. Antes de escrever a ponte, **verifique se o Claude Code já lê `AGENTS.md`
nativamente** (a documentação oficial e o `/context` respondem isso) em vez de gravar a suposição. Se ainda
não ler, o `CLAUDE.md` é um arquivo de uma linha:

```markdown
@AGENTS.md
```

Prefira isso a symlink: o import garante o carregamento, é auditável no diff e não quebra em Windows nem em
CI que não preserva link. Se já existir um `CLAUDE.md` com conteúdo duplicado, a duplicata é achado — a
correção é reduzi-lo à ponte.

---

## Fase E — Saída

Quatro entregáveis. Os dois primeiros são arquivos; **os dois últimos vão no output da conversa e não viram
arquivo** — relatório versionado envelhece, ninguém relê, e ele existe para o usuário decidir agora.

1. **`scripts/`** — validados, com o resultado de cada prova do portão.
2. **`AGENTS.md` + ponte** — dentro do teto, com o relatório de contagem.
3. **Relatório de exclusão** — tudo que foi considerado e ficou de fora, cada item com endereço:

   | Endereço | Quando |
   |---|---|
   | verificação automática (hook, CI, lint) | a máquina consegue conferir sozinha → não gaste linha de regra |
   | skill | conhecimento de domínio usado às vezes → carregar sob demanda, não em toda sessão |
   | README | instrução para humano (pré-requisito de máquina, ferramenta global) |
   | não confirmado | pareceu verdade mas não achou evidência no repositório |

4. **Lista de achados do projeto** — o que está quebrado, foi encontrado e **não** foi consertado: suíte
   inexistente, `.env` de exemplo com typo, credencial em claro, ausência de migração.

Passe cada achado pelo mesmo roteador antes de fechar. Alguns são só bug e morrem na lista; outros são
**comportamento do projeto que o agente precisa conhecer** — "o schema nasce no boot, não há migração" é
achado *e* é linha de regra. Sem essa passada, a lista vira depósito.

## Limites declarados

- **Precisa de projeto.** Sem repositório não há ficha de evidências, e sem ficha a skill vira template.
  Repositório vazio é caso de bootstrap de stack, não desta skill.
- **Uma aplicação, tudo na raiz.** Monorepo e repositório com áreas heterogêneas reabrem a pergunta de
  `AGENTS.md` aninhado e ficam fora. Se encontrar esse formato, diga e pare — não invente hierarquia.
- **Não altera o projeto.** Vale sempre, inclusive quando consertar seria trivial.
