# teste-e2e-navegacao

Gera e executa casos de teste E2E para qualquer aplicação web — SPA, server-rendered ou híbrida. Analisa o codebase para descobrir rotas, componentes, fluxos de autenticação, formulários, modais, roles/permissões e padrões de navegação, depois produz um documento estruturado de casos de teste com árvore de dependências e checklists. Se solicitado, executa os testes via automação de browser, marca cada passo com seu resultado e preenche a seção de observações com falhas, bloqueios e resumo.

## Pré-requisitos e configuração

- Codebase da aplicação web acessível para análise
- Para execução (opcional): ferramenta de automação de browser disponível (ex.: playwright-cli) e servidor dev do projeto inicializável

## Dependências externas

- Automação de browser (opcional, apenas para executar os testes gerados)

## Skills relacionadas

- **guia-de-testes** — use guia-de-testes para decidir o que cobrir em cada camada antes de rodar teste-e2e-navegacao para o fluxo completo
- **escrever-prd** — o PRD pode referenciar os fluxos críticos que teste-e2e-navegacao vai validar

## Exemplos de uso

```
Gera os testes e2e da minha aplicação

Mapeia todos os fluxos de navegação do app e cria os casos de teste

Quero um plano de teste e2e separado por role (admin, user, guest)

Testar meu app — cria os casos e executa em modo headless

Criar test-cases.md com cobertura de navegação do painel administrativo

Verifica todos os fluxos de autenticação e gera a árvore de dependências
```

## Limitações conhecidas

- Arquivo de saída por padrão em `docs/test-cases-e2e.md` (ou `docs/test-cases-e2e-<role>.md` em apps multi-role) — screenshots de falha são salvas em `screenshots/` ao lado do documento
- Resultados são binários — cada passo passa ou falha, não existe "parcial"
- Execução depende de o servidor dev do projeto subir sem intervenção manual e de credenciais de teste válidas descobertas na Fase 1
- Fluxos com MFA, OAuth externo (Google, GitHub), CAPTCHA ou editores rich-text customizados exigem ajustes adicionais (consulte `references/common-pitfalls.md`)
- Framework detection cobre 18 stacks explicitamente — projetos fora dessa lista caem no modo genérico e podem precisar de descoberta manual
- Não cobre testes de performance, acessibilidade ou segurança — foco é navegação e fluxos funcionais
