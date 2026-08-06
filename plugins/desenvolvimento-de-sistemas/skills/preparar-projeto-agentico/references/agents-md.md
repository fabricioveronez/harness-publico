# O arquivo: estrutura, critério de entrada e auditoria

Índice:
- [Os seis blocos](#os-seis-blocos)
- [Critério de entrada](#critério-de-entrada)
- [O roteador de rejeição](#o-roteador-de-rejeição)
- [Regras de escrita](#regras-de-escrita)
- [As quatro classes da auditoria](#as-quatro-classes-da-auditoria)
- [Modelo de referência](#modelo-de-referência)

---

## Os seis blocos

Ordem fixa. A spec do `AGENTS.md` não exige seção nenhuma — esses seis são convergência entre o que a spec
lista como comum e o que de fato muda o comportamento do agente. A ordem importa porque o começo do arquivo é
o que sobrevive melhor à diluição de contexto.

### 1. Sobre o projeto
O que é e qual o objetivo. Duas ou três linhas. Sem história, sem justificativa de existência.

### 2. Arquitetura e stack
Tecnologias principais, como o deploy acontece, arquitetura em visão alta. **Sem diagrama e sem descrever
camada por camada** — o agente lê o código para isso. O que entra aqui é o que ele *não* infere: que o banco
é compartilhado com outro serviço, que existe fila, que a app roda atrás de proxy.

### 3. Estrutura do projeto
Pastas principais e onde encontrar cada tipo de recurso. **Mapa de navegação, não inventário.** Não desça
arquivo a arquivo.

Este bloco costuma ser subestimado e é o que mais paga. A pesquisa sobre guidance files mostra que o ganho
vem de o agente **chegar no arquivo certo** — a cobertura sobe, a qualidade do patch por si não muda. Um mapa
bom é literalmente o mecanismo de retorno do arquivo inteiro.

### 4. Comandos de build e teste
Como subir, como testar, como executar comando dentro do projeto. **Ponteiros para `scripts/`**, com o
comando exatamente como foi validado. Só os comandos que o agente vai executar de fato — não catálogo de tudo
que é possível.

Não explique o que o comando faz. Ele não precisa entender, precisa acertar.

### 5. Convenções de código
Só as que este repositório de fato segue, comprovadas lendo o código existente, incluindo o padrão de commit.
Convenção padrão da linguagem não entra — o modelo já sabe.

### 6. Políticas e limites
O que não deve ser feito e as exceções que precisam de tratamento. É o bloco mais curto e o de maior
densidade, porque é onde mora o que a máquina não consegue conferir.

É aqui que vive a linha proibitiva do `down`: ele derruba tudo, inclusive os dados, não pede confirmação
(prompt interativo trava o agente) e não tem defesa técnica possível. Sobra a regra.

---

## Critério de entrada

Uma linha entra quando as duas condições valem:

1. o agente **não descobre** aquilo lendo o repositório; **e**
2. a ausência dela faz ele **errar**.

O teste operacional, aplicado linha a linha: *"tirar isso faria o agente errar?"* Se não faria, corte.

| Entra | Não entra |
|---|---|
| comando que ele não tem como adivinhar | qualquer coisa que ele descobre lendo o código |
| convenção que diverge do padrão da linguagem | convenção padrão da linguagem |
| onde os testes rodam e de qual diretório | documentação detalhada de API (aponte o caminho) |
| quirk de ambiente (variável obrigatória, arquivo de env que vale) | informação que muda toda semana |
| decisão de arquitetura específica deste projeto | descrição arquivo por arquivo do código |
| armadilha não óbvia ("o schema nasce no boot") | prática auto-evidente ("escreva código limpo") |
| etiqueta do repositório (branch, PR, commit) | explicação de conceito de tecnologia |

O teto de 200 linhas é teto, nunca meta. Estourar não dá erro — **degrada a obediência**: quando o arquivo
fica longo demais, a regra que importa se perde no ruído e o agente passa a ignorar metade. Se ele insiste em
fazer algo que você já proibiu por escrito, o suspeito número um é o tamanho do arquivo, não a redação da
regra.

---

## O roteador de rejeição

Corte não é descarte. Cada rejeição tem endereço, e o endereço se reusa no próximo repositório.

| Destino | Critério | Exemplo |
|---|---|---|
| **verificação automática** | a máquina consegue conferir sozinha | formatação, lint, tipo, import ordenado → hook ou CI, não linha de regra |
| **skill** | conhecimento de domínio usado só às vezes | padrão de um subsistema específico → carrega sob demanda em vez de custar contexto toda sessão |
| **README** | instrução para humano | instalar CLI global, criar conta, pedir credencial — o agente não faz isso |
| **não confirmado** | pareceu verdade, não achou evidência | tudo que veio de convenção de framework e não de leitura |

O critério tem duas direções, e a segunda é a que importa mais:

- o que a máquina **consegue** conferir → sai do arquivo e vira verificação automática;
- o que a máquina **não consegue** conferir → é exatamente o que precisa estar no arquivo.

A regra é advisory; o hook é determinístico. Gastar linha de regra com o que um hook garante é desperdiçar
espaço permanente em algo que já está resolvido.

Cheque unanimidade antes de escrever "sempre" ou "nunca": procure a exceção no código. Regra absoluta com
exceção conhecida ensina o agente a desobedecer o conjunto.

---

## Regras de escrita

- Frase curta e imperativa. Nada de parágrafo explicativo.
- Sem título de boas-vindas, badge, emoji ou seção de contribuição.
- Não explique conceito geral de tecnologia. Assuma que quem lê sabe o que é container, banco relacional e
  teste automatizado.
- Informação que já existe em outro arquivo do repositório: aponte o caminho, não copie o conteúdo.
- Caso raro fica de fora — ele custa espaço permanente por uma situação eventual.
- Ênfase (`IMPORTANTE`, `NUNCA`) funciona, e por isso gasta: se tudo é importante, nada é.

---

## As quatro classes da auditoria

No modo `auditar`, confronte cada linha do arquivo existente com a ficha de evidências. Todo achado cai numa
destas quatro:

| Classe | Definição | Como detectar |
|---|---|---|
| **Mentira** | o arquivo afirma, a ficha contradiz | comando que mudou, caminho que sumiu, porta trocada, script referenciado que não existe, versão desatualizada |
| **Peso morto** | não passa em *"tirar faria o agente errar?"* | conceito geral de tecnologia, fato descobrível lendo o repo, duplicata de outro arquivo, boilerplate de ferramenta |
| **Buraco** | está na ficha, o agente não descobre sozinho, não está no arquivo | a classe mais valiosa — é onde mora o ganho real |
| **Endereço errado** | ocupa espaço permanente mas pertence a outro lugar | deveria ser hook, skill ou README |

Mais duas verificações mecânicas, que não dependem de julgamento:

- **contagem de linhas** contra o teto;
- **revalidação do contrato**: os scripts referenciados ainda funcionam? `up` duas vezes, `test` alcança o
  runner, `exec` prova o ambiente. Um arquivo impecável apontando para script quebrado é pior que nenhum.

**Relatório primeiro, edição sob aprovação.** Auditoria que se auto-aplica é reescrita, e o usuário perde a
chance de discordar linha a linha — que é onde está o valor.

Bloco gerado por ferramenta (OpenWiki, Copilot, qualquer marcador `<!-- X:START -->`) é **preservado**, não
auditado. Ele tem dono e regenera sozinho; classifique como peso morto apenas se o usuário perguntar.

---

## Modelo de referência

Formato, não conteúdo a copiar. O conteúdo real sai da ficha de evidências.

```markdown
# AGENTS.md

## Sobre o projeto
Portal de notícias usado como aplicação de exemplo em treinamento. Publica e lista posts.

## Arquitetura e stack
Node 18 + Express + Sequelize, PostgreSQL 15. Aplicação e banco sobem por Docker Compose.
Métricas expostas em /metrics via prom-client.

## Estrutura do projeto
- `src/` — aplicação (`server.js` é o entrypoint)
- `src/models/` — modelos Sequelize e conexão
- `src/views/` — templates EJS
- `scripts/` — operação do projeto

## Comandos
Todo comando roda pelos scripts. Nada executa direto no host.

- `./scripts/up.sh` — sobe app e banco. Idempotente.
- `./scripts/down.sh` — derruba tudo.
- `./scripts/test.sh` — roda a suíte.
- `./scripts/exec.sh <comando>` — executa comando dentro do ambiente.

## Convenções
- Commit: `<tipo>: <descrição>`, tipos `feat`, `fix`, `docs`, `chore`.

## Políticas e limites
- `./scripts/down.sh` remove o volume do banco. Todos os dados locais são perdidos.
  Não rode sem o usuário pedir.
- O schema é criado no boot da aplicação (`sequelize.sync()`). Não existe migração:
  para recriar o schema, derrube e suba de novo.
- Não instale dependência no host. Use `./scripts/exec.sh`.
```
