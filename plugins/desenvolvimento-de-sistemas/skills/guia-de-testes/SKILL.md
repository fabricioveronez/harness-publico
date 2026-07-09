---
name: guia-de-testes
description: >
  Guia para escrever e auditar testes em todas as camadas — unitários, integração e E2E.
  Use esta skill ao escrever novos testes, criar arquivos de teste, decidir o que testar em cada camada,
  escolher entre unitário vs integração vs E2E, e também ao auditar testes existentes, limpar
  testes redundantes ou identificar cobertura ausente. Ativa com: "escrever testes", "adicionar testes para",
  "criar testes unitários", "criar testes de integração", "criar testes e2e", "devo testar isso",
  "em qual camada deve ficar esse teste", "auditar testes", "limpar testes", "quais testes posso deletar",
  "quais testes estou faltando", "revisar qualidade dos testes".
---

# Guia de Testes

Escreva testes que verificam se o sistema se comporta corretamente em cada camada. Cada teste deve ter um propósito claro — qual comportamento ele prova e em qual fronteira. Vá além dos cenários felizes: teste casos extremos, cenários de erro e condições de borda onde os bugs realmente se escondem.

---

## Os Critérios

Estas regras se aplicam tanto ao escrever novos testes quanto ao auditar os existentes.

### Vale testar

- **Lógica de negócio com ramificação** — condicionais, máquinas de estado, verificações de permissão, regras de domínio
- **Fronteiras de segurança** — autenticação, autorização, rate limiting, sanitização de entrada, xss, csrf, sql injection, etc.
- **Integridade de dados** — transformações, serialização, migrações, cálculos onde saída errada = dados corrompidos
- **Tratamento de erros** — o que acontece quando serviços externos falham, banco está fora, usuário não autorizado
- **Fluxos críticos de usuário** — autenticação, pagamento, upload, CRUD principal que os usuários dependem
- **Race conditions** — operações concorrentes, optimistic locking, processamento de filas
- **Casos extremos/borda** — null, vazio, valores máximos, off-by-one, overflow
- **Integrações externas** — webhooks, respostas inesperadas de API, timeouts, incompatibilidades de contrato

### NÃO vale testar

- **Comportamento do framework** — Confie no que o framework garante: renderização, roteamento, tratamento de requisições, persistência do ORM, estados de carregamento. Se o framework funciona, isso funciona. Teste sua lógica em cima dele.
- **Passagem de validação** — Bibliotecas de validação já aplicam suas regras. Um teste provando que o validador está conectado é suficiente — não um por regra no mesmo caminho de código. Mantenha um teste happy-path por validador para provar que entrada válida passa, mas não duplique cada regra de rejeição.
- **Testes espelho** — Quando a asserção copia o valor de retorno da implementação. O teste nunca pode capturar um bug — ele só quebra quando você muda o código intencionalmente.
- **Cobertura duplicada entre camadas** — Cada teste deve capturar um bug que nenhum outro teste captura. Se um comportamento é verificado em uma camada superior, um teste de camada inferior para o mesmo caminho não acrescenta nada, a menos que a lógica seja complexa o suficiente para precisar de isolamento de falhas. Isso inclui: funções re-testadas por seus chamadores.
- **Testes de fiação** — Testes que apenas verificam se uma chamada de efeito colateral foi feita com os argumentos certos. Eles testam cola, não lógica. Quebram em refatorações, não em bugs. Só teste fiação quando há transformação, lógica condicional ou tratamento de erro entre chamador e chamado.
- **Asserções de estrutura estática** — Existência de campo, tipos de coluna, valores de estado inicial, config padrão, verificações de tipo. Se a estrutura estiver errada, todos os outros testes que dependem dela já falham.
- **Forma de saída sem comportamento** — Testes que verificam saída estática (texto renderizado, presença de campo na resposta, propriedades visuais, conteúdo de arquivo fonte) sem exercer nenhuma lógica. Se um teste comportamental no mesmo arquivo já produz a mesma saída, o teste apenas de forma é redundante.
- **Repetição de variantes sem ramificação** — Múltiplos testes exercendo o mesmo caminho de código com entradas diferentes. Se a lógica não ramifica, um teste representativo (ou um teste parametrizado) é suficiente.
- **Utilitários de caminho único** — Funções sem condicionais, sem tratamento de erro, sem casos extremos. Getters simples, setters, delegações de uma linha. Se a função ramifica, vale testar.

### Saúde dos mocks

- **Máximo 3 mocks por teste.** Mais do que isso significa que você está testando fiação, não comportamento.
- Se um teste precisa de 4+ mocks, reescreva como teste de integração ou remova-o.
- Testes de frontend são especialmente propensos a excesso de mocks. Um teste de componente com router mockado, context mockado, API mockada e hooks mockados não testa nada real.

### Cada camada tem um propósito

**Testes unitários** provam que lógica isolada funciona — ramificação, cálculos, regras de domínio. São rápidos e apontam exatamente o que quebrou. Escreva-os para funções com condicionais complexas onde o isolamento de falhas importa. Nem todo comportamento precisa de teste unitário — se a lógica é simples e um teste de integração já cobre, o teste unitário é cobertura duplicada.

**Testes de integração** provam que partes funcionam juntas — API + BD, serviço + repositório, componente + context. Capturam incompatibilidades de contrato e bugs de fiação que testes unitários não conseguem ver.

**Testes E2E** provam que um fluxo completo funciona de ponta a ponta — uma chamada de API completa atravessando todas as camadas (requisição → middleware → serviço → BD → resposta), um teste guiado por browser que dispara chamadas de backend, ou um fluxo que inclui serviços externos. Validam que toda a cadeia funciona junta, não apenas peças individuais.

| Camada | Testar | Pular |
|--------|--------|-------|
| **Unitário** | Funções com condicionais, cálculos, regras de domínio, máquinas de estado | Getters, utils triviais, config, validação de schema |
| **Integração** | Endpoints de API (auth, permissões, erros), serviços + BD, componente + context | CRUD simples já coberto por E2E, renderização estática |
| **E2E** | Fluxos críticos de usuário (auth, upload, workflows principais), travessias completas de API | Fluxos já bem cobertos por testes de integração |

---

## Modo: Escrevendo Testes

Ao criar novos testes, aplique os critérios acima antes de escrever qualquer coisa.

1. Verifique o código contra as categorias **"Vale testar"** e **"NÃO vale testar"** acima.
2. Se corresponder a "Vale testar" e não a "NÃO vale testar" → escreva. Foque as asserções em comportamento, não apenas em detalhes granulares de implementação.
3. Caso contrário → não escreva o teste. Siga em frente.

Ao escrever:
- Teste comportamento e resultados, não detalhes granulares de implementação.
- Um conceito por teste — se precisar de `e` no nome do teste, divida-o
- Nomeie testes pelo que verificam: `test_conta_bloqueada_retorna_403`, não `test_login_3`
- Prefira dependências reais a mocks **quando viável** (BD em memória em vez de repositório mockado). Se não for um projeto greenfield, siga as convenções do projeto.

---

## Modo: Auditoria

Ao auditar testes existentes, use os mesmos critérios para classificar cada teste.

### Fase 1: Entenda as definições de teste do projeto

Antes de julgar, entenda o que unitário/integração/E2E significam **neste projeto específico** — esses termos são ambíguos:

- Leia documentação do projeto, configs de teste, pipeline de CI, estrutura de diretórios
- Confirme seu entendimento com o usuário antes de prosseguir

### Fase 2: Explorar, Contar e Classificar

- **Passo 1**: Explore o código da aplicação (não apenas os testes) — entenda módulos, lógica de negócio, fluxos críticos e o que cada área do codebase faz. Esse contexto é essencial para julgar se um teste vale manter.
- **Passo 2**: Encontre todos os arquivos de teste (Glob) para saber a escala total.
- **Passo 3**: Com base no número de arquivos/diretórios/módulos de teste e na estrutura da aplicação, decida quantos agentes paralelos lançar. Cada agente recebe um escopo específico (arquivos, diretórios ou módulos — siga a organização do projeto). Cada agente também recebe contexto sobre o código de produção ao qual seus testes se relacionam.
- **Passo 4**: Cada agente, em uma única passagem por arquivo:
  - Conta cada caso de teste individualmente com precisão (leia cada arquivo, conte declarações exatas — sem estimativas, sem amostragem). Máxima precisão na contagem de testes é obrigatória.
  - Classifica cada teste: **Remover** / **Manter** / **Faltando** — usando conhecimento do código de produção para julgar a pertinência segundo os critérios acima.
- **Passo 5**: Agrega todos os resultados dos agentes — contagens totais + classificações.

### Fase 3: Relatório

```
# Relatório de Auditoria de Testes

## Visão Geral da Contagem de Testes
| Métrica | Contagem |
|---------|----------|
| **Total de testes no sistema** | X |
| **Testes para remover** | Y |
| **Contagem projetada após limpeza** | Z |

## Definições de Teste do Projeto
[O que cada categoria significa neste projeto]

## Resumo
- Arquivos de teste analisados: X
- Remover: X | Manter: X | Críticos faltando: X | Casos extremos faltando: X

## Testes para Remover
### [arquivo:nome_do_teste]
- **Categoria**: [categoria correspondente da lista NÃO vale testar acima]
- **Por quê**: [1-2 frases]

## Testes Faltando (Ordem de Prioridade)
### Críticos
[O que testar e por que importa]

### Casos Extremos
[Descrições de cenários]

## Saúde dos Mocks
[Arquivos com excesso de mocking e refatorações sugeridas]
```

### Modos de execução

Pergunte ao usuário qual modo deseja:

- **Somente relatório** (padrão) — gera relatório, não faz alterações
- **Relatório + Deletar** — relatório, depois remove testes confirmados um por um
- **Relatório + Scaffold** — relatório, depois cria estrutura de testes faltando com placeholders TODO
- **Automação completa** — relatório, deleta testes confirmados, cria estrutura de testes faltando com placeholders TODO

---

## Princípios

- Leia o código real do teste — não julgue apenas pelo nome
- Aplique os critérios de forma consistente — se um teste corresponde a NÃO vale testar e não corresponde a Vale testar, remova-o
- Respeite as convenções do projeto (configs de teste)
- A pirâmide de testes é uma diretriz, não uma lei — se a lógica vive em handlers de API, testes de integração podem importar mais que unitários
