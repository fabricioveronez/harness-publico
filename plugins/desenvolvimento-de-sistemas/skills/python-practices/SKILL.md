---
name: python-practices
description: "Padrões de código Python deste ecossistema — as decisões já tomadas sobre type hints, exceções e tratamento de erro, orientação a objetos e injeção de dependências, separação de camadas, PEP 8, async e anti-patterns. Consulte ANTES de escrever ou alterar qualquer arquivo .py — implementar endpoint ou rota, service, repository, model, schema, classe ou módulo, refatorar, corrigir bug, escrever ou ajustar teste. Não assuma que o código vizinho já segue estes padrões; imitar os arquivos ao redor costuma propagar justamente o que a skill corrige, e revisar depois de escrito vira retrabalho. Inclui checklist de implementação por tipo de tarefa (novo endpoint/handler, nova classe, integração externa, refatoração) e como decompor uma funcionalidade Python em tarefas. Use também para revisar ou auditar código Python existente."
---

# Python Practices

Guia prescritivo de boas práticas para escrita, revisão e planejamento de desenvolvimento em Python. Aplique estas convenções diretamente ao código sem explicar cada decisão — o objetivo é consistência e qualidade, não ensinar conceitos.

## Documentação de bibliotecas

Antes de usar qualquer biblioteca externa, busque a documentação atualizada:

1. Verifique se há um MCP disponível na sessão que forneça docs da biblioteca (ex.: `context7`, `docs-langchain`)
2. Se houver, consulte via MCP antes de escrever código
3. Se não houver, use web search para obter a documentação oficial atualizada
4. Nunca assuma que sua versão de treinamento reflete a API atual — bibliotecas como FastAPI, SQLAlchemy, Pydantic e Celery têm mudanças significativas entre versões maiores

## Convenções de código (PEP 8)

### Naming

- Variáveis e funções: `snake_case`
- Classes: `PascalCase`
- Constantes: `UPPER_SNAKE_CASE`
- Módulos e pacotes: `snake_case` curto
- Métodos privados e atributos internos: `_prefixo_com_underscore`
- Dunder methods: `__nome__` — não crie fora dos casos definidos pela linguagem
- Nomes descritivos — prefira `get_user_by_id` a `get_user` quando houver ambiguidade

### Imports

- Agrupe em três blocos separados por linha em branco: stdlib → third-party → interno
- Prefira imports explícitos: `from pathlib import Path`, não `import pathlib` só para usar `pathlib.Path`
- Nunca use `from módulo import *` — polui o namespace e dificulta rastreabilidade
- Use `__all__` em módulos públicos para declarar o que é exportado

```python
import os
from pathlib import Path

import httpx
from pydantic import BaseModel

from app.domain.user import User
from app.infra.repository import UserRepository
```

### Formatação

- Linhas com no máximo 88 caracteres (padrão Black/Ruff)
- Use aspas duplas como padrão — consistente com Black
- Vírgula trailing em listas e dicts multilinhas

## Type hints

Type hints são obrigatórios em todas as funções públicas e métodos de classe. Código sem anotações em funções públicas é um anti-pattern.

### Regras fundamentais

- Anote parâmetros e retorno em toda função pública
- Use `X | None` (Python 3.10+) em vez de `Optional[X]` — mais legível
- Use `Any` apenas como último recurso — força narrowing explícito antes de usar
- `Final` para constantes que não devem ser reatribuídas
- `ClassVar` para atributos de classe que não pertencem à instância

```python
from typing import Final, ClassVar

MAX_RETRIES: Final = 3

def find_user(user_id: str) -> User | None:
    ...

def process_items(items: list[str]) -> dict[str, int]:
    ...
```

### TypedDict e Protocol

- `TypedDict` para dicts com forma conhecida — melhor que `dict[str, Any]`
- `Protocol` para duck typing explícito — define contratos sem herança

```python
from typing import TypedDict, Protocol

class AddressData(TypedDict):
    street: str
    city: str
    zip_code: str

class Notifiable(Protocol):
    def notify(self, message: str) -> None:
        ...
```

### Generics

- Use `TypeVar` quando o tipo de entrada determina o tipo de saída
- Python 3.12+: use a sintaxe nativa `def func[T](x: T) -> T`

```python
from typing import TypeVar

T = TypeVar("T")

def first(items: list[T]) -> T | None:
    return items[0] if items else None
```

## Orientação a Objetos

OOP é o padrão. Use funções puras para transformações simples e utilitários sem estado — não para lógica de domínio.

### Classes

- Encapsule estado interno com atributos prefixados por `_`
- Receba dependências pelo `__init__` — não instancie dependências dentro da classe
- Uma classe deve ter uma responsabilidade clara — se o nome precisa de "And" ou "Manager" genérico, considere dividir
- Use `@dataclass` ou `@dataclass(frozen=True)` para classes de dados simples — evita boilerplate de `__init__`

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int
    currency: str

class OrderService:
    def __init__(
        self,
        repository: OrderRepository,
        notifier: Notifiable,
    ) -> None:
        self._repository = repository
        self._notifier = notifier

    def create(self, data: CreateOrderInput) -> Order:
        order = Order.from_input(data)
        self._repository.save(order)
        self._notifier.notify(f"Pedido {order.id} criado")
        return order
```

### Herança vs Composição

- Prefira composição — herança profunda (mais de 2 níveis) é sinal de problema
- Use herança quando existir relação real de "é um" com comportamento compartilhado
- Use `Protocol` para contratos que múltiplas classes implementam sem herança direta
- Classes abstratas (`ABC`) apenas quando há lógica base real a compartilhar

```python
from abc import ABC, abstractmethod

class BaseRepository(ABC):
    @abstractmethod
    def find_by_id(self, entity_id: str) -> object | None:
        ...

    def find_by_id_or_raise(self, entity_id: str) -> object:
        entity = self.find_by_id(entity_id)
        if entity is None:
            raise NotFoundError(entity_id)
        return entity
```

### Properties

- Use `@property` para acesso controlado a atributos computados ou encapsulados
- Evite setters quando possível — prefira métodos com nomes que descrevem a intenção

```python
class Circle:
    def __init__(self, radius: float) -> None:
        self._radius = radius

    @property
    def radius(self) -> float:
        return self._radius

    @property
    def area(self) -> float:
        import math
        return math.pi * self._radius ** 2
```

## Error handling

### Custom exceptions

- Crie hierarquias de exceção específicas para o domínio
- Herde de `Exception`, nunca de `BaseException`
- Inclua contexto suficiente para debugging na mensagem

```python
class AppError(Exception):
    pass

class NotFoundError(AppError):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(f"{resource} not found: {resource_id}")
        self.resource = resource
        self.resource_id = resource_id

class ValidationError(AppError):
    def __init__(self, field: str, message: str) -> None:
        super().__init__(f"Validation error on '{field}': {message}")
        self.field = field
```

### Regras de captura

- Capture exceções específicas — nunca `except Exception` ou `except:` sem re-raise
- Não engula exceções com `pass` ou `...` em blocos `except`
- Use `finally` para cleanup de recursos — ou prefira context managers (`with`)
- Propague erros inesperados — só trate o que você sabe lidar

```python
def load_config(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        raise ConfigNotFoundError(str(path))
    except json.JSONDecodeError as e:
        raise ConfigParseError(str(path), str(e)) from e
```

## Organização de código

### Estrutura de módulos

- Um módulo por responsabilidade — evite arquivos com mais de 300 linhas
- `__init__.py` expõe apenas a API pública do pacote — não reexporte tudo automaticamente
- Use `__all__` para controlar o que é público
- Separe camadas: domínio, infraestrutura, aplicação — não misture lógica de negócio com I/O

### pyproject.toml

- Use `pyproject.toml` como fonte única de configuração do projeto — substitui `setup.py`, `setup.cfg` e `tox.ini`
- Declare dependências com versões mínimas: `httpx>=0.27`
- Separe dependências de dev em grupo dedicado: `[dependency-groups]` ou `[project.optional-dependencies]`

```toml
[project]
name = "meu-projeto"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "httpx>=0.27",
    "pydantic>=2.0",
]

[dependency-groups]
dev = [
    "pytest>=8.0",
    "ruff>=0.4",
    "mypy>=1.10",
]
```

### Contexto de módulo

- Use `if __name__ == "__main__":` apenas em scripts de entrada — nunca em módulos de biblioteca
- Código de inicialização pesado (conexões, carregamento de modelos) nunca no nível do módulo — encapsule em funções ou classes

## Async

### Quando usar asyncio

- Use `async/await` quando a aplicação é I/O-bound: chamadas HTTP, banco de dados, filas
- Não use asyncio para código CPU-bound — use `concurrent.futures.ProcessPoolExecutor`
- Não misture código sync bloqueante dentro de funções `async` sem `asyncio.to_thread`

### Padrões

```python
import asyncio
from collections.abc import AsyncIterator
import httpx

async def fetch_users(ids: list[str]) -> list[User]:
    async with httpx.AsyncClient() as client:
        tasks = [fetch_one(client, uid) for uid in ids]
        return await asyncio.gather(*tasks)

async def stream_events(source_url: str) -> AsyncIterator[Event]:
    async with httpx.AsyncClient() as client:
        async with client.stream("GET", source_url) as response:
            async for line in response.aiter_lines():
                yield Event.parse(line)
```

- Use `asyncio.gather` para paralelizar I/O independente
- Use `asyncio.TaskGroup` (Python 3.11+) para grupos com cancelamento automático em falha
- Nunca use `asyncio.run` dentro de código já assíncrono — use `await`

## Anti-patterns

- `from módulo import *` — polui namespace, dificulta refatoração
- `except Exception: pass` — engole erros silenciosamente
- Instanciar dependências dentro de `__init__` — impede testes e troca de implementação
- Tipo de retorno `Any` sem justificativa — perde todo o valor dos type hints
- `Optional[X]` em vez de `X | None` no Python 3.10+ — verbosidade desnecessária
- Código de conexão/I/O no nível do módulo — torna import caro e dificulta testes
- Herança de 3+ níveis — use composição
- Misturar lógica de negócio com I/O na mesma função — viola separação de responsabilidades
- Usar `time.sleep` em código async — bloqueia o event loop; use `await asyncio.sleep`
- `assert` para validação de negócio — é removido com `python -O`; use exceções explícitas

---

## Planejamento de tarefas Python

Use esta seção quando precisar decompor uma funcionalidade ou projeto Python em tarefas concretas. O objetivo é produzir um plano executável — não uma lista de intenções vagas.

### Princípios de decomposição

- Cada tarefa deve ser implementável de forma independente, sem depender de outra tarefa incompleta
- Uma tarefa entregável é aquela que pode ser revisada em um PR por si só
- Prefira tarefas verticais (do modelo ao endpoint) a tarefas horizontais (primeiro todos os modelos, depois todos os repositórios)
- Identifique dependências técnicas antes de ordenar — bibliotecas externas, schemas de banco, contratos de API

### Estrutura de uma tarefa

Cada tarefa deve ter:

```
## [Número] Título curto e acionável

**O que fazer:** descrição objetiva do que será implementado
**Por que:** contexto ou decisão de design relevante (omitir se óbvio)
**Critérios de aceitação:**
- [ ] comportamento verificável 1
- [ ] comportamento verificável 2
**Dependências:** lista de tarefas que precisam estar prontas antes
**Arquivos afetados:** módulos, pacotes ou arquivos relevantes
```

### Checklist Python por tipo de tarefa

**Nova classe/módulo:**
- [ ] Type hints em todos os métodos públicos
- [ ] Docstring apenas se a interface não for autoexplicativa
- [ ] Exceções de domínio específicas, não genéricas
- [ ] Injeção de dependências pelo `__init__`
- [ ] Teste unitário cobrindo os caminhos principais

**Novo endpoint/handler:**
- [ ] Schema de entrada com validação (Pydantic ou similar)
- [ ] Schema de saída tipado
- [ ] Error handling com status HTTP corretos
- [ ] Teste de integração ou contrato

**Integração com serviço externo:**
- [ ] Verificar documentação atualizada via MCP ou web search
- [ ] Abstrair o cliente atrás de uma interface (`Protocol`)
- [ ] Tratar falhas e timeouts explicitamente
- [ ] Mock isolado nos testes unitários

**Refatoração:**
- [ ] Escopo claro — o que muda e o que não muda
- [ ] Testes existentes continuam passando sem alteração
- [ ] Sem mudança de comportamento observável

### Exemplo de decomposição

**Funcionalidade:** "Adicionar autenticação JWT à API"

```
## 1. Criar domínio de autenticação
O que fazer: classes Token e UserCredentials com type hints e validação
Critérios: token gerado com expiração, erro de domínio para credencial inválida
Arquivos: app/domain/auth.py

## 2. Implementar repositório de usuários
O que fazer: interface UserRepository (Protocol) + implementação SQLAlchemy
Critérios: find_by_email retorna User | None, senha comparada com hash
Dependências: #1
Arquivos: app/domain/ports.py, app/infra/repositories/user.py

## 3. Implementar middleware JWT
O que fazer: dependency do FastAPI que valida Bearer token e injeta usuário
Critérios: 401 em token inválido/expirado, usuário disponível no handler
Dependências: #1, #2
Arquivos: app/api/dependencies.py

## 4. Proteger endpoints existentes
O que fazer: adicionar dependency JWT nos routers que exigem autenticação
Critérios: endpoints retornam 401 sem token, 200 com token válido
Dependências: #3
Arquivos: app/api/routers/*.py
```

### O que evitar no planejamento

- Tarefas do tipo "implementar camada X inteira" — sem critério claro de conclusão
- Dependências circulares entre tarefas — reorganize a decomposição
- Misturar refatoração com nova funcionalidade na mesma tarefa — dificulta revisão
- Deixar decisões técnicas abertas para a hora da implementação — resolva no planejamento
