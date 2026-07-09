# terraform-practices

Skill prescritiva e didática para código Terraform (HCL) cloud-agnóstico — estrutura de arquivos, naming, variables/outputs, módulos, state remoto, versionamento, for_each vs count e anti-patterns. Aplica convenções diretamente ao código, e tem guias de aprofundamento para quando o aluno quer entender o "porquê" das práticas.

Ativa sempre que a tarefa envolver escrever ou revisar código Terraform, mesmo sem o usuário pedir explicitamente por "boas práticas".

## Estrutura

```
skills/terraform-practices/
├── SKILL.md                                ← guia prescritivo (sempre carregado)
└── references/                             ← carregados sob demanda
    ├── mentalidade-iac-e-state.md          ← state, backend remoto, drift, separação
    ├── modulos-na-pratica.md               ← quando criar, anatomia, versionamento, providers
    └── for-each-vs-count-e-armadilhas.md   ← address de recurso, lifecycle, moved {}
```

O `SKILL.md` cobre o "o que fazer" (regras prescritivas). Os references explicam o "porquê" e cobrem casos do mundo real — incidentes, erros comuns de iniciante, exemplos comentados.

## Pré-requisitos e configuração

- Terraform 1.5+ (para `required_version` compatível com os exemplos e suporte a `moved {}`)
- Backend remoto configurado ao trabalhar em equipe (S3+DynamoDB, GCS, Azure Storage, Terraform Cloud)

## Quando os references são carregados

| Cenário | Reference |
|---|---|
| Primeiro Terraform, alguém edita pela console e seu apply quer reverter, state precisa ir pra S3 | `mentalidade-iac-e-state.md` |
| Copiando configuração entre ambientes pela 3ª vez, primeiro módulo, consumindo módulo de registry | `modulos-na-pratica.md` |
| Primeira vez com `count`/`for_each`, removeu item do meio do array deu errado, refactor de state | `for-each-vs-count-e-armadilhas.md` |

## Skills relacionadas

- **github-actions-practices** — execução de `terraform plan`/`apply` em pipelines com OIDC
- **kubernetes-practices** — provisionar o cluster e gerar manifests/Helm releases via Terraform

## Exemplos de uso

```
Revisa esses arquivos .tf e aponta o que está fora do padrão

Refatora esse módulo Terraform seguindo boas práticas

Organiza esse main.tf separando em variables.tf, outputs.tf, versions.tf

Converte esse count para for_each nesse resource

Adiciona backend remoto com locking nesse projeto

Por que removi item do array e o Terraform quer destruir 5 recursos?
```

## Limitações conhecidas

- Cloud-agnóstico — não aborda recursos específicos de AWS/GCP/Azure em detalhe. Convenções estruturais aplicam-se a qualquer provider, mas padrões específicos de cada cloud (IAM, VPC, networking) ficam fora do escopo
- Não cobre **OpenTofu** explicitamente — práticas aplicam-se, mas exemplos assumem Terraform CLI da HashiCorp
- Não cobre **Terragrunt** — gerenciamento multi-ambiente aqui é via separação nativa de state e diretórios
- Não substitui validadores (tflint, tfsec, Checkov) — é guia de escrita
- Pulumi/CDK não são cobertos — skill foca exclusivamente em HCL

## Para o aluno

Esta skill ilustra **progressive disclosure**: o `SKILL.md` é o "manual de bolso" prescritivo, e os references são as "aulas profundas" para entender de verdade os porquês. O reference `for-each-vs-count-e-armadilhas.md`, em particular, é um caso clássico de "regra que parece arbitrária até você quebrar produção uma vez" — vale ler antes da quebrar.
