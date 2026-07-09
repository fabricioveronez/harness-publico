# Mentalidade IaC e state

> **Quando ler:** ao escrever Terraform pela primeira vez, quando outra pessoa edita recurso na console e seu apply quer destruir, quando você não sabe explicar por que `terraform.tfstate` precisa ficar em S3, quando alguém menciona "drift" e você quer entender.

## Índice

1. [O que IaC realmente significa](#o-que-iac-realmente-significa)
2. [O state: o que é e por que existe](#o-state-o-que-é-e-por-que-existe)
3. [Por que state local quebra em equipe](#por-que-state-local-quebra-em-equipe)
4. [Backend remoto + locking: a solução padrão](#backend-remoto--locking-a-solução-padrão)
5. [Drift: quando realidade e state divergem](#drift-quando-realidade-e-state-divergem)
6. [Separação de state: por ambiente, por blast radius](#separação-de-state-por-ambiente-por-blast-radius)
7. [Erros comuns de iniciante](#erros-comuns-de-iniciante)

---

## O que IaC realmente significa

Antes do Terraform, gente provisionava infraestrutura por:

- Console web (cliques)
- CLI manual (`aws ec2 run-instances --...`)
- Scripts shell ad-hoc

Problemas:
- Ninguém lembra exatamente o que fez
- Ambiente de staging "parecia igual" ao de produção mas não era
- Recriar do zero era impossível ou levava semanas
- Onboarding novo dev: "ah, o ambiente foi montado em 2019 pelo Marcos, ele saiu, ninguém sabe direito"

IaC é **descrever a infraestrutura como código declarativo, versionado, revisável**. O código é a fonte de verdade. Quem precisa do recurso lê o código, vê PR aprovado, sabe o porquê.

### Declarativo vs imperativo

```bash
# Imperativo — dá ordens passo a passo
aws ec2 create-vpc --cidr-block 10.0.0.0/16
aws ec2 create-subnet --vpc-id vpc-abc --cidr-block 10.0.1.0/24
aws ec2 create-internet-gateway
aws ec2 attach-internet-gateway --vpc-id vpc-abc --internet-gateway-id igw-xyz
```

Você diz "como fazer". Se rodar duas vezes, falha (já existe). Se uma chamada falhar no meio, fica estado inconsistente.

```hcl
# Declarativo — descreve estado desejado
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}
```

Você diz "o que deve existir". Terraform lê, compara com o que existe, calcula o **diff** e aplica só o necessário. Rodar 100 vezes seguidas com mesmo código: o resultado é igual.

A diferença não é estética. Declarativo escala. Imperativo, não.

### O ciclo do Terraform

```
┌─────────────┐     plan     ┌──────────────┐     apply    ┌───────────┐
│  Código .tf │  ────────►   │  Diff (plan) │  ──────────► │ Provider  │
│             │              │              │              │ (AWS, GCP)│
└─────────────┘              └──────────────┘              └─────┬─────┘
       ▲                            │                            │
       │                            │                            │
       └─────────── state ──────────┴──────── refresh ────────────┘
```

1. Você escreve `.tf` (estado desejado).
2. Terraform lê o **state** (o que ele acha que existe).
3. Faz **refresh**: consulta provider para ver o que **de fato** existe.
4. Calcula **plan**: o que precisa criar, alterar, destruir.
5. Você revisa, aprova.
6. **Apply**: provider executa as mudanças.
7. State é atualizado.

O state é a peça central que torna isso possível.

## O state: o que é e por que existe

`terraform.tfstate` é um arquivo JSON que mapeia **cada recurso no seu código a um ID real no provider**:

```json
{
  "resources": [
    {
      "type": "aws_instance",
      "name": "api",
      "instances": [{
        "attributes": {
          "id": "i-0abc123def456",
          "instance_type": "t3.micro",
          "private_ip": "10.0.1.42"
        }
      }]
    }
  ]
}
```

Sem state, Terraform não saberia que `aws_instance.api` no código corresponde à instância EC2 `i-0abc123def456` na AWS. Toda execução teria que descobrir do zero — lento e ambíguo (qual instância é "a api"?).

### O que o state guarda

- ID provider-specific de cada recurso
- Atributos lidos do provider (IP, ARN, hashes)
- Dependências entre recursos (calculadas)
- Outputs do módulo
- Versão do Terraform que aplicou

### Por que isso afeta seu trabalho

- **Imports**: ao adotar Terraform sobre infra existente, você usa `terraform import` para popular o state — sem isso, Terraform tentaria criar recursos novos.
- **Refactoring**: mudar o nome de um recurso no código (`resource "aws_instance" "old_name"` → `"new_name"`) sem mexer no state faz Terraform planejar **destruir** o old e **criar** o new. Você precisa de `moved {}` ou `terraform state mv`.
- **State drift** (próxima seção): se alguém mexer na console, o state fica desatualizado.

## Por que state local quebra em equipe

`terraform.tfstate` por padrão fica em `./terraform.tfstate` no diretório onde você roda. Para uma pessoa, funciona. Para equipe, problema imediato:

### Problema 1 — quem tem o state?

- Maria roda apply na máquina dela. State atualizado fica só lá.
- João tenta rodar apply na máquina dele (com state vazio). Terraform tenta criar tudo do zero — falha porque já existe.
- Maria tem que dar `terraform.tfstate` para o João. Por email? Por chat? Está num diretório local.

Caos.

### Problema 2 — race condition

- Maria começa apply (10 minutos para subir VPC).
- João, sem saber, começa apply ao mesmo tempo, com state mais antigo.
- Apply do João vê estado "vazio" e tenta criar VPC.
- Resultado: estado corrompido, VPC duplicada, apply do Maria falha no meio.

### Problema 3 — segredos no state

State tem **valores em texto puro**, incluindo:
- Senhas geradas (`random_password`)
- Connection strings
- Tokens de API
- Conteúdo de Secrets do K8s (quando você gerencia Secret via Terraform)

Commitar `terraform.tfstate` no Git = commitar senhas. Já aconteceu várias vezes.

## Backend remoto + locking: a solução padrão

A solução é **backend remoto** com **locking**:

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

O que isso significa:

- **Bucket S3** armazena o `tfstate`. Todos os devs do time têm acesso (via IAM).
- **DynamoDB table** serve de **lock**: enquanto um apply está rodando, ninguém mais consegue rodar. Lock libera ao terminar.
- **`encrypt = true`** garante encryption at rest no S3.

Outras combinações comuns:

| Backend | Locking | Plataforma |
|---|---|---|
| S3 + DynamoDB | DynamoDB | AWS |
| GCS | Object lock nativo | GCP |
| Azure Storage | Native blob lease | Azure |
| Terraform Cloud / HCP | Built-in | Multi-cloud, hospedado |
| `pg` (Postgres) | Built-in | Self-hosted |

### O que muda no fluxo

```
Maria roda apply →
  Terraform pega lock no DynamoDB →
  Lê state do S3 →
  Calcula plan →
  Aplica →
  Atualiza state no S3 →
  Libera lock

João roda apply ao mesmo tempo →
  Terraform tenta pegar lock →
  Lock ocupado →
  Espera (configurable timeout)
  Quando libera, pega lock →
  Lê state já atualizado →
  Aplica em cima
```

Sem race condition. Sem state local. Senha não fica em git.

### Configurando pela primeira vez

1. Crie bucket S3 com versionamento (recuperação se state corromper).
2. Crie tabela DynamoDB com primary key `LockID` (string).
3. Adicione `backend "s3"` ao seu `terraform { ... }`.
4. Rode `terraform init` — Terraform detecta novo backend e oferece migrar state existente.

**Versionamento no bucket** é importante: se um apply der ruim e corromper state, você pode voltar para versão anterior.

## Drift: quando realidade e state divergem

"Drift" é quando o estado real (na cloud) e o state do Terraform discordam.

### Cenário clássico

1. Você tem `aws_security_group.api` aberto na porta 80.
2. Em meio a um incidente noturno, alguém edita pela console e adiciona porta 8080.
3. Console: porta 80 + porta 8080. Estado real.
4. State do Terraform: só porta 80.
5. Próximo `terraform plan`: "vou remover porta 8080" — porque o código continua só com 80.

### O que fazer

Três respostas, dependendo do contexto:

#### 1. A mudança manual era certa — incorporar no código

Adicione porta 8080 ao Terraform. Rode plan — agora não tem diferença. Mudança documentada, próximo apply é no-op para isso.

#### 2. A mudança manual era errada — corrigir aplicando

`terraform apply` vai remover a porta 8080. Estado volta a casar com código.

#### 3. A mudança manual é temporária — não-aplicar agora

Adicione `lifecycle { ignore_changes = [ingress] }` para que o Terraform ignore esse atributo. Mudanças manuais não são revertidas. Você perde a "fonte única de verdade", mas em alguns casos é trade-off necessário.

### Como detectar drift

```bash
terraform plan
# se mostrar diff sem você ter mudado código, é drift
```

Em produção séria, rode `plan` periodicamente (ex: nightly) e alerte se houver diff. Existem ferramentas (`driftctl`, `tfsec`, `Terraform Cloud Drift Detection`) para isso.

### Por que drift é problema

- Apply do dia seguinte (em mudança não relacionada) vai reverter a mudança manual sem aviso
- Disaster recovery (recriar do código) não recupera ao estado real
- Perde-se a propriedade fundamental do IaC: "código é a verdade"

## Separação de state: por ambiente, por blast radius

Pergunta de iniciante: "uso um state pra tudo?"

Resposta: **não.** Separe por:

### 1. Por ambiente

```
state/
├── dev/terraform.tfstate
├── staging/terraform.tfstate
└── prod/terraform.tfstate
```

Razões:
- Apply em dev não pode acidentalmente afetar prod
- Permissões diferentes (dev é mais permissivo)
- Mudança em dev pode estar com bug; ela não chega em prod até passar staging

### 2. Por blast radius

Mesmo dentro de um ambiente, separe states quando o "raio de explosão" justifica:

```
state/
├── prod/
│   ├── network/terraform.tfstate          # VPC, subnets, gateways
│   ├── databases/terraform.tfstate         # RDS, DynamoDB
│   ├── api/terraform.tfstate               # ECS service da api
│   └── workers/terraform.tfstate           # ECS service dos workers
```

Vantagens:
- Apply na api não bloqueia apply nos workers
- Mudança em network não toca databases
- State menor = `terraform plan` mais rápido
- Erro humano no apply afeta menos coisa

### Acoplamento entre states

Quando state A precisa referenciar coisa de state B:

```hcl
# state "api" precisa do ID da VPC criada em state "network"

data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "myorg-terraform-state"
    key    = "prod/network/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_security_group" "api" {
  vpc_id = data.terraform_remote_state.network.outputs.vpc_id
}
```

Cuidado: você criou dependência entre states. Se mudar outputs do network, quem consome quebra.

Alternativa moderna: use **AWS SSM Parameter Store** ou **Vault** como "barramento" — network publica IDs lá, api consome. Menos acoplamento entre states.

### Anti-pattern: um state pra tudo

Você começa simples (1 state). 6 meses depois, são 200 recursos no mesmo state. `terraform plan` leva 5 minutos. Mudança em SQS bloqueia mudança em VPC. Apply em produção é cirurgia. Difícil voltar atrás.

Comece com a separação certa. Migrar state depois (`terraform state mv`, `terraform state rm`, `terraform import`) é trabalhoso e arriscado.

## Erros comuns de iniciante

### "Commitei terraform.tfstate no Git"

Senhas, tokens, ARNs sensíveis estão lá. Solução:

1. Considere os secrets vazados — gere novos.
2. Migre para backend remoto.
3. Apague o tfstate do Git e adicione ao `.gitignore`. Histórico do Git mantém versões antigas — purgue com `git filter-repo` se for crítico.

### "Apaguei terraform.tfstate por engano"

Você "perdeu" o mapeamento. Recursos continuam existindo na cloud, mas Terraform não os "vê" mais. Ao rodar apply, ele tentará criar tudo de novo (e vai falhar — recursos com nomes únicos já existem).

Recuperação:
- Bucket S3 com versionamento: volte para versão anterior
- Sem versionamento: `terraform import` recurso por recurso (chato, mas funcional)

Por isso: **versionamento no bucket de state sempre**.

### "Apply travou e o lock ficou pendurado"

Apply abortado violentamente (Ctrl+C duas vezes, máquina caiu) pode deixar o lock no DynamoDB sem dono. Próxima execução fica esperando.

```bash
terraform force-unlock <LOCK_ID>
```

Use só quando tem certeza que ninguém mais está rodando apply. `LOCK_ID` aparece na mensagem de erro.

### "Outro dev fez apply e quebrou meu plan"

Você fez `plan` há 20 minutos, ele aplicou no meio, agora seu plan está desatualizado. Refaça `plan` antes de `apply` — diff pode ter mudado.

Padrão profissional: sempre `plan` imediatamente antes de `apply`, idealmente com `-out=tfplan.bin` para amarrar:

```bash
terraform plan -out=tfplan.bin
# revisar
terraform apply tfplan.bin
```

`apply tfplan.bin` aplica **exatamente** o que o plan capturou — se algo mudou no meio, falha em vez de aplicar diferente.

### "Provider em módulo declarando provider"

Módulos reutilizáveis NÃO devem ter `provider {}` interno. Eles herdam do chamador. Se declarar interno, comportamento fica inconsistente quando o chamador tem múltiplos providers (multi-region, multi-account).

```hcl
# Em módulo reutilizável
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
# Não tem `provider "aws" {}` aqui — só required_providers
```

### "Por que `count` quebrou meu apply quando removi item do meio?"

Esse é tópico do `references/for-each-vs-count-e-armadilhas.md`. Resumo: `count` indexa por número; remover item do meio renomeia todos os seguintes no state. Use `for_each`.

### "Tudo num state só, mais simples"

Por agora. Com o tempo, vira problema. Pelo menos separe por ambiente desde o dia 1.

---

**Princípio que resume tudo:** Terraform é declarativo, mas precisa do state para fazer essa declaratividade funcionar contra um sistema mutável (a cloud). Cuidar bem do state — backend remoto, locking, versionamento, separação adequada — é o que diferencia "rodando Terraform" de "tendo IaC profissional".
