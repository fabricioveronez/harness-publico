# Módulos na prática

> **Quando ler:** ao copiar-colar configuração entre ambientes pela segunda ou terceira vez, antes de criar seu primeiro módulo, ao consumir um módulo do registry e não saber o que esperar, quando o time pergunta "como a gente padroniza isso?".

## Índice

1. [O que é um módulo (e o que NÃO é)](#o-que-é-um-módulo-e-o-que-não-é)
2. [Quando criar e quando NÃO criar módulo](#quando-criar-e-quando-não-criar-módulo)
3. [Anatomia de um módulo bem desenhado](#anatomia-de-um-módulo-bem-desenhado)
4. [Variables e outputs como contrato público](#variables-e-outputs-como-contrato-público)
5. [Versionamento: source, ref, version](#versionamento-source-ref-version)
6. [Providers em módulos: por que NÃO declarar](#providers-em-módulos-por-que-não-declarar)
7. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## O que é um módulo (e o que NÃO é)

Módulo Terraform é **um diretório com arquivos `.tf` que pode ser instanciado múltiplas vezes**. Ponto.

```
modules/
  api/
    main.tf
    variables.tf
    outputs.tf
    versions.tf
```

Você consome assim:

```hcl
module "orders_api" {
  source = "./modules/api"

  name          = "orders"
  replica_count = 3
  environment   = "prod"
}

module "users_api" {
  source = "./modules/api"

  name          = "users"
  replica_count = 2
  environment   = "prod"
}
```

Mesmo módulo, dois consumos com inputs diferentes. Cria duas APIs com configuração igual mas inputs distintos.

### O que NÃO é módulo

- **Não é "biblioteca compartilhada de funções"**. Terraform é declarativo; módulo declara recursos, não procedimentos.
- **Não é "framework de abstração"**. Não tente criar módulo "genérico para tudo" — fica complicado de usar.
- **Não é "wrapper que esconde detalhes do provider"**. Se o módulo só envolve um único `aws_instance`, é overkill.

### Tipos de módulo (informalmente)

| Tipo | Exemplo | Quem cria |
|---|---|---|
| **Root module** | O diretório onde você roda `terraform apply` | Você |
| **Child module local** | `./modules/...` | Você ou time |
| **Child module remoto (privado)** | `git::https://github.com/myorg/tf-modules.git//api?ref=v1.0.0` | Time/empresa |
| **Módulo público** | `terraform-aws-modules/vpc/aws` (registry) | Comunidade |

## Quando criar e quando NÃO criar módulo

### Crie módulo quando

- O mesmo conjunto de recursos aparece em **2+ lugares com variação controlada**
- Você quer **padronizar** algo no time (ex: toda app web tem ALB + ECS + log group da mesma forma)
- A configuração é **complexa o suficiente** que esconder detalhes ajuda

### NÃO crie módulo quando

- Vai usar uma vez só (YAGNI)
- É um wrapper fino sobre um único recurso (`aws_instance` que só repassa variáveis)
- Você ainda não entende bem o domínio (criar módulo cedo = abstrair errado)

### Heurística

> **Regra dos três**: copie-cole 2 vezes. Na terceira, considere extrair módulo.

A primeira vez ensina a forma. A segunda revela variações. Na terceira, você já sabe quais são as variáveis reais e quais detalhes esconder.

### Anti-pattern: módulo gigante

Módulos com 200+ recursos são difíceis de:

- Revisar (PR enorme)
- Apply (lento, blast radius enorme)
- Versionar (toda mudança afeta todos os consumidores)

Quebra em módulos menores que se compõem. Pequeno é bonito.

## Anatomia de um módulo bem desenhado

```
modules/api/
├── main.tf          # recursos principais
├── variables.tf     # contrato de entrada
├── outputs.tf       # contrato de saída
├── versions.tf      # required_providers + required_version
├── locals.tf        # valores computados (opcional)
├── data.tf          # data sources (opcional)
└── README.md        # como usar
```

### `versions.tf` — primeira coisa a criar

```hcl
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 6.0"
    }
  }
}
```

**Não declara `provider {}` aqui** — só `required_providers`. Veja seção dedicada.

### `variables.tf` — interface de entrada

```hcl
variable "name" {
  description = "Nome lógico do serviço (ex: orders, users)"
  type        = string

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{1,30}$", var.name))
    error_message = "name deve ser lowercase, alfanumérico, com hífen, 2-31 chars."
  }
}

variable "environment" {
  description = "Ambiente de deploy"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment precisa ser dev, staging ou prod."
  }
}

variable "replica_count" {
  description = "Número de réplicas. Mínimo 2 em prod."
  type        = number
  default     = 2

  validation {
    condition     = var.replica_count >= 1 && var.replica_count <= 50
    error_message = "replica_count entre 1 e 50."
  }
}

variable "tags" {
  description = "Tags adicionais aplicadas a todos os recursos"
  type        = map(string)
  default     = {}
}
```

### `main.tf` — os recursos

```hcl
locals {
  name_prefix = "${var.environment}-${var.name}"

  default_tags = {
    Environment = var.environment
    Service     = var.name
    ManagedBy   = "terraform"
  }

  tags = merge(local.default_tags, var.tags)
}

resource "aws_ecs_service" "this" {
  name            = local.name_prefix
  cluster         = data.aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = var.replica_count

  tags = local.tags
}

# ... mais recursos
```

### `outputs.tf` — interface de saída

```hcl
output "service_arn" {
  description = "ARN do serviço ECS criado"
  value       = aws_ecs_service.this.id
}

output "task_role_arn" {
  description = "ARN da IAM role da task — útil para anexar políticas adicionais"
  value       = aws_iam_role.task.arn
}

output "log_group_name" {
  description = "Nome do log group CloudWatch"
  value       = aws_cloudwatch_log_group.this.name
}
```

### `README.md` — como usar

Mesmo que ninguém leia, escreva. Daqui a 6 meses você não vai lembrar:

```markdown
# api module

Cria um serviço ECS Fargate com ALB target group, log group e IAM role.

## Uso

\`\`\`hcl
module "orders_api" {
  source = "git::https://github.com/myorg/tf-modules.git//api?ref=v1.2.0"

  name          = "orders"
  environment   = "prod"
  replica_count = 3
}
\`\`\`

## Outputs

- `service_arn` — para referenciar em IAM policies
- `task_role_arn` — para anexar policies adicionais
- `log_group_name` — para criar metric filters

## Pre-requisitos

- Cluster ECS chamado `${environment}-cluster` deve existir
- VPC e subnets configurados conforme [doc-de-rede]
```

## Variables e outputs como contrato público

Variables e outputs são a **API pública** do módulo. Mudar eles **quebra todos os consumidores**.

### Princípios para variables

1. **Toda variable tem `description`** — não é só boas maneiras, é exigido (linter falha sem isso).
2. **`type` explícito sempre** — `type = any` é vago e falha em runtime em vez de em plan.
3. **`default` apenas quando faz sentido universal** — caso contrário, força o consumidor a decidir.
4. **`validation`** para restringir valores — feedback rápido em vez de erro no apply.
5. **`sensitive = true`** em credenciais — não aparece em logs do plan/apply.

```hcl
variable "database_password" {
  description = "Senha master do banco. Use random_password ou Secrets Manager."
  type        = string
  sensitive   = true
}
```

### Princípios para outputs

1. **Toda output tem `description`**.
2. **`sensitive = true`** quando o valor não deve aparecer em logs.
3. **Exporte só o que faz sentido externamente** — se o atributo é detalhe interno, não exporte. Adicionar é fácil; remover quebra consumidores.
4. **Use outputs para valores que outros módulos/recursos do consumidor precisam**, não para "documentar" valores internos.

### Compatibilidade retro

Quando você muda módulo, lembre que outros estão consumindo:

- **Adicionar nova variable opcional** (com default) → breaking? Não. OK.
- **Adicionar nova variable obrigatória** → breaking. Bump major version.
- **Renomear variable** → breaking. Bump major version, ou mantenha alias.
- **Adicionar output** → não breaking. OK.
- **Remover output** → breaking. Bump major version.
- **Mudar tipo de variable** → breaking quase sempre. Bump major.

## Versionamento: source, ref, version

Onde o módulo mora muda como você o referencia.

### Local

```hcl
module "api" {
  source = "./modules/api"
  # ...
}
```

Bom para: protótipos, módulos só usados num root específico.
Ruim para: compartilhar entre múltiplos roots, controle de versão (não versiona).

### Git (privado)

```hcl
module "api" {
  source = "git::https://github.com/myorg/tf-modules.git//api?ref=v1.2.0"
  # ...
}
```

Anatomia:
- `git::https://github.com/myorg/tf-modules.git` → repositório
- `//api` → subdirectory dentro do repo (módulo `api/` na raiz)
- `?ref=v1.2.0` → tag git

**`ref` sempre pinada**:
- ✅ `?ref=v1.2.0` (tag)
- ✅ `?ref=abc123def` (commit SHA — máxima imutabilidade)
- ❌ `?ref=main` (mutável, frágil — main pode mudar amanhã)

### Terraform Registry (público)

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"
  # ...
}
```

- `version = "~> 5.0"` → "qualquer 5.x, mas não 6.0" (pessimistic constraint)
- `version = "5.1.2"` → exata
- `version = ">= 5.0, < 6.0"` → range

### Terraform Registry (privado, da empresa)

Plataformas como Terraform Cloud, JFrog, Spacelift hospedam registry privado. Sintaxe similar ao público.

### Por que pinning importa

Cenário real:

1. Você consome `module "api" { source = "...//api?ref=main" }` há 3 meses, tudo funcionando.
2. Maintainer do módulo merge PR que muda comportamento default (ex: muda CIDR padrão).
3. Você roda `terraform plan` para uma mudança não-relacionada.
4. Plan mostra diff inesperado: módulo quer alterar CIDR.
5. 3 horas debugando até descobrir que `main` mudou.

Pin por tag/SHA evita esse cenário. Atualizações ficam **deliberadas**.

## Providers em módulos: por que NÃO declarar

Iniciantes copiam isso de exemplo:

```hcl
# DENTRO de um módulo reutilizável — RUIM

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {           # ← problema aqui
  region = var.region
}

resource "aws_instance" "this" {
  # ...
}
```

Por que é problema:

### 1. Configuração fica fragmentada

Quem chama o módulo não tem controle sobre como o provider é configurado dentro dele. Se o consumidor quer multi-region, multi-account, ou usar um alias específico, o módulo já decidiu.

### 2. Múltiplas instâncias do módulo viram um pesadelo

Cenário: você usa o mesmo módulo em 3 regions:

```hcl
module "api_us" {
  source = "./modules/api"
  region = "us-east-1"
}

module "api_eu" {
  source = "./modules/api"
  region = "eu-west-1"
}

module "api_ap" {
  source = "./modules/api"
  region = "ap-southeast-1"
}
```

Se o módulo declarar `provider "aws"` interno, cada instância cria seu próprio provider — e a configuração é local àquele módulo. Difícil compartilhar IAM, hard de debugar.

### 3. Padrão correto: módulo só declara `required_providers`

```hcl
# DENTRO do módulo

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source                = "hashicorp/aws"
      version               = "~> 5.0"
      configuration_aliases = [aws.replica]   # opcional, se precisa de alias
    }
  }
}

# SEM provider {} aqui

resource "aws_instance" "this" {
  # ...
}
```

`required_providers` declara **o que o módulo precisa**, sem **como configurar**.

### 4. Consumidor configura

```hcl
# NO ROOT do consumidor

provider "aws" {
  alias  = "us"
  region = "us-east-1"
}

provider "aws" {
  alias  = "eu"
  region = "eu-west-1"
}

module "api_us" {
  source = "./modules/api"
  providers = {
    aws = aws.us
  }
}

module "api_eu" {
  source = "./modules/api"
  providers = {
    aws = aws.eu
  }
}
```

Configuração centralizada no root, módulo permanece "puro" e reutilizável.

### Quando módulo PODE declarar `provider {}`

**Apenas no root module.** O `terraform apply` que você roda vem de algum lugar — esse lugar é o root, e ele precisa declarar providers. Mas qualquer módulo que outros vão consumir, não.

## Erros comuns de iniciante

### "Criei módulo na primeira vez que usei"

Provavelmente abstraiu errado. Use 2-3 vezes em formato concreto, depois extraia. Refactoring tarde > abstração cedo errada.

### "Mudei nome de variable e quebrei produção"

Variables são API pública. Mudança = breaking. Caminho seguro:

1. Adicione variable nova com default.
2. Use a nova internamente, mantém a antiga como alias (`coalesce`, `try`).
3. Avise consumidores, deprecando a antiga.
4. Em major version, remove a antiga.

### "`?ref=main` é prático no dia-a-dia"

Até o dia que quebra. Pinning custa 5 segundos por update; debug de regressão custa horas.

### "Por que meu módulo não funciona em multi-region?"

Provavelmente ele declara `provider {}` interno. Refatore para só `required_providers` e deixe o consumidor passar via `providers = { aws = aws.us }`.

### "Output sem `sensitive = true` vazou no log do CI"

Plan/apply imprime outputs em texto plain a menos que sensitive. Adicione e refaça o CI.

### "Module wrapper sobre um único resource — fica bonito?"

Não. É indireção sem ganho. Use o resource direto. Crie módulo quando há **composição** (vários recursos relacionados), não envelopamento.

### "Esqueci de criar README e o time pergunta como usar"

README mínimo (descrição + exemplo + outputs principais) economiza muitas mensagens. Faça quando criar.

### "Quero módulo super genérico, com 50 variables"

Provavelmente você está tentando abstrair demais. Módulo bom é **opinativo** — toma decisões em vez de delegar todas. Se precisar de outra variante, crie outro módulo (ou variant via `count`/`for_each`), não infla o existente.

---

**Princípio que resume tudo:** módulos são contratos. Inputs (variables), saídas (outputs), comportamento. Bem desenhados, escalam o time — todo mundo cria coisa do mesmo jeito sem reinventar. Mal desenhados, viram dívida que ninguém quer mexer. Comece simples, evolua com base em uso real.
