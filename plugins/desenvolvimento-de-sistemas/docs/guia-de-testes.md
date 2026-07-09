# guia-de-testes

Guia para escrever e auditar testes em todas as camadas — unitários, integração e E2E. Define critérios objetivos sobre o que vale e o que não vale testar, limites saudáveis de mocks (máximo 3 por teste) e o propósito distinto de cada camada. Funciona em dois modos: **Escrita** (decidir se um teste novo deve existir e como escrevê-lo) e **Auditoria** (classificar testes existentes em Remover / Manter / Faltando com relatório consolidado).

## Pré-requisitos e configuração

- Projeto com ou sem testes existentes
- Para auditoria: acesso ao código de produção e aos arquivos de teste para que os agentes paralelos possam ler tudo em uma passagem

## Dependências externas

Nenhuma.

## Skills relacionadas

- **teste-e2e-navegacao** — para fluxos críticos de ponta a ponta, delegue a geração dos cases de navegação à teste-e2e-navegacao e use guia-de-testes para as camadas unitária e de integração
- **typescript-practices** — aplique as convenções de TypeScript nos testes que forem escritos

## Exemplos de uso

```
Escreve os testes dessa função de cálculo de frete

Devo testar esse helper ou ele cai em "NÃO vale testar"?

Em qual camada deve ficar o teste desse endpoint?

Audita os testes do módulo de pagamentos — quero saber o que dá pra deletar

Quais testes estão faltando na API de usuários?

Revisa a qualidade dos testes antes do PR
```

## Limitações conhecidas

- No modo Auditoria, a Fase 1 exige confirmação do usuário sobre o que unitário/integração/E2E significam no projeto — esses termos são ambíguos e a skill não chuta convenções
- Contagem de testes é feita lendo cada arquivo — sem amostragem ou estimativa; em projetos muito grandes a auditoria paraleliza via múltiplos agentes, mas ainda tem custo proporcional ao número de arquivos
- Quatro modos de execução disponíveis (Somente relatório, Relatório + Deletar, Relatório + Scaffold, Automação completa) — a skill pergunta qual modo usar antes de aplicar qualquer mudança
- Critérios são prescritivos — se o projeto tem convenção diferente (ex.: testar wiring intencionalmente), informe no prompt para a skill respeitar
- A pirâmide de testes é tratada como diretriz, não lei — se a lógica vive em handlers, testes de integração podem pesar mais que unitários na recomendação final
