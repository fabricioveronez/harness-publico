---
name: typescript-practices
description: "Boas práticas e padrões de qualidade para código TypeScript. Use esta skill sempre que estiver escrevendo, revisando ou analisando código TypeScript — inclui convenções de código, type safety, orientação a objetos, error handling e organização. Ativar mesmo quando o usuário não pedir explicitamente por 'boas práticas', bastando que a tarefa envolva escrever ou revisar TypeScript."
---

# TypeScript Practices

Guia prescritivo de boas práticas para escrita e revisão de código TypeScript. Aplique estas convenções diretamente ao código sem explicar cada decisão — o objetivo é consistência e qualidade, não ensinar conceitos.

## Convenções de código

### Naming

- Variáveis e funções: `camelCase`
- Classes: `PascalCase`
- Interfaces: `PascalCase` sem prefixo `I` — use `UserService`, não `IUserService`
- Types: `PascalCase`
- Enums: `PascalCase` com membros em `PascalCase`
- Constantes globais: `UPPER_SNAKE_CASE`
- Arquivos: `kebab-case.ts`
- Nomes descritivos — prefira `getUserById` a `getUser` quando houver ambiguidade

### Interface vs Type

- `interface` para definir formas de objetos e contratos — tem mensagens de erro mais claras e suporta extensão natural
- `type` para unions, intersections e aliases de tipos primitivos
- Na dúvida, use `interface`

```typescript
// Interface para objetos
interface User {
  id: string;
  name: string;
  email: string;
}

// Type para unions e composições
type Status = "active" | "inactive" | "suspended";
type Result<T> = Success<T> | Failure;
```

### Enums

- Prefira `enum` para conjuntos fixos de valores com significado no domínio
- Use `as const` com objetos quando precisar de values como tipos

```typescript
enum OrderStatus {
  Pending = "PENDING",
  Confirmed = "CONFIRMED",
  Shipped = "SHIPPED",
  Delivered = "DELIVERED",
}
```

## Type Safety

### Regras fundamentais

- Use `unknown` em vez de `any` — force narrowing explícito antes de usar o valor
- Declare tipos de retorno em funções públicas e métodos de classe
- Use `readonly` para propriedades que não devem mudar após a criação
- Use optional chaining (`?.`) e nullish coalescing (`??`) para lidar com valores opcionais
- Evite type assertions (`as`) — prefira type guards quando precisar narrowing

### Null handling

- Prefira retornos explícitos a valores mágicos — `null` ou `undefined` com tipo declarado
- Use o pattern de early return para eliminar null checks aninhados

```typescript
function findUser(id: string): User | null {
  const user = this.repository.get(id);
  if (!user) {
    return null;
  }
  return user;
}
```

### Generics básicos

- Use generics quando o tipo de entrada determina o tipo de saída
- Nomeie o parâmetro com `T` para tipo principal, `K` para chaves, `V` para valores
- Adicione constraints com `extends` quando o generic precisar de propriedades específicas

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

## Orientação a Objetos

### Classes

- Use `private` para encapsular estado interno
- Use `readonly` para propriedades imutáveis
- Receba dependências pelo construtor
- Uma classe deve ter uma responsabilidade clara — se o nome precisa de "And" ou "Manager" genérico, considere dividir

```typescript
class OrderService {
  constructor(
    private readonly repository: OrderRepository,
    private readonly notifier: NotificationService
  ) {}

  async create(data: CreateOrderInput): Promise<Order> {
    const order = new Order(data);
    await this.repository.save(order);
    await this.notifier.send(order.userId, "Pedido criado");
    return order;
  }
}
```

### Abstract classes

- Use para definir comportamento base com métodos compartilhados
- Prefira sobre interfaces quando houver lógica reutilizável, não apenas contratos

```typescript
abstract class BaseRepository<T> {
  abstract findById(id: string): Promise<T | null>;
  abstract save(entity: T): Promise<void>;

  async findByIdOrFail(id: string): Promise<T> {
    const entity = await this.findById(id);
    if (!entity) {
      throw new NotFoundError(`Entity not found: ${id}`);
    }
    return entity;
  }
}
```

### Herança vs Composição

- Prefira composição para combinar comportamentos — herança profunda (mais de 2 níveis) é sinal de problema
- Use herança quando existir relação real de "é um" com comportamento compartilhado
- Use interfaces para definir contratos que múltiplas classes implementam

### Quando usar abordagem funcional

Orientação a objetos é o padrão, mas prefira funções puras em estas situações:
- Transformações de dados simples (map, filter, reduce)
- Funções utilitárias sem estado
- Handlers de eventos e callbacks
- Composição de operações pequenas e independentes

```typescript
// Funcional é mais natural aqui
const activeUsers = users.filter((u) => u.status === "active");
const emails = activeUsers.map((u) => u.email);

// OOP é mais natural aqui — estado + comportamento + ciclo de vida
class ShoppingCart {
  private items: CartItem[] = [];

  add(product: Product, quantity: number): void { ... }
  remove(productId: string): void { ... }
  get total(): number { ... }
}
```

## Error Handling

### Custom errors

- Crie classes de erro específicas para o domínio
- Inclua informações contextuais úteis para debugging

```typescript
class DomainError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = this.constructor.name;
  }
}

class NotFoundError extends DomainError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, "NOT_FOUND", 404);
  }
}

class ValidationError extends DomainError {
  constructor(
    message: string,
    public readonly field: string
  ) {
    super(message, "VALIDATION_ERROR", 400);
  }
}
```

### Async error handling

- Use try/catch em operações async com erros esperados
- Propague erros inesperados — não engula exceções com catch vazio
- Tipe os erros quando possível

```typescript
async function processOrder(id: string): Promise<Order> {
  const order = await orderRepository.findById(id);
  if (!order) {
    throw new NotFoundError("Order", id);
  }

  try {
    await paymentService.charge(order);
  } catch (error) {
    if (error instanceof PaymentDeclinedError) {
      order.cancel(error.reason);
      await orderRepository.save(order);
      throw error;
    }
    throw error; // erro inesperado — propaga
  }

  return order;
}
```

## Organização de código

### Estrutura de arquivos

- Um arquivo por classe principal ou módulo lógico
- Co-localize tipos com a implementação — não crie um arquivo `types.ts` gigante
- Separe tipos compartilhados em um módulo dedicado apenas quando usados em 3+ lugares
- Barrel exports (`index.ts`) apenas na raiz de módulos públicos, não em cada pasta

### Imports

- Agrupe imports: externos primeiro, depois internos, separados por linha em branco
- Use path aliases quando configurados no projeto

### Modularização

- Exporte apenas o que é público — mantenha helpers internos sem export
- Prefira funções e classes pequenas com responsabilidade única
- Evite arquivos com mais de 300 linhas — é sinal de que precisa dividir

## Patterns de referência

Para patterns mais detalhados com exemplos (discriminated unions, type guards, generics aplicados, async patterns), consulte `references/patterns.md`.
