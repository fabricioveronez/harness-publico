---
name: teste-e2e-navegacao
description: >
  Gera e executa casos de teste E2E para qualquer aplicação web — SPA, server-rendered
  ou híbrida. Analisa o codebase para descobrir rotas, componentes, fluxos de autenticação,
  formulários, modais, roles/permissões e padrões de navegação, depois produz um documento
  estruturado de casos de teste com árvores de dependência e checklists. Funciona com qualquer
  framework: Next.js, React, Vue, Angular, Django, Laravel, Rails, Flask, Go,
  Symfony, Spring, ASP.NET, PHP e mais. Use esta skill sempre que o usuário pedir para
  "testar navegação", "gerar testes e2e", "testar fluxos de usuário", "criar casos de teste",
  "executar testes de navegação", "plano de teste e2e", "verificar todos os fluxos", "testar meu app",
  "mapear jornadas do usuário", ou qualquer coisa relacionada a testes de fluxo ponta a ponta.
  Também ative quando o usuário mencionar "test-cases.md", "cobertura de fluxo" ou
  "cobertura de navegação".
---

# Gerador de Casos de Teste E2E

Analise um codebase de aplicação web (SPA, server-rendered ou híbrida), gere um plano de teste estruturado com consciência de dependências e, opcionalmente, execute os testes usando automação de browser.

---

## Fase 1: Descoberta do Codebase

Antes de gerar qualquer caso de teste, construa um modelo mental de toda a aplicação.

### Passo 1: Detectar o framework

Identifique qual framework e sistema de roteamento o projeto usa. A aplicação pode ser uma SPA (single-page app), uma aplicação server-rendered com templates, ou híbrida. Procure pelos sinais abaixo, depois **leia `references/framework-discovery.md`** para o checklist completo do framework detectado — ele diz exatamente onde encontrar rotas, config de auth, templates, roles e padrões de navegação para aquele framework específico.

**Frameworks JavaScript SPA:**
- **Next.js App Router**: diretório `app/` com `page.tsx`, `layout.tsx`, grupos de rota `(nome)/`
- **Next.js Pages Router**: diretório `pages/`
- **React Router**: imports de `react-router-dom`, componentes `<Route>`
- **Vue Router**: `router/index.ts`, `<router-view>`
- **SvelteKit**: `src/routes/` com `+page.svelte`
- **Angular**: `app-routing.module.ts`, `RouterModule`
- **Nuxt**: diretório `pages/` com arquivos `.vue`
- **Astro**: diretório `src/pages/`
- **Remix**: diretório `app/` com arquivos `route.ts`

**Frameworks server-rendered / baseados em template:**
- **Django**: definições de rota em `urls.py`, diretório `templates/` com arquivos `.html`, sintaxe de template Django/Jinja2 (`{% block %}`, `{{ var }}`)
- **Laravel**: `routes/web.php`, `resources/views/` com templates `.blade.php`
- **Rails**: `config/routes.rb`, `app/views/` com templates `.erb` ou `.haml`
- **Go (html/template)**: arquivos `*.go` com `http.HandleFunc`, `templates/` com arquivos `.html` ou `.tmpl`
- **Symfony/Twig**: `config/routes.yaml` ou anotações, `templates/` com arquivos `.html.twig`
- **Flask**: decorators `@app.route()`, `templates/` com arquivos Jinja2 `.html`
- **Express + templates**: rotas `app.get()` / `router.get()`, `views/` com templates `.ejs`, `.pug`, `.hbs`
- **Spring MVC**: `@Controller` + `@RequestMapping`, `src/main/resources/templates/` com Thymeleaf `.html`
- **PHP (puro)**: arquivos `.php` com roteamento direto ou ponto de entrada `index.php`
- **ASP.NET MVC/Razor**: `Controllers/`, views Razor `.cshtml`

**Estático / sem framework:**
- **HTML puro**: arquivos `.html` com tags âncora, sem framework
- **Genérico**: nenhum framework reconhecível — analise a estrutura de arquivos e infira roteamento a partir de links, formulários e elementos de navegação

Para **apps server-rendered**, a navegação acontece via carregamentos completos de página (não roteamento client-side). Isso significa:
- Cada clique em link dispara uma nova requisição HTTP
- Formulários são submetidos via POST e redirecionam (padrão PRG)
- Não há estado de router client-side para rastrear
- Rotas são definidas no código de backend, não em componentes frontend
- Passos de teste devem esperar recarregamentos completos de página após ações de navegação

Identifique também:
- **Sistema de autenticação**: NextAuth, Clerk, Auth0, Firebase Auth, Django auth, Laravel Sanctum/Breeze, Devise, JWT customizado, baseado em sessão, ou outro
- **Biblioteca de UI**: Headless UI, Radix, shadcn, MUI, Chakra, Bootstrap, Tailwind, HTML/CSS puro, ou outro
- **Gerenciamento de estado**: Context, Redux, Zustand, Pinia, Vuex, sessões server-side, ou outro

Reporte os achados ao usuário antes de prosseguir.

### Passo 2: Mapear todas as rotas e pontos de entrada

Leia a estrutura de roteamento e construa um mapa completo de rotas:

- Todas as rotas de página (estáticas e dinâmicas)
- Grupos de rota e layouts (elementos de navegação compartilhados)
- Rotas protegidas vs públicas
- Regras de redirecionamento (middleware, guards, configs de rota)
- Rotas de API que afetam navegação (endpoints de login, redirecionamentos)

### Passo 3: Mapear fluxos dentro das páginas

Para cada rota, identifique fluxos interativos:

- **Formulários**: registro, login, busca, operações CRUD, configurações
- **Modais/Diálogos**: diálogos de confirmação, formulários de criar/editar, views de detalhe
- **Elementos de navegação**: sidebar, barra superior, breadcrumbs, tabs, menus
- **UI orientada por estado**: estados de carregamento, estados vazios, estados de erro, renderização condicional
- **Drag and drop**: reordenação, movimentação de itens entre contêineres
- **Operações em lote**: selecionar tudo, deletar em lote, mover em lote

### Passo 4: Identificar autenticação, roles e permissões

Realize uma investigação minuciosa de roles e permissões de usuário. Roles são frequentemente definidas em vários lugares — verifique todos eles:

**Camada de banco de dados:**
- Leia o schema (Prisma, migrations, arquivos SQL) para colunas de role/permissão, enums ou tabelas de junção
- Verifique arquivos seed para diferentes tipos de usuário e suas atribuições de role
- Procure tabelas de permissão, tabelas RBAC (controle de acesso baseado em role) ou tabelas de política

**Camada de aplicação:**
- Middleware de auth, guards ou proteção de rota que verifica roles
- Verificações de role em componentes (renderização condicional: `if (user.role === 'admin')`, `{isAdmin && ...}`)
- Handlers de rota de API que verificam permissões antes de executar ações
- Constantes ou enums que definem roles disponíveis (ex.: `UserRole.ADMIN`, `ROLES = [...]`)

**Camada de configuração:**
- Variáveis de ambiente que definem roles padrão
- Arquivos de config com matrizes de permissão
- Feature flags vinculadas a roles

Construa uma **matriz de roles** listando cada role e quais funcionalidades ela pode acessar:

```
| Funcionalidade    | admin | user | guest |
|-------------------|-------|------|-------|
| Ver dashboard     |  sim  | sim  |  não  |
| Criar itens       |  sim  | sim  |  não  |
| Deletar qualquer  |  sim  |  não |  não  |
| Acessar painel    |  sim  |  não |  não  |
```

Apresente esta matriz ao usuário e pergunte:
- "Encontrei estes roles: [lista]. Para quais roles devo gerar casos de teste? Todos, ou roles específicos?"

**Se múltiplos roles forem selecionados**, gere um arquivo de casos de teste separado por role:
- `docs/test-cases-e2e-admin.md`
- `docs/test-cases-e2e-user.md`
- `docs/test-cases-e2e-guest.md`

(Ou use o padrão `docs/test-cases-e2e.md` se houver apenas um role ou se o app não tiver sistema de roles.)

Cada arquivo de role deve incluir:
- **Fluxos específicos do role**: funcionalidades únicas para aquele role
- **Fluxos compartilhados**: funcionalidades comuns testadas pela perspectiva daquele role (não é preciso detalhar os passos novamente se o comportamento for idêntico — referencie o outro arquivo)
- **Testes de negação de acesso**: verifique que o role NÃO PODE acessar funcionalidades reservadas para roles superiores (ex.: usuário comum tenta acessar `/admin` e é redirecionado ou vê 403)

**Se apenas um role existir** (ou nenhum sistema de roles), prossiga com um único arquivo e pule a pergunta de seleção de role.

---

## Fase 2: Construir a Árvore de Dependências

Esta é a fase mais crítica. Todo fluxo de teste tem pré-requisitos. Modele-os explicitamente.

### Regras de dependência

1. **Um fluxo depende de outro se não puder ser testado sem que esse fluxo tenha sucesso primeiro.** Exemplo: "Criar um prompt" depende de "Login" porque você precisa estar autenticado.

2. **Se uma dependência falha, todos os fluxos que dependem dela ficam automaticamente BLOQUEADOS.** Documente isso claramente. Exemplo: se Login falha, tudo atrás de auth está BLOQUEADO.

3. **Fluxos independentes rodam independentemente de outras falhas.** Exemplo: "Visitar página inicial" e "Visitar página de cadastro" são independentes entre si.

4. **Evite testar redundantemente.** Se Login já foi verificado como dependência, fluxos subsequentes que precisam de auth devem indicar "Requer: Login (testado em T01)" mas NÃO re-testar os passos de login. Eles começam de uma sessão já autenticada.

5. **Encadeie dependências, não as repita.** Se "Editar prompt" depende de "Criar prompt" que depende de "Login", então "Editar prompt" lista apenas "Criar prompt" como sua dependência direta. A dependência transitiva em Login é implícita.

### Formato da árvore de dependências

Construa a árvore como uma hierarquia visual que mostra relacionamentos pai-filho de relance. Use conectores ASCII (`├─`, `└─`, `│`) para transmitir a estrutura. Cada teste recebe um ID curto (T01, T02, ...) para fácil referência.

```
T01 Página Inicial
 ├─ T02 Cadastro
 └─ T03 Login
     └─ T04 Dashboard
         ├─ T05 Criar Item
         │   ├─ T06 Editar Item
         │   └─ T07 Deletar Item
         ├─ T08 Busca
         └─ T09 Alternar Tema
 └─ T10 Logout
```

Nós raiz (T01) não têm dependências. Um filho só pode executar se seu pai passou. Irmãos são independentes entre si — se T06 falha, T07 ainda roda. Note que Busca (T08) depende de Dashboard (T04), não de Criar Item (T05) — coloque cada teste sob sua dependência real, não sob um irmão não relacionado.

---

## Fase 3: Gerar Documento de Casos de Teste

### Caminho de saída

- **Role único ou sem roles**: `docs/test-cases-e2e.md`
- **Múltiplos roles**: um arquivo por role — `docs/test-cases-e2e-<role>.md` (ex.: `docs/test-cases-e2e-admin.md`, `docs/test-cases-e2e-user.md`)

Pergunte ao usuário para confirmar: "Vou salvar os casos de teste em `docs/test-cases-e2e.md` (ou arquivos por role se houver múltiplos roles). Quer um local diferente?"

### Estrutura do documento

Use exatamente esta estrutura:

O documento deve ser completamente autocontido — qualquer pessoa lendo deve ter tudo o que precisa para executar os testes sem consultar outros lugares.

````markdown
# Casos de Teste E2E de Navegação [— Role: <nome_do_role>]

> Gerado automaticamente pela skill teste-e2e-navegacao
> Framework: [framework detectado]
> Gerado em: [data]
> Role: [nome do role, ou "Role único / Sem roles" se não aplicável]

Testes de aceitação ponta a ponta para [descrição do app].
Os testes são ordenados por dependência — se um teste falha, todos os testes dependentes ficam automaticamente **BLOQUEADOS**.

## Pré-requisitos

- **Iniciar servidor**: [comando descoberto no projeto — ex.: `npm run dev`, `./scripts/init.sh`]
- **URL base**: `http://localhost:[porta]`
- **Usuário de teste para este role**: **[email]** / **[senha]** (role: [nome_do_role])
- **Screenshots em falha**: salvas na subpasta `screenshots/` ao lado deste arquivo
- **Modo de browser**: headless

## Stack Detectada

- **Framework**: [ex.: Next.js 16 App Router]
- **Auth**: [ex.: NextAuth v5]
- **Biblioteca de UI**: [ex.: Headless UI, Tailwind CSS]
- **Roles detectados**: [lista todos os roles encontrados, ou "Nenhum"]
- **Rotas descobertas**: [contagem]

## Matriz de Roles

[Incluir apenas se múltiplos roles existirem. Mostra quais funcionalidades cada role pode acessar.]

| Funcionalidade    | admin | user | guest |
|-------------------|-------|------|-------|
| Ver dashboard     |  sim  | sim  |  não  |
| Criar itens       |  sim  | sim  |  não  |
| Deletar qualquer  |  sim  |  não |  não  |

[Omitir esta seção inteiramente para apps de role único ou sem roles.]

---

## Árvore de Dependências

```
T01 Página Inicial
 ├─ T02 Cadastro
 └─ T03 Login
     └─ T04 Dashboard
         ├─ T05 Criar Item
         │   ├─ T06 Editar Item
         │   └─ T07 Deletar Item
         └─ T08 Busca
 └─ T09 Logout
```

Se um teste pai falha, todos os seus filhos ficam automaticamente **BLOQUEADOS** e são ignorados.

---

## Fluxos de Teste

### T01: [Nome do Fluxo]

**Dependências**: Nenhuma
**Bloqueia**: T02, T03 (liste todos os filhos diretos)

- [ ] Navegar para /caminho
- [ ] Verificar que [elemento] está visível
- [ ] Executar [ação]
- [ ] Verificar [resultado esperado]

---

### Testes de Negação de Acesso

[Incluir apenas em arquivos multi-role. Teste que este role NÃO PODE acessar funcionalidades reservadas para outros roles. Use a mesma numeração T — continue após o último fluxo regular.]

### T10: [Funcionalidade] — Acesso Negado

- [ ] Navegar para [caminho restrito]
- [ ] Verificar redirecionamento para login/home OU exibição de erro 403
- [ ] Verificar que conteúdo restrito NÃO está visível

---

[Repita para cada fluxo...]

---

## Observações

[Preenchido após execução. Vazio durante geração.]

### Testes com Falha

#### T05: Criar Item — FALHOU no passo 3
- **Erro**: [mensagem de erro concreta]
- **Impacto**: T06, T07 ficaram BLOQUEADOS
- **Screenshot**: screenshots/t05-criar-item-passo3.png

### Testes Bloqueados

| Teste | Motivo |
|-------|--------|
| T06 Editar Item | Pai T05 falhou |
| T07 Deletar Item | Pai T05 falhou |

### Resumo

- Total: X
- Passou: X
- Falhou: X
- Bloqueado: X
````

### Escrevendo bons passos de teste

Cada passo deve ser concreto e executável:

- **Navegar para** um caminho de URL específico
- **Verificar** que um elemento específico está visível, tem texto, ou tem um estado
- **Clicar/Preencher/Selecionar** elementos específicos pelo seu role ou texto visível
- **Aguardar** navegação, estados de carregamento ou animações completarem
- **Verificar o resultado**: URL mudou, elemento apareceu/desapareceu, mensagem toast exibida

Evite passos vagos como "verificar que a página funciona" ou "verificar funcionalidade". Cada passo deve ser binário: ou passa ou falha.

### Granularidade

Cada fluxo deve ter 3-8 passos. Se um fluxo precisar de mais de 8 passos, divida em sub-fluxos.

Passos dentro de um fluxo são sequenciais. Se o passo 3 falha, os passos 4+ naquele fluxo não são executados.

---

## Fase 4: Executar Testes (Opcional)

Após gerar o documento, pergunte ao usuário: "Casos de teste prontos. Quer que eu os execute agora usando automação de browser?"

Se sim:

### Regras de execução

1. **Leia a seção de Pré-requisitos** do documento de casos de teste gerado — ela já contém o comando de inicialização, URL base e credenciais de teste (descobertas durante a Fase 1). Se executando na mesma sessão que gerou o documento, esses valores já são conhecidos. Se executando depois, leia-os do documento.

2. **Garanta que o servidor está rodando** antes de qualquer teste. Se o projeto tem um script de inicialização, use-o. Caso contrário, execute o comando de servidor dev descoberto acima.

3. **Use a automação de browser disponível** (playwright-cli ou qualquer ferramenta disponível) em modo headless.

4. **Siga a ordem da árvore de dependências** — execute os testes raiz primeiro, depois seus filhos.

5. **Em falha de dependência**: marque todos os testes filhos como BLOQUEADOS, não os tente executar.

6. **Em falha independente**: continue com o próximo teste independente.

7. **Tire um screenshot em falha.** Salve screenshots em uma subpasta `screenshots/` ao lado do documento de casos de teste. Nomeie o arquivo após o teste com falha: `screenshots/t05-criar-item-passo3.png`. Nunca salve screenshots na raiz do projeto.

8. **Após cada navegação**: verifique o console do browser por erros — qualquer erro de compilação ou runtime significa FALHA para aquele passo.

### Atualizando o documento após execução

Marque cada passo com seu resultado:

- `[x]` — passou
- `[ ]` — ainda não executado
- `[FAIL]` — falhou (adicione motivo breve inline)
- `[BLOQUEADO]` — ignorado porque uma dependência pai falhou

### Seção de Observações

Após a execução, preencha a seção de Observações no final do documento usando o formato mostrado no template do documento acima (Testes com Falha, tabela de Testes Bloqueados, contagens de Resumo).

---

## Princípios

- **Descubra antes de assumir.** Leia o código real, não apenas nomes de arquivo. Uma rota pode existir mas redirecionar. Um formulário pode estar desabilitado. Uma verificação de auth pode ser apenas client-side.
- **Respeite a árvore de dependências.** Nunca execute um fluxo se sua dependência falhou. Isso evita falhas em cascata que obscurecem o problema real.
- **Sem passos de login redundantes.** Se o login foi testado e passou no T01, fluxos subsequentes começam de uma sessão de browser já autenticada. Não repita os passos de login — apenas anote a dependência.
- **Seja consciente do framework mas não dependente dele.** A fase de descoberta se adapta ao framework, mas o formato de saída e a lógica de execução permanecem iguais independentemente do stack.
- **Resultados binários apenas.** Cada passo passa ou falha. "Funciona parcialmente" é uma falha com uma nota.

---

## Arquivos de Referência

### `references/framework-discovery.md` — Checklists de Descoberta de Framework

Leia a seção para o framework detectado **imediatamente após o Passo 1** (Detectar o framework). Fornece um checklist detalhado de onde encontrar rotas, auth, templates, roles, formulários e gerenciamento de estado para 18 frameworks. Exemplos de quando ler:

- Detectou **Django** — leia a Seção 7 para encontrar todos os arquivos `urls.py`, decorators `@login_required`, diretórios de template, tabelas `auth_group`/`auth_permission`
- Detectou **Laravel** — leia a Seção 8 para encontrar `routes/web.php` vs `routes/api.php`, templates Blade, permissões Spatie, grupos de middleware
- Detectou **Rails** — leia a Seção 9 para encontrar `config/routes.rb`, auth Devise, comportamento Turbo/Hotwire, políticas Pundit
- Detectou **Next.js App Router** — leia a Seção 1 para encontrar redirecionamentos de middleware, Server Components vs Client Components, Server Actions
- Detectou **PHP tradicional** — leia a Seção 16 para escanear arquivos `.php`, reescritas `.htaccess`, auth baseada em sessão

### `references/common-pitfalls.md` — Armadilhas Comuns

Leia quando encontrar problemas específicos durante geração ou execução de testes:

**Durante Fase 1 (Descoberta):**
- O app usa OAuth/provedores de login externos (Google, GitHub) — leia a Seção 1.2 para alternativas
- O app é construído com Django, Laravel, Rails, ou outro framework server-rendered — leia a Seção 4 (Aplicações Server-Rendered) e Seção 7 (Particularidades por Framework)
- O app usa editores de texto rico (TinyMCE, Quill, CKEditor) — leia a Seção 2.2 para estratégias de interação
- O app tem date pickers customizados, campos de auto-complete, ou uploads de arquivo — leia as Seções 2.3-2.5

**Durante Fase 2 (Árvore de Dependências):**
- Dados de teste podem colidir com dados seed (restrições de unicidade) — leia a Seção 6.1
- Testes criam dados dos quais testes posteriores dependem (IDs dinâmicos) — leia a Seção 6.2

**Durante Fase 3 (Gerando Passos de Teste):**
- Formulários têm tokens CSRF (Django, Laravel, Rails, etc.) — leia a Seção 2.1
- Campos de busca têm debounce — leia a Seção 3.1
- Modais/diálogos têm animações que atrasam interação — leia a Seção 3.2
- O app usa WebSockets ou atualizações em tempo real — leia a Seção 3.3

**Durante Fase 4 (Execução):**
- Login funciona mas testes posteriores recebem 401/redirecionam para login — leia a Seção 1.1 (persistência de sessão) e Seção 1.3 (expiração de JWT)
- Servidor não inicia (porta em uso, variáveis de ambiente faltando) — leia a Seção 5
- Testes passam na primeira execução mas falham na segunda — leia a Seção 6.3
- Submissão de formulário não faz nada ou retorna 403 — leia a Seção 2.1 (CSRF) e Seção 4.1 (padrão PRG)
- Mensagens flash/toast são perdidas — leia a Seção 4.2
- MFA bloqueia login automatizado — leia a Seção 1.5
