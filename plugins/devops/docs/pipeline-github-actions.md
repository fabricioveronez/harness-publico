# pipeline-github-actions

Skill que leva pipelines do GitHub Actions do YAML até um run verde comprovado. Ela escreve e revisa workflows com boas práticas (triggers, permissions, OIDC, secrets, cache, concurrency, reuso, pinning) e conduz o ciclo operacional inteiro: preflight do repositório e das dependências externas, secrets e variables a partir de `.env` sem vazar valores, disparo em etapas (PR → merge → main/dispatch), acompanhamento do run, leitura de log, correção, rerun e verificação de ponta a ponta do que a pipeline entregou.

Substitui a antiga `github-actions-practices`, cujo conteúdo virou o reference `boas-praticas-yaml.md`. Nasceu da análise de sessões reais em que três pipelines (CI de app com publicação no Docker Hub, provisionamento Terraform + Ansible e deploy em K3s com dispatch entre repositórios) foram levadas ao verde. As falhas e os retrabalhos dessas sessões viraram o preflight, o catálogo de falhas e as regras da skill.

## Estrutura

```
skills/pipeline-github-actions/
├── SKILL.md                            ← princípios + fluxo em 10 fases (sempre carregado)
├── references/                         ← carregados sob demanda
│   ├── boas-praticas-yaml.md           ← regras de escrita + "Lições de pipelines reais"
│   ├── anatomia-de-um-workflow.md      ← workflow/job/step, contexto, expressões
│   ├── seguranca-em-pipelines.md       ← pull_request_target, OIDC, permissions, pinning
│   ├── performance-e-reuso.md          ← cache, matrix, concurrency, reusable, composite
│   ├── preflight.md                    ← o que checar antes do 1º run, com relatório pronto × falta
│   ├── comandos-gh.md                  ← secrets, runs, logs, rerun, PR, PAT de dispatch
│   └── catalogo-de-falhas.md           ← sintoma → causa → correção
└── scripts/
    ├── env-para-gh.py                  ← .env → secrets/variables (dry-run padrão, valores via stdin)
    ├── esperar-run.sh                  ← espera o run pelo SHA, acompanha e mostra os jobs
    └── log-falha.sh                    ← log dos jobs falhos, limpo e filtrado
```

## O fluxo

0. **Mapear** workflows × gatilhos × jobs e o inventário de `secrets.*`/`vars.*`
1. **Escrever/ajustar** o YAML com as boas práticas
2. **Validar localmente** (actionlint, terraform validate, ansible-lint)
3. **Preflight**: plano da conta, repositório, credenciais e dependências externas checadas por API
4. **Secrets e variables** (do `.env` ou via comandos `!` para o usuário)
5. **Disparar em etapas**: PR primeiro, depois o merge feito pelo usuário, depois main/dispatch
6. **Acompanhar** o run pelo SHA, em background
7. **Diagnosticar e corrigir**: log filtrado, catálogo, rerun ou PR de correção, diagnóstico temporário
8. **Verificar** os jobs (`skipped` = não testado), os marcadores no log e o mundo real (curl, TLS, portas, API da cloud)
9. **Relatório final** em pt-BR

## Pré-requisitos e configuração

- `gh` autenticado (`gh auth status`) com escopo `repo` e `workflow`
- `jq`, `perl`, `python3` (para os scripts)
- Opcional, para validação local: `actionlint`, Terraform/Ansible na versão do projeto (a skill baixa no scratchpad se faltar)

## Fronteira humano × Claude

A skill entrega comandos `!` ou links prontos, sem tentar antes, para: gravar um secret cujo valor não está em disco, criar PAT, fazer merge de PR, apagar repositório e ampliar o escopo do `gh`. Ela não lê `.env` com `cat`/`source` e nunca imprime valores de secret.

## Skills relacionadas

- **docker-practices**: build e push de imagens em workflows
- **kubernetes-practices**: manifests aplicados pelo deploy

## Exemplos de uso

```
Criei o .env com as variáveis. Cria o repositório no GitHub, coloca os secrets e testa a pipeline de provisionamento

O deploy falhou no Actions, descobre por quê e corrige

Por que o plan e o ansible-lint não rodaram nesse run?

Adiciona permissions mínimas e concurrency nesse workflow

Quero testar o CI/CD da aplicação de ponta a ponta até a app estar no ar

O que é esse INFRA_DISPATCH_TOKEN e como eu crio?
```

## Limitações conhecidas

- Específica de **GitHub Actions**: não cobre GitLab CI, Jenkins etc.
- Não desenha a arquitetura das pipelines: brainstorm, TRD e SDD ficam com as skills do fluxo spec-driven
- Merge, criação de PAT e ações destrutivas dependem do usuário (limite do harness e do próprio GitHub)
- O catálogo de falhas reflete os casos já vividos e cresce conforme novas falhas são resolvidas
