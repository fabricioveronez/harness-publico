# for_each vs count e armadilhas

> **Quando ler:** ao escrever recurso múltiplas vezes pela primeira vez, quando você removeu item da lista e o Terraform quer destruir/criar coisas que não deveria, antes de fazer refactor de state, ao usar `lifecycle` blocks.

## Índice

1. [O modelo mental: address de recurso](#o-modelo-mental-address-de-recurso)
2. [`count`: como funciona e por que machuca](#count-como-funciona-e-por-que-machuca)
3. [`for_each`: o jeito moderno](#for_each-o-jeito-moderno)
4. [Quando `count` ainda faz sentido](#quando-count-ainda-faz-sentido)
5. [Refatorando de count para for_each](#refatorando-de-count-para-for_each)
6. [`lifecycle` blocks: armadilhas comuns](#lifecycle-blocks-armadilhas-comuns)
7. [`moved {}`: refactor sem destruir state](#moved--refactor-sem-destruir-state)
8. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## O modelo mental: address de recurso

Cada recurso no Terraform tem um **address** único — a "chave primária" no state.

Recurso simples:

```hcl
resource "aws_instance" "api" {
  # ...
}
```

Address: `aws_instance.api`

Múltiplas instâncias com `count`:

```hcl
resource "aws_instance" "api" {
  count = 3
  # ...
}
```

Addresses: `aws_instance.api[0]`, `aws_instance.api[1]`, `aws_instance.api[2]`

Múltiplas instâncias com `for_each`:

```hcl
resource "aws_instance" "api" {
  for_each = toset(["primary", "replica1", "replica2"])
  # ...
}
```

Addresses: `aws_instance.api["primary"]`, `aws_instance.api["replica1"]`, `aws_instance.api["replica2"]`

**O address é como o Terraform identifica o recurso no state.** Se o address muda, o Terraform pensa que é um recurso diferente — destrói o "antigo" e cria o "novo".

Isso é o coração da diferença entre count e for_each.

## `count`: como funciona e por que machuca

```hcl
variable "instance_names" {
  default = ["api", "worker", "scheduler"]
}

resource "aws_instance" "services" {
  count         = length(var.instance_names)
  ami           = "ami-abc"
  instance_type = "t3.micro"

  tags = {
    Name = var.instance_names[count.index]
  }
}
```

State resultante:

```
aws_instance.services[0] — Name: api
aws_instance.services[1] — Name: worker
aws_instance.services[2] — Name: scheduler
```

Funciona. Mas observe o que acontece se você **remover "worker"** do meio:

```hcl
variable "instance_names" {
  default = ["api", "scheduler"]   # removeu "worker"
}
```

Novo state esperado:

```
aws_instance.services[0] — Name: api
aws_instance.services[1] — Name: scheduler
```

O que o Terraform calcula:

| Address | State antigo | Plan calculado |
|---|---|---|
| `aws_instance.services[0]` | `Name: api` | `Name: api` → **no change** ✓ |
| `aws_instance.services[1]` | `Name: worker` | `Name: scheduler` → **destroy worker, create scheduler** ✗ |
| `aws_instance.services[2]` | `Name: scheduler` | (não existe) → **destroy scheduler** ✗ |

**O Terraform vai destruir scheduler que estava bem, e recriar com nome scheduler.** Mas durante o intervalo, o recurso real não existe — você pode perder dados, IPs, dependências.

### Por que isso acontece

`count` indexa por **número**. Quando você remove item do meio, todos os subsequentes "deslocam" — `[2]` vira `[1]`. Mas o state já tem `[1]` mapeado para "worker". O address mudou de significado.

Esse comportamento existe porque o Terraform não tem como saber a "intenção" — pra ele, `aws_instance.services[1]` é o mesmo recurso, e o conteúdo mudou.

### O caso patológico

Cenário: 100 instâncias gerenciadas com `count`. Você remove a primeira da lista. Resultado:

- 1 destroy (a do final)
- 99 in-place updates (cada uma "vira" a próxima)
- Em recursos com mudanças que forçam recreate (mudança de instance_type, de subnet), você pode acabar **destruindo e recriando 99 instâncias**

Em produção, isso é catástrofe.

## `for_each`: o jeito moderno

Mesmo cenário, com `for_each`:

```hcl
resource "aws_instance" "services" {
  for_each      = toset(["api", "worker", "scheduler"])
  ami           = "ami-abc"
  instance_type = "t3.micro"

  tags = {
    Name = each.key
  }
}
```

State resultante:

```
aws_instance.services["api"]
aws_instance.services["worker"]
aws_instance.services["scheduler"]
```

Cada instância é endereçada pela **chave** ("api", "worker", "scheduler"), não pelo índice.

Remover "worker":

```hcl
for_each = toset(["api", "scheduler"])
```

Plan calculado:

| Address | Antes | Depois |
|---|---|---|
| `aws_instance.services["api"]` | existe | existe → **no change** ✓ |
| `aws_instance.services["worker"]` | existe | não existe → **destroy** ✓ |
| `aws_instance.services["scheduler"]` | existe | existe → **no change** ✓ |

Apenas o "worker" é destruído. Os outros não são tocados. Comportamento intuitivo.

### `for_each` com map

Quando você precisa de configuração diferente por item:

```hcl
resource "aws_instance" "services" {
  for_each = {
    api = {
      instance_type = "t3.medium"
      subnet_id     = "subnet-public"
    }
    worker = {
      instance_type = "t3.large"
      subnet_id     = "subnet-private"
    }
  }

  ami           = "ami-abc"
  instance_type = each.value.instance_type
  subnet_id     = each.value.subnet_id

  tags = {
    Name = each.key
  }
}
```

`each.key` é a chave do map ("api", "worker"). `each.value` é o valor.

### Referenciando recursos `for_each`

```hcl
# Acessar um específico
output "api_id" {
  value = aws_instance.services["api"].id
}

# Iterar todos
output "all_ids" {
  value = { for k, v in aws_instance.services : k => v.id }
  # → { api = "i-abc", worker = "i-def", scheduler = "i-ghi" }
}
```

## Quando `count` ainda faz sentido

`count` não é "ruim". Tem um caso onde brilha:

### Toggle binário (0 ou 1)

Recurso opcional, criado se condição for verdadeira:

```hcl
resource "aws_cloudwatch_alarm" "high_cpu" {
  count = var.enable_alarms ? 1 : 0

  alarm_name = "${var.name}-high-cpu"
  # ...
}
```

- Se `enable_alarms = true` → cria 1 alarm em `aws_cloudwatch_alarm.high_cpu[0]`
- Se `false` → não cria

Aqui count funciona perfeitamente — mudar de `0` para `1` cria o recurso, de `1` para `0` destroi.

### Em coleções, sempre `for_each`

Toda vez que você tem **lista de items diferentes**, prefira for_each. Indexação numérica gera surpresas.

## Refatorando de count para for_each

Você herda código com `count` e quer migrar para `for_each` sem destruir tudo.

### O problema

Antes (com count):
```
aws_instance.services[0]  ← Name: api
aws_instance.services[1]  ← Name: worker
```

Depois (com for_each):
```
aws_instance.services["api"]
aws_instance.services["worker"]
```

Os addresses mudam. Sem nenhum cuidado, Terraform vê:

- `aws_instance.services[0]` (state) → não está no código → **destroy**
- `aws_instance.services["api"]` (código) → não está no state → **create**

Resultado: destrói tudo e recria. Catástrofe.

### Solução 1 — `terraform state mv` (manual)

```bash
terraform state mv 'aws_instance.services[0]' 'aws_instance.services["api"]'
terraform state mv 'aws_instance.services[1]' 'aws_instance.services["worker"]'
```

Renomeia no state sem tocar nos recursos reais. Após isso, `terraform plan` mostra "no changes".

### Solução 2 — `moved {}` block (Terraform 1.1+)

Desde Terraform 1.1, você pode declarar movimento direto no código:

```hcl
moved {
  from = aws_instance.services[0]
  to   = aws_instance.services["api"]
}

moved {
  from = aws_instance.services[1]
  to   = aws_instance.services["worker"]
}
```

Terraform processa os `moved` blocks no plan e ajusta o state automaticamente. Vantagens:

- Versionado em Git
- Outros membros do time aplicam a mesma migração ao rodar plan
- Histórico claro do refactor

Você pode remover os `moved` blocks depois que todos os ambientes migraram.

## `lifecycle` blocks: armadilhas comuns

`lifecycle` é um meta-bloco que controla comportamento de criação/destruição:

```hcl
resource "aws_instance" "api" {
  # ...

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
    ignore_changes        = [tags]
  }
}
```

### `create_before_destroy = true`

Quando uma mudança força recreate, o padrão é **destruir antes de criar**. Para zero downtime:

```hcl
lifecycle {
  create_before_destroy = true
}
```

Cria o novo recurso primeiro, depois destrói o antigo. Útil para load balancers, target groups, instâncias com IP elástico.

**Pegadinha:** alguns recursos não suportam (chave primária precisa ser única). Se nome é igual, criar o segundo falha. Use nome dinâmico (`prefix` em vez de `name`).

### `prevent_destroy = true`

Bloqueia destruição. Para recursos sensíveis (banco de produção):

```hcl
resource "aws_db_instance" "prod" {
  # ...
  lifecycle {
    prevent_destroy = true
  }
}
```

Se alguém tentar destruir (ou se um plan calcular destroy), Terraform falha com erro.

**Pegadinhas:**
- `prevent_destroy = true` impede `terraform destroy` mesmo com `--auto-approve`
- Para realmente destruir, precisa **remover o lifecycle do código**, fazer plan/apply, e SÓ ENTÃO destruir
- Não impede destruição via console (drift)

### `ignore_changes = [...]`

Diz ao Terraform: "esse atributo pode ser alterado fora do meu controle, ignore".

Caso clássico: tags adicionadas por console/automação:

```hcl
lifecycle {
  ignore_changes = [tags]
}
```

Outro caso: senha rotacionada externamente:

```hcl
resource "aws_db_instance" "prod" {
  password = var.initial_password   # criação inicial
  # ...
  lifecycle {
    ignore_changes = [password]     # depois, ignora se mudou
  }
}
```

**Pegadinhas:**
- Você está abrindo mão da capacidade do Terraform de gerenciar esse atributo
- Drift fica permanente — não é detectado nem revertido
- Use só quando há razão real (rotação automática, automação externa)

### Combo perigoso: `create_before_destroy` + recursos com nome único

```hcl
resource "aws_iam_role" "api" {
  name = "api-role"   # nome fixo
  # ...
  lifecycle {
    create_before_destroy = true
  }
}
```

Mudança que força recreate:
1. Terraform cria nova role com nome `api-role`.
2. Já existe `api-role` (o antigo). API falha: `EntityAlreadyExists`.

Solução: use `name_prefix` em vez de `name`:

```hcl
resource "aws_iam_role" "api" {
  name_prefix = "api-role-"   # gera sufixo aleatório
  # ...
}
```

## `moved {}`: refactor sem destruir state

Já mencionado, vale aprofundar. `moved` é a ferramenta para qualquer renomeação:

### Renomear recurso

```hcl
# Antes
resource "aws_instance" "web_server" {
  # ...
}

# Depois
resource "aws_instance" "api" {
  # ...
}

moved {
  from = aws_instance.web_server
  to   = aws_instance.api
}
```

Terraform reconhece como mesma instância, só atualizado o address.

### Mover para dentro de módulo

```hcl
# Antes (root)
resource "aws_instance" "api" {
  # ...
}

# Depois (extraído para módulo)
module "api" {
  source = "./modules/api"
}

# Em modules/api/main.tf:
# resource "aws_instance" "this" { ... }

# No root:
moved {
  from = aws_instance.api
  to   = module.api.aws_instance.this
}
```

### Múltiplos `moved` em série

```hcl
# v1 → v2 → v3

moved {
  from = aws_instance.servers[0]            # v1
  to   = aws_instance.servers["primary"]    # v2
}

moved {
  from = aws_instance.servers["primary"]    # v2
  to   = module.compute.aws_instance.this   # v3
}
```

Terraform aplica em sequência.

### Limitações

- `moved` só funciona dentro do mesmo state. Para mover entre states, use `terraform state mv` + `terraform state pull/push`.
- Não funciona em recursos importados há pouco tempo sem refresh.

## Erros comuns de iniciante

### "Removi item do meio do array, perdi metade dos meus serviços"

Você usou `count`. Migre para `for_each` com `terraform state mv` ou `moved`.

### "Quero usar `for_each` mas a variable é `list(string)`"

`for_each` precisa de set ou map. Converte:

```hcl
for_each = toset(var.names)   # se a lista é única (sem duplicatas)
```

Se há possibilidade de duplicatas, decida o que fazer (`distinct(var.names)`) ou use map com chaves explícitas.

### "Mudei tags da resource e Terraform quer recriar tudo"

Provavelmente o resource provider trata mudanças de tags como force_new. Raríssimo, mas existe. Confira documentação. Se realmente é o caso, considere `ignore_changes = [tags]` ou aceite o recreate.

### "lifecycle prevent_destroy não impediu destroy via console"

Não impediria mesmo. `lifecycle` só age sobre operações do Terraform. Para proteção real contra destruição manual, use IAM policy ou Service Control Policy.

### "Apliquei `moved` e nada aconteceu"

Conferir:
- O `from` realmente existe no state (`terraform state list | grep ...`)
- O `to` é o address novo correto
- Você rodou `terraform apply` (ou ao menos `plan`) — moved é processado em plan

### "for_each com chaves dinâmicas baseadas em data source"

Cuidado: se o data source não pode ser conhecido em plan-time, `for_each` falha. Garanta que os keys são determinísticos:

```hcl
# Falha — data source não conhecido em plan
resource "aws_instance" "this" {
  for_each = toset(data.aws_subnets.private.ids)
  # ...
}
```

Pode ser necessário `-target` na primeira aplicação, ou estruturar para que os keys venham de variável.

### "Confundi `count.index` com `each.key`"

- `count.index` → número (0, 1, 2...)
- `each.key` → chave do for_each (string ou whatever)
- `each.value` → valor (quando for_each é map)

Quando converte de count para for_each, todos os `count.index` no código viram `each.key` (ou `each.value` dependendo do uso).

---

**Princípio que resume tudo:** o Terraform identifica recursos por **address no state**. `count` indexa por número (volátil — depende da ordem); `for_each` indexa por chave (estável — depende do nome). Em coleções de configuração, sempre `for_each`. `count` fica reservado para toggle binário. `moved` é a ferramenta para refatorar address sem perder recursos. Dominar isso é a diferença entre alguém que escreve Terraform e alguém que mantém infra real em produção sem destruir nada por engano.
