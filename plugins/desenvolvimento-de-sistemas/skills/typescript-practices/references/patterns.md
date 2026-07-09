# TypeScript Patterns — Referência

Patterns práticos para situações recorrentes. Consulte quando precisar de exemplos detalhados.

## Sumário

1. [Discriminated Unions](#discriminated-unions)
2. [Type Guards](#type-guards)
3. [Generics Aplicados](#generics-aplicados)
4. [Async Patterns](#async-patterns)

---

## Discriminated Unions

Use para modelar estados que têm dados diferentes conforme o caso. O TypeScript consegue fazer narrowing automático pelo campo discriminante.

```typescript
interface Success<T> {
  status: "success";
  data: T;
}

interface Failure {
  status: "error";
  error: string;
  code: number;
}

interface Loading {
  status: "loading";
}

type AsyncState<T> = Success<T> | Failure | Loading;

function handle<T>(state: AsyncState<T>): string {
  switch (state.status) {
    case "success":
      return JSON.stringify(state.data); // TS sabe que é Success<T>
    case "error":
      return `Error ${state.code}: ${state.error}`; // TS sabe que é Failure
    case "loading":
      return "Loading...";
  }
}
```

**Quando usar:**
- Estados com dados variáveis (loading/success/error)
- Eventos com payloads diferentes por tipo
- Qualquer situação onde um `if/else` com type assertions seria a alternativa

**Checagem de exaustividade** — garante que todos os casos foram tratados:

```typescript
function assertNever(value: never): never {
  throw new Error(`Caso não tratado: ${value}`);
}

function handle<T>(state: AsyncState<T>): string {
  switch (state.status) {
    case "success":
      return JSON.stringify(state.data);
    case "error":
      return state.error;
    case "loading":
      return "Loading...";
    default:
      return assertNever(state); // erro de compilação se faltar um caso
  }
}
```

---

## Type Guards

Funções que ajudam o TypeScript a entender o tipo de um valor em runtime.

### typeof e instanceof

```typescript
function format(value: string | number): string {
  if (typeof value === "string") {
    return value.trim();
  }
  return value.toFixed(2);
}

function handleError(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  return String(error);
}
```

### Custom type guards

Use quando `typeof` e `instanceof` não são suficientes:

```typescript
interface Cat {
  meow(): void;
}

interface Dog {
  bark(): void;
}

function isDog(animal: Cat | Dog): animal is Dog {
  return "bark" in animal;
}

function makeSound(animal: Cat | Dog): void {
  if (isDog(animal)) {
    animal.bark(); // TS sabe que é Dog
  } else {
    animal.meow(); // TS sabe que é Cat
  }
}
```

### Assertion functions

Para validações que lançam erro se falharem:

```typescript
function assertIsString(value: unknown): asserts value is string {
  if (typeof value !== "string") {
    throw new Error(`Expected string, got ${typeof value}`);
  }
}

function process(input: unknown): string {
  assertIsString(input);
  return input.toUpperCase(); // TS sabe que é string a partir daqui
}
```

---

## Generics Aplicados

### Repository genérico

```typescript
interface Entity {
  id: string;
}

interface Repository<T extends Entity> {
  findById(id: string): Promise<T | null>;
  findAll(): Promise<T[]>;
  save(entity: T): Promise<void>;
  delete(id: string): Promise<void>;
}

class UserRepository implements Repository<User> {
  async findById(id: string): Promise<User | null> { ... }
  async findAll(): Promise<User[]> { ... }
  async save(entity: User): Promise<void> { ... }
  async delete(id: string): Promise<void> { ... }
}
```

### Response wrapper

```typescript
interface ApiResponse<T> {
  data: T;
  status: number;
  message: string;
}

function createResponse<T>(data: T, status: number = 200): ApiResponse<T> {
  return {
    data,
    status,
    message: status < 400 ? "OK" : "Error",
  };
}

// O tipo é inferido automaticamente
const response = createResponse({ id: "1", name: "João" });
// ApiResponse<{ id: string; name: string }>
```

### Service com generic constraint

```typescript
interface Identifiable {
  id: string;
}

interface Timestamped {
  createdAt: Date;
  updatedAt: Date;
}

class CrudService<T extends Identifiable & Timestamped> {
  constructor(private readonly repository: Repository<T>) {}

  async update(id: string, data: Partial<T>): Promise<T> {
    const entity = await this.repository.findById(id);
    if (!entity) {
      throw new NotFoundError("Entity", id);
    }
    const updated = { ...entity, ...data, updatedAt: new Date() };
    await this.repository.save(updated as T);
    return updated as T;
  }
}
```

---

## Async Patterns

### Execução paralela tipada

```typescript
async function loadDashboard(userId: string): Promise<Dashboard> {
  const [user, orders, notifications] = await Promise.all([
    userService.findById(userId),
    orderService.findByUser(userId),
    notificationService.getUnread(userId),
  ]);
  // Cada variável tem seu tipo correto inferido

  return { user, orders, notifications };
}
```

### Promise com timeout

```typescript
async function withTimeout<T>(
  promise: Promise<T>,
  ms: number
): Promise<T> {
  const timeout = new Promise<never>((_, reject) =>
    setTimeout(() => reject(new Error(`Timeout after ${ms}ms`)), ms)
  );
  return Promise.race([promise, timeout]);
}

const data = await withTimeout(fetchData(), 5000);
```

### Retry com tipagem

```typescript
async function retry<T>(
  fn: () => Promise<T>,
  attempts: number,
  delayMs: number = 1000
): Promise<T> {
  for (let i = 0; i < attempts; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === attempts - 1) {
        throw error;
      }
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  throw new Error("Unreachable");
}

const result = await retry(() => paymentService.charge(order), 3);
```
