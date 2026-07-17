# python-practices

Skill prescritiva e didática para escrita, revisão e planejamento de desenvolvimento em Python — convenções PEP 8, type hints, orientação a objetos, error handling, organização de módulos, async e decomposição de funcionalidades em tarefas. Aplica as convenções diretamente ao código enquanto escreve, sem parar para explicar cada decisão — o objetivo é consistência e qualidade.

Ativa sempre que a tarefa envolver escrever, revisar ou analisar código Python (`.py`), ou planejar/decompor uma funcionalidade Python em tarefas, mesmo quando o usuário não pede explicitamente por "boas práticas" ou "planejamento".

## Estrutura

```
skills/python-practices/
└── SKILL.md   ← guia prescritivo completo (sempre carregado)
```

A skill é um único `SKILL.md`, sem references ou scripts. Todo o conteúdo — convenções de código, type hints, OOP, error handling, organização, async, anti-patterns e a seção de planejamento de tarefas — está carregado no próprio guia.

## Pré-requisitos e configuração

- Alvo de Python 3.10+ para as convenções de type hints (`X | None` em vez de `Optional[X]`); recursos citados específicos de 3.11+ (`asyncio.TaskGroup`) e 3.12+ (sintaxe nativa de generics `def func[T]`)
- `pyproject.toml` como fonte única de configuração do projeto (substitui `setup.py`, `setup.cfg`, `tox.ini`)
- Ferramental de referência assumido nas convenções de formatação: Black/Ruff (linha de 88 caracteres, aspas duplas) e mypy para checagem de tipos
- Para bibliotecas externas, a skill instrui a buscar documentação atualizada antes de escrever código — via MCP de docs disponível na sessão (ex.: `context7`, `docs-langchain`) ou, na ausência, via web search

## Skills relacionadas

- **typescript-practices** — skill irmã com o mesmo molde prescritivo, para o ecossistema TypeScript
- **guia-de-testes** — cobre a escrita dos testes que os checklists de tarefa desta skill exigem
- **preparar-execucao** — planejamento mais amplo de implementação; a seção "Planejamento de tarefas Python" aqui é a camada específica da linguagem
- **implementar-task** — execução das tarefas decompostas segundo a estrutura definida nesta skill
- **escrever-prd** / **escrever-trd** — definição de requisitos e decisões técnicas que antecedem a decomposição em tarefas

## Exemplos de uso

```
Revisa esse módulo Python e aponta o que está fora do padrão

Adiciona type hints nas funções públicas desse arquivo

Refatora essa classe para receber as dependências pelo __init__

Cria a hierarquia de exceções de domínio pra esse serviço

Esse except Exception: pass tá certo? Como deveria tratar?

Converte esse Optional[X] pra sintaxe moderna

Paraleliza essas chamadas HTTP com asyncio

Decompõe "adicionar autenticação JWT à API" em tarefas de implementação
```

## Limitações conhecidas

- Guia prescritivo — pode conflitar com convenções já estabelecidas no projeto. Quando houver conflito, as convenções do repositório prevalecem; informe no prompt
- Assume Python moderno (3.10+); parte das regras de type hints e async não se aplica a bases de código em versões anteriores
- Não é um linter nem type checker — é guia de escrita e revisão, não substitui Ruff, Black ou mypy rodando de verdade
- A checagem de documentação de bibliotecas depende de um MCP de docs disponível na sessão ou de acesso a web search; sem eles, a skill não consegue confirmar a API atual
- A seção de planejamento produz decomposição em tarefas e checklists, mas não gerencia backlog nem acompanha execução — isso fica com as skills de plan/task
