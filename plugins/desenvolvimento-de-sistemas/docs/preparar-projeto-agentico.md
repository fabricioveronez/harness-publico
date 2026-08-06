# preparar-projeto-agentico

Prepara um repositório que já existe para ser operado por agentes de codificação. Analisa o projeto e monta uma ficha de evidências (`fato → arquivo onde foi lido`), cria os scripts de operação (`up`, `down`, `test`, `exec`), **valida cada um contra o ambiente real** e só então escreve um `AGENTS.md` enxuto que aponta para esses scripts, com ponte para o `CLAUDE.md`. Tem também o modo `auditar`, que confronta um `AGENTS.md` existente com o repositório e devolve mentira, peso morto, buraco e endereço errado.

A ordem é o que diferencia a skill de um gerador de documento: comando cru copiado para dentro da regra envelhece separado do projeto e diverge calado; ponteiro para script validado sobrevive à troca da pilha inteira.

## Pré-requisitos e configuração

- Um repositório com código — a skill não roda em diretório vazio, porque sem leitura não há ficha de evidências
- O ambiente de execução do projeto disponível na máquina (Docker, devcontainer CLI, gerenciador da linguagem — o que o repositório usar)
- Portas do projeto livres: o portão de validação sobe o ambiente de verdade antes de escrever qualquer documento

## Dependências externas

Nenhuma biblioteca. A skill usa o que o próprio repositório já declara — Docker Compose, devcontainer CLI, `uv`/`npm`/`go`, `make`. O ambiente é detectado por evidência, nunca presumido.

## Skills relacionadas

- **nextjs-bootstrap** — cobre o mesmo terreno para projeto Next.js novo, com stack fixa e scaffolding completo. As duas são autônomas e se sobrepõem: use a `nextjs-bootstrap` em greenfield Next.js, esta em qualquer projeto que já existe
- **containerizar-projeto** — se o repositório ainda não tem ambiente containerizado, rode ela antes: esta skill detecta ambiente, não cria
- **criar-runbook** — o runbook cobre deploy e operação em produção; esta skill para na fronteira do desenvolvimento
- **guia-de-testes** — a skill reporta a ausência de suíte como achado, mas não escreve teste; quem faz isso é a `guia-de-testes`

## Exemplos de uso

```
Esse projeto não tem contexto nenhum pro agente, deixa ele preparado

Meu AGENTS.md saiu do /init e ficou gigante, corta o que não presta

Cria os scripts pra operar esse projeto e documenta pro agente

O CLAUDE.md desse repo está desatualizado, revisa contra o código

O agente fica tateando e instalando dependência na minha máquina em vez de usar o container

Escreve o AGENTS.md desse repositório lendo o projeto de verdade
```

## Limitações conhecidas

- **Não altera o projeto.** O escopo de escrita é `scripts/`, `AGENTS.md`, a ponte `CLAUDE.md`, `.env` e `.gitignore`. Suíte quebrada, credencial em claro e migração ausente viram achado no output, não conserto — mesmo quando corrigir seria trivial
- **`README.md` é entrada, nunca saída.** Ele é lido como pista a confirmar (envelhece pior que código), e a skill não escreve nele
- **Uma aplicação, tudo na raiz.** Monorepo e repositório com áreas heterogêneas reabrem a questão de `AGENTS.md` aninhado e ficam fora — a skill declara e para
- **Escopo de desenvolvimento, não de produção.** `deploy`, staging e ambiente produtivo não entram no contrato de scripts
- **`down` derruba sem perguntar**, inclusive os dados locais. Prompt interativo travaria a sessão do agente; a única defesa possível é a linha proibitiva que a skill escreve no bloco de políticas
- **Os relatórios não viram arquivo.** Relatório de exclusão e lista de achados saem só no output da conversa — relatório versionado envelhece e ninguém relê
- **O portão custa.** Subir o ambiente, provar os quatro scripts e derrubar consome mais tempo e tokens que escrever o documento direto. É o preço de não entregar um arquivo que aponta para script quebrado
