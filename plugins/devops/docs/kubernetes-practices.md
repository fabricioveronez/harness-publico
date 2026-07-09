# kubernetes-practices

Skill prescritiva e didática para manifests Kubernetes (YAML) na perspectiva de app developer — labels, deployments, services, probes, resource limits, ConfigMaps/Secrets, HPA, security context e ingress. Aplica convenções diretamente aos manifests, e tem guias de aprofundamento para quando o aluno quer entender o "porquê" das práticas.

Ativa sempre que a tarefa envolver escrever ou revisar manifests K8s, mesmo sem o usuário pedir explicitamente por "boas práticas".

## Estrutura

```
skills/kubernetes-practices/
├── SKILL.md                                 ← guia prescritivo (sempre carregado)
└── references/                              ← carregados sob demanda
    ├── anatomia-de-um-deployment.md         ← Pod/RS/Deployment/Service + ciclo de vida
    ├── probes-e-resiliencia.md              ← liveness/readiness/startup, PDB, replicas
    ├── recursos-e-scheduling.md             ← requests/limits, QoS, OOMKilled, HPA, namespaces
    └── configuracao-e-secrets.md            ← ConfigMap, Secret, montagem, rotação
```

O `SKILL.md` cobre o "o que fazer" (regras prescritivas). Os references explicam o "porquê" e cobrem casos do mundo real — incidentes, erros comuns de iniciante, anatomia de manifests linha a linha.

## Pré-requisitos e configuração

- Familiaridade com conceitos core de K8s (Pod, Deployment, Service, Ingress)
- Acesso a um cluster para validar (minikube, kind, k3d ou gerenciado)
- `kubectl` configurado com contexto apropriado

## Quando os references são carregados

| Cenário | Reference |
|---|---|
| Escrevendo primeiro Deployment, Service não roteia, entendendo Pod/Service/Deployment | `anatomia-de-um-deployment.md` |
| Configurando probes, CrashLoopBackOff, rolling update derruba tráfego, PDB | `probes-e-resiliencia.md` |
| Definindo requests/limits, pod em Pending, OOMKilled, HPA, namespaces | `recursos-e-scheduling.md` |
| Variáveis de ambiente, mudou ConfigMap e app não viu, certificados, rotação | `configuracao-e-secrets.md` |

## Skills relacionadas

- **docker-practices** — imagens seguem práticas compatíveis com execução em pods
- **github-actions-practices** — deploy de manifests via pipeline de CI/CD
- **terraform-practices** — provisionar o cluster e a infra ao redor

## Exemplos de uso

```
Revisa esse Deployment e aponta o que está fora do padrão

Adiciona probes, resource limits e security context nesse manifest

Cria um HPA para esse Deployment com scale baseado em CPU

Ajusta esse Service para usar ClusterIP + Ingress em vez de LoadBalancer direto

Converte esse manifest para rodar como non-root

Por que mudei o ConfigMap e a app não atualizou?
```

## Limitações conhecidas

- Perspectiva restrita a **app developer** — não cobre RBAC, NetworkPolicy, admission controllers, instalação de cluster nem observabilidade de cluster
- Não cobre **Helm** nem **Kustomize** — manifests puros apenas. Packaging e overlays ficam fora do escopo desta skill
- Não cobre operadores customizados (CRDs, controllers)
- Cloud-agnóstico — não aborda integrações específicas (IRSA, Workload Identity, Azure AD Pod Identity). Consulte documentação do provider
- Não substitui validadores automatizados (kubeval, kube-linter, Polaris) — é guia de escrita

## Para o aluno

Esta skill ilustra **progressive disclosure**: o `SKILL.md` é o "manual de bolso" prescritivo, e os references são as "aulas profundas" para entender de verdade os porquês. Você pode usar a skill sem nunca abrir os references — mas vai abrir quando quiser entender por que cada regra existe (ex: por que liveness e readiness não devem checar a mesma coisa), ou quando bater num problema real (ex: rolling update aparentemente correto, mas erros 502 nos logs).
