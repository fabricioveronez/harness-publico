---
name: terraform-practices
description: "Boas práticas e padrões de qualidade para código Terraform (HCL) — cloud agnóstico. Use esta skill sempre que estiver escrevendo, revisando ou refatorando arquivos .tf, .tfvars, terraform.lock.hcl, estruturando módulos ou discutindo state management. Cobre estrutura de arquivos, naming, variables/outputs, módulos, state remoto, locking de versões, for_each vs count, data sources e anti-patterns. Ativar mesmo quando o usuário não pedir explicitamente por 'boas práticas', bastando que a tarefa envolva código Terraform. Exemplos usam providers agnósticos (random, null, local) — as convenções aplicam-se a qualquer provider de cloud."
---

# Terraform Practices

Guia prescritivo de boas práticas para código Terraform. Aplique estas convenções diretamente ao código sem explicar cada decisão — o objetivo é consistência, reprodutibilidade e segurança, não ensinar conceitos.

As convenções são cloud-agnósticas. Exemplos usam providers `random`, `null` e `local` para ilustrar estrutura sem amarrar a provider específico.

## Quando aprofundar

Os guias em `references/` aprofundam o "porquê" das práticas e cobrem casos do mundo real. Carregue sob demanda quando:

| Cenário | Reference |
|---|---|
| Escrevendo Terraform pela primeira vez, ou alguém edita pela console e seu apply quer reverter, ou state precisa ir pra S3 | `references/mentalidade-iac-e-state.md` |
| Copiando configuração entre ambientes pela 3ª vez, antes de criar primeiro módulo, consumindo módulo de registry | `references/modulos-na-pratica.md` |
| Primeira vez usando `count` ou `for_each`, removendo item do meio do array deu errado, refatorando state, usando `lifecycle` | `references/for-each-vs-count-e-armadilhas.md` |

## Estrutura de arquivos

Todo módulo (root ou reutilizável) tem estes arquivos canônicos:

- `main.tf` — recursos principais
- `variables.tf` — todas as variables de entrada
- `outputs.tf` — todos os outputs
- `versions.tf` — `required_version` + `required_providers`
- `providers.tf` — configuração dos providers (apenas em root; módulos reutilizáveis não declaram providers)
- `locals.tf` — valores computados reutilizáveis (quando necessário)
- `data.tf` — data sources (quando numerosos)

Ordem preferida dentro de cada arquivo: `terraform {} → provider {} → data → locals → resource → output`.

## Naming

- Recursos, variables, outputs e locals: `snake_case`
- Nomes descritivos — `primary` / `replica`, não `first` / `second`
- Não inclua o tipo do recurso no nome — `random_pet.api`, não `random_pet.api_pet`
- Nomes reais de infraestrutura (tags, nomes de recursos na cloud): siga a convenção do provider (geralmente `kebab-case`)

```hcl
# Bom
resource "random_pet" "api_prefix" {
  length    = 2
  separator = "-"
}

# Ruim — tipo no nome
resource "random_pet" "api_prefix_pet" {
  length = 2
}
```

## Variables

- Toda variable tem `description` obrigatória — não é só útil, é exigido
- Declare `type` explícito — nunca `type = any`
- `default` apenas quando faz sentido universal; caso contrário, force o chamador a decidir
- Use `validation` para restringir valores válidos
- `sensitive = true` em credenciais, tokens e qualquer valor que não deve aparecer em logs

```hcl
variable "environment" {
  description = "Ambiente de deploy (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "environment precisa ser dev, staging ou prod."
  }
}

variable "replica_count" {
  description = "Número de réplicas. Mínimo 2 em produção."
  type        = number
  default     = 2
}

variable "api_token" {
  description = "Token de autenticação para API externa"
  type        = string
  sensitive   = true
}
```

## Outputs

- Todo output tem `description`
- `sensitive = true` quando o valor não deve aparecer em logs do plan/apply
- Exporte apenas o que outros módulos/consumidores realmente precisam — outputs são a interface pública do módulo

```hcl
output "api_endpoint" {
  description = "URL pública da API"
  value       = "https://${local.domain}"
}

output "database_password" {
  description = "Senha do banco gerada pelo módulo"
  value       = random_password.db.result
  sensitive   = true
}
```

## Módulos

### Quando criar

- Crie módulo quando o mesmo conjunto de recursos é usado em 2+ lugares com variação controlada
- Não crie "wrapper fino" sobre um único recurso — abstração que não agrega valor, só sobrecarga
- Módulo deve ter interface clara (variables bem definidas, outputs mínimos)

### Estrutura

```
modules/
  my-module/
    main.tf
    variables.tf
    outputs.tf
    versions.tf
    README.md
```

### Versionamento

- Use tags git para versionar módulos — `ref=v1.2.0`
- Pinne a versão na chamada — nunca `ref=main`
- Para registros públicos (Terraform Registry), use `version = "~> 1.2"` (pessimistic constraint)

```hcl
module "api" {
  source  = "git::https://github.com/org/tf-modules.git//api?ref=v1.2.0"

  environment   = var.environment
  replica_count = 3
}
```

### Providers em módulos

- Módulos reutilizáveis **não declaram `provider {}`** — recebem do chamador
- Declaram `required_providers` em `versions.tf` para documentar compatibilidade

## State management

### Remote backend (obrigatório em equipe)

- State local (`terraform.tfstate` em disco) apenas em experimentos pessoais
- Qualquer equipe precisa de backend remoto com locking (S3+DynamoDB, GCS, Azure Storage, Terraform Cloud)
- Locking previne apply concorrente corrompendo state

```hcl
terraform {
  backend "s3" {
    bucket         = "myorg-terraform-state"
    key            = "prod/api/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
```

### Separação por ambiente

- Separe state por ambiente (dev/staging/prod) via `key` diferente no backend
- Nunca use um único state para todos os ambientes — blast radius enorme

### Sensibilidade do state

- State pode conter secrets em plain text (`sensitive = true` mascara logs, não o state)
- Backend deve ter encryption at rest + controle de acesso restrito

## Versões travadas

### `versions.tf`

- Sempre declare `required_version` do Terraform e `required_providers` com versões pinadas
- Use pessimistic constraint (`~>`) — aceita patches, não minor/major

```hcl
terraform {
  required_version = "~> 1.7"

  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}
```

### `terraform.lock.hcl`

- Sempre commitar `.terraform.lock.hcl` — garante que todos usam exatamente os mesmos providers
- Atualize com `terraform init -upgrade` deliberadamente, revisando o diff

## for_each vs count

### Prefira `for_each`

- `for_each` usa chaves nomeadas — recursos permanecem estáveis quando a coleção muda
- `count` usa índices — remover item do meio renomeia todos os seguintes no state, causando destruir+recriar

```hcl
# Bom — for_each com chaves estáveis
resource "random_pet" "services" {
  for_each = toset(["api", "worker", "scheduler"])
  length   = 2
}

# Ruim — count, remoção do meio quebra
resource "random_pet" "services" {
  count  = length(var.services)
  length = 2
}
```

### Use `count` apenas para toggle

- `count = var.enabled ? 1 : 0` — padrão aceitável para recursos opcionais binários
- Para coleções, sempre `for_each`

## Data sources

- Prefira `data` a hardcoded IDs quando referenciando recursos existentes fora do state
- Data sources adicionam dependência implícita ao plan — entenda o custo de rede por execução

## Tags e labels consistentes

- Defina tags/labels em `locals` e aplique em todos os recursos via `merge()`
- Tags recomendadas: `Environment`, `ManagedBy`, `Service`, `Owner`

```hcl
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Service     = var.service_name
    Owner       = var.team
  }
}

resource "aws_s3_bucket" "logs" {
  bucket = "logs-${var.environment}"
  tags   = merge(local.common_tags, { Component = "logs" })
}
```

## Fluxo de apply

- `terraform fmt` e `terraform validate` em todo PR (automatizar em CI)
- `terraform plan` revisado antes de qualquer `apply` — nunca `apply -auto-approve` em produção sem plan explícito
- Em produção, plan e apply são passos separados com aprovação humana entre eles

## Anti-patterns

- Secrets hardcoded em `.tf` ou `.tfvars` commitados
- State local em equipe
- Um único state para dev/staging/prod
- `count` para coleções mutáveis
- Módulos que declaram `provider {}` internamente (exceto root)
- Variables sem `description` ou sem `type`
- `required_version` ausente
- `.terraform.lock.hcl` não commitado
- `terraform apply -auto-approve` em produção sem plan prévio aprovado
- Módulos monolíticos (200+ recursos) — difícil revisar, blast radius enorme
- `terraform destroy` em produção como atalho para recriar — prefira `terraform apply -replace=<recurso>`
