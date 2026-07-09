# Checklists de Descoberta de Framework

Onde encontrar rotas, auth, templates e padrões de navegação para cada framework. Use como checklist durante a Fase 1 (Descoberta do Codebase) após detectar o framework. Leia apenas a seção do framework detectado.

---

## Índice

1. [Next.js (App Router)](#1-nextjs-app-router)
2. [Next.js (Pages Router)](#2-nextjs-pages-router)
3. [React (CRA / Vite + React Router)](#3-react-cra--vite--react-router)
4. [Vue / Nuxt](#4-vue--nuxt)
5. [SvelteKit](#5-sveltekit)
6. [Angular](#6-angular)
7. [Django](#7-django)
8. [Laravel](#8-laravel)
9. [Ruby on Rails](#9-ruby-on-rails)
10. [Flask](#10-flask)
11. [Express.js (com templates)](#11-expressjs-com-templates)
12. [Go (net/http + templates)](#12-go-nethttp--templates)
13. [Symfony / Twig](#13-symfony--twig)
14. [Spring Boot MVC](#14-spring-boot-mvc)
15. [ASP.NET MVC / Razor Pages](#15-aspnet-mvc--razor-pages)
16. [PHP (Tradicional / Sem Framework)](#16-php-tradicional--sem-framework)
17. [Remix](#17-remix)
18. [Astro](#18-astro)

---

## 1. Next.js (App Router)

### Rotas
- Diretório `app/` — cada `page.tsx` é uma rota
- Grupos de rota: `app/(grupo)/` — parênteses no nome da pasta agrupam rotas sem afetar a URL
- Segmentos dinâmicos: `app/[slug]/page.tsx`, `app/[...catch]/page.tsx`
- Rotas paralelas: `app/@modal/`, `app/@sidebar/`
- Rotas interceptadas: `app/(.)photo/`, `app/(..)settings/`
- `app/not-found.tsx` — página 404 customizada
- `app/error.tsx` — boundary de erro por segmento de rota

### Layouts e Navegação
- `app/layout.tsx` — layout raiz (envolve tudo)
- `app/(grupo)/layout.tsx` — layouts específicos de grupo
- `app/loading.tsx` — UI de carregamento por segmento
- `app/template.tsx` — re-renderiza na navegação (diferente do layout)
- Procure imports de `<Link>` de `next/link`
- Procure `useRouter()` de `next/navigation` para navegação programática
- Procure `redirect()` de `next/navigation` em server components/actions

### Auth e Middleware
- `middleware.ts` (ou `.js`) na raiz do projeto — intercepta TODAS as requisições, comum para redirecionamentos de auth
- Verifique a config `matcher` dentro do middleware para ver quais rotas são protegidas
- NextAuth: `app/api/auth/[...nextauth]/route.ts` ou `auth.ts` na raiz
- Clerk: `middleware.ts` com `clerkMiddleware()`
- Procure chamadas de `auth()` ou `getServerSession()` em server components e route handlers

### Rotas de API
- `app/api/*/route.ts` — cada uma exporta métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`)
- Server Actions: diretiva `"use server"` em funções — tratam submissões de formulário sem rotas de API

### Formulários e Interatividade
- Componentes com `"use client"` são interativos (têm handlers de evento, estado)
- Server Components (padrão) NÃO são interativos — sem onClick, sem useState
- Server Actions podem ser usadas em `<form action={serverAction}>` mesmo em Server Components
- Procure hooks `useFormState`, `useFormStatus`, `useActionState`

### Gerenciamento de Estado
- React Context: procure `createContext` e wrappers `<Provider>`
- Zustand/Redux: procure arquivos de store, hooks `useStore`
- Estado de URL: `useSearchParams()`, `usePathname()`

---

## 2. Next.js (Pages Router)

### Rotas
- Diretório `pages/` — cada arquivo é uma rota (`pages/about.tsx` = `/about`)
- Dinâmico: `pages/[id].tsx`, `pages/[...slug].tsx`
- `pages/_app.tsx` — envolve todas as páginas (como layout raiz)
- `pages/_document.tsx` — documento HTML customizado
- `pages/404.tsx` — 404 customizado
- `pages/500.tsx` — 500 customizado

### Auth e Middleware
- `middleware.ts` na raiz do projeto (igual ao App Router)
- NextAuth: `pages/api/auth/[...nextauth].ts`
- `getServerSideProps` — executa em cada requisição, frequentemente verifica auth
- `getStaticProps` — executa no build (sem verificações de auth)

### Rotas de API
- `pages/api/*.ts` — cada arquivo é um endpoint de API

---

## 3. React (CRA / Vite + React Router)

### Rotas
- Procure imports de `react-router-dom`
- Definições de rota: `<Route path="/about" element={<About />} />`
- Verifique a configuração `createBrowserRouter` ou `<BrowserRouter>`
- Rotas podem estar em um arquivo dedicado (`routes.tsx`, `App.tsx`, `router.ts`)
- Rotas aninhadas: `<Route>` dentro de `<Route>` com `<Outlet />`
- Rotas lazy: `React.lazy(() => import('./pages/About'))`

### Layouts e Navegação
- `<Outlet />` — renderiza rotas filhas (como layout Next.js)
- `<Link to="/path">` — navegação client-side
- `useNavigate()` — navegação programática
- `<NavLink>` — link com estilo de estado ativo

### Auth
- Sem auth nativo — procure implementações customizadas
- Padrões comuns: `AuthContext`, componente `PrivateRoute`, wrapper `RequireAuth`
- Rotas protegidas: `<Route element={<RequireAuth />}> <Route path="/dashboard" ... /> </Route>`
- Procure armazenamento de token: `localStorage.getItem('token')`, `sessionStorage`, cookies
- Procure interceptors de API (Axios interceptors) que adicionam headers de auth

### Gerenciamento de Estado
- Context: `createContext`, `useContext`
- Redux: `store.ts`, `configureStore`, `useSelector`, `useDispatch`
- Zustand: `create()` de `zustand`
- React Query / TanStack Query: `useQuery`, `useMutation`

---

## 4. Vue / Nuxt

### Rotas Vue (standalone)
- `router/index.ts` ou `router.ts` — config do Vue Router
- Definições de rota: `{ path: '/about', component: About }`
- Guards de navegação: `router.beforeEach()` — verificações de auth
- Guards por rota: `beforeEnter` na config de rota
- Guards no componente: `beforeRouteEnter`, `beforeRouteLeave`

### Rotas Nuxt
- Diretório `pages/` — roteamento baseado em arquivos (como Next.js)
- `pages/[id].vue` — rotas dinâmicas
- `layouts/` — componentes de layout (`layouts/default.vue`)
- `middleware/` — middleware de rota (verificações de auth)
- `nuxt.config.ts` — registro de middleware, regras de rota
- `server/api/` — rotas de API

### Auth
- Módulo `@nuxtjs/auth-next` — verifique `nuxt.config.ts` para registro do módulo
- Auth customizado: procure stores Pinia/Vuex com estado de auth
- Middleware de rota: `middleware/auth.ts` com `defineNuxtRouteMiddleware`
- `navigateTo()` para redirecionamentos em middleware

### Formulários e Interatividade
- `v-model` — data binding bidirecional em inputs
- `@submit.prevent` — handler de submissão de formulário
- `v-if` / `v-show` — renderização condicional (roles, estado de auth)

---

## 5. SvelteKit

### Rotas
- `src/routes/` — roteamento baseado em arquivos
- `+page.svelte` — componente de página
- `+page.ts` / `+page.server.ts` — funções load (busca de dados)
- `+layout.svelte` — layout (como layout Next.js)
- `+error.svelte` — página de erro
- `[param]/` — rotas dinâmicas
- `(grupo)/` — grupos de rota

### Auth e Middleware
- `hooks.server.ts` — hooks de servidor, executa em cada requisição (como middleware)
- `+page.server.ts` — função load pode verificar auth e lançar redirecionamentos
- `+layout.server.ts` — verificações de auth no nível do layout
- Procure o padrão `locals.user` nos hooks

### Rotas de API
- `src/routes/api/*/+server.ts` — endpoints de API com exports `GET`, `POST`

### Formulários
- `<form method="POST">` com actions em `+page.server.ts`
- Diretiva `use:enhance` para progressive enhancement
- `$page.form` para acesso a dados do formulário

---

## 6. Angular

### Rotas
- `app-routing.module.ts` ou `app.routes.ts` (standalone) — config principal de rotas
- Módulos lazy-loaded: `loadChildren: () => import('./feature/feature.module')`
- Módulos de roteamento de feature: `*-routing.module.ts`
- Config de rota: `{ path: 'about', component: AboutComponent }`

### Auth e Guards
- Route guards: `canActivate`, `canDeactivate`, `canLoad`
- Arquivos de guard: `*.guard.ts` — implementam a interface `CanActivate`
- Interceptor de auth: `*.interceptor.ts` — adiciona headers de auth às requisições HTTP
- Procure implementações de `HttpInterceptor`

### Navegação
- `<router-outlet>` — renderiza rotas filhas
- `routerLink="/path"` — diretiva de link
- `Router.navigate(['/path'])` — navegação programática

### Formulários
- Formulários reativos: `FormGroup`, `FormControl`, `FormBuilder`
- Formulários template-driven: `ngModel`, `#form="ngForm"`
- Validadores: `Validators.required`, validadores customizados

### Estado
- Services com `@Injectable()` — estado singleton
- NgRx: `Store`, `Actions`, `Reducers`, `Effects`
- RxJS: padrões `BehaviorSubject`, `Observable`

---

## 7. Django

### Rotas
- `urls.py` — padrões de URL (nível de projeto e de app)
- `urlpatterns = [path('about/', views.about, name='about')]`
- Incluir URLs de app: `path('api/', include('myapp.urls'))`
- Namespace: `app_name = 'myapp'` no `urls.py` do app
- Verifique TODOS os arquivos `urls.py` em todos os apps — não apenas o raiz

### Auth
- `settings.py` > `AUTHENTICATION_BACKENDS` — backends de auth
- `settings.py` > `AUTH_USER_MODEL` — modelo de usuário customizado
- `settings.py` > `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `LOGOUT_REDIRECT_URL`
- `settings.py` > `MIDDLEWARE` — procure `AuthenticationMiddleware`, `SessionMiddleware`
- Decorator `@login_required` nas views
- `LoginRequiredMixin` nas class-based views
- `PermissionRequiredMixin` — verificações de role/permissão
- Decorator `@permission_required('app.can_edit')`
- Permissões customizadas em models: `class Meta: permissions = [...]`
- Grupos e permissões: tabelas `auth_group`, `auth_permission`

### Templates
- Diretório `templates/` (nível de projeto ou de app)
- `settings.py` > `TEMPLATES` > `DIRS` — diretórios de template
- Sintaxe de template: `{% extends "base.html" %}`, `{% block content %}`, `{{ variable }}`
- Tags de template: `{% url 'nome' %}` — resolução de URL em templates
- `{% if user.is_authenticated %}` — verificações de auth em templates
- `{% if perms.app.can_edit %}` — verificações de permissão em templates

### Formulários
- `forms.py` — definições de formulário (`ModelForm`, `Form`)
- CSRF: `{% csrf_token %}` em toda tag `<form>`
- `{{ form.as_p }}` / `{{ form.field }}` — renderização de formulário

### Admin
- `admin.py` — models registrados
- `/admin/` — sistema de auth e UI separados
- `@admin.register(Model)` ou `admin.site.register(Model)`

### Roles e Permissões
- Tabela `auth_user`: flags `is_staff`, `is_superuser`
- Tabela `auth_group`: grupos nomeados
- Tabela `auth_permission`: permissões por model (add, change, delete, view)
- `auth_user_groups`: atribuições de usuário-grupo
- Permissões customizadas: definidas em `Meta.permissions` do model
- `user.has_perm('app.codename_permissao')` — verificações no código

---

## 8. Laravel

### Rotas
- `routes/web.php` — rotas web (com middleware de sessão e CSRF)
- `routes/api.php` — rotas de API (stateless, tipicamente auth por token)
- `routes/auth.php` — rotas de auth (se usando Laravel Breeze/Fortify)
- `routes/channels.php` — canais de broadcast
- Grupos de rota: `Route::middleware(['auth'])->group(function() { ... })`
- Rotas resource: `Route::resource('posts', PostController::class)`

### Auth
- `config/auth.php` — guards, providers, config de reset de senha
- `app/Http/Middleware/Authenticate.php` — middleware de auth
- `app/Http/Middleware/` — todos os arquivos de middleware
- `app/Http/Kernel.php` — grupos de middleware (`web`, `api`, `auth`)
- Breeze/Jetstream/Fortify: verifique `composer.json` para o pacote de auth
- Sanctum: `config/sanctum.php` — auth por token para SPA/API
- `app/Models/User.php` — model de usuário, relacionamentos, roles
- Diretivas Blade `@auth` / `@guest` — verificações de auth em templates
- `$this->middleware('auth')` em controllers
- `Gate::define()` / classes `Policy` — autorização

### Templates (Blade)
- `resources/views/` — templates `.blade.php`
- `@extends('layout')` — herança de template
- `@section('content')` / `@yield('content')` — seções
- `@component` / `<x-componente>` — componentes Blade
- `@csrf` — token CSRF em formulários
- `@can('permissao')` / `@role('admin')` — verificações de permissão nas views

### Controllers
- `app/Http/Controllers/` — todos os controllers
- Controllers resource: métodos `index`, `create`, `store`, `show`, `edit`, `update`, `destroy`

### Roles e Permissões
- Pacote Spatie Permission: `config/permission.php`, trait `HasRoles` no model User
- Tabelas `roles`, `permissions`, `model_has_roles`, `role_has_permissions` (pivot)
- Pacote Bouncer: estrutura similar
- Customizado: coluna `role` na tabela users, ou relacionamento `roles`
- `$user->hasRole('admin')`, `$user->can('edit posts')` — verificações no código
- `@can('edit', $post)` — autorização Blade

---

## 9. Ruby on Rails

### Rotas
- `config/routes.rb` — todas as definições de rota
- `resources :posts` — rotas RESTful (index, show, new, create, edit, update, destroy)
- `namespace :admin do ... end` — rotas com namespace
- `root 'home#index'` — rota raiz
- Execute `rails routes` para ver todas as rotas resolvidas

### Auth
- Devise: `config/initializers/devise.rb`, `devise_for :users` nas rotas
- Customizado: `before_action :authenticate_user!` nos controllers
- Helper `current_user` — disponível em controllers e views
- `app/controllers/application_controller.rb` — controller base com filtros de auth
- Config de sessão: `config/initializers/session_store.rb`

### Templates (ERB / HAML)
- `app/views/` — organizado por nome do controller
- `app/views/layouts/application.html.erb` — layout principal
- `<%= yield %>` — ponto de inserção de conteúdo
- `<%= link_to 'Sobre', about_path %>` — helper de link
- `<% if user_signed_in? %>` — verificações de auth (Devise)
- `<%= form_with model: @post do |f| %>` — form builder
- Turbo/Hotwire: `data-turbo-action`, `turbo_frame_tag` — comportamento similar a SPA em app server-rendered

### Roles e Permissões
- Gem Rolify: tabela `roles`, `has_role?(:admin)`, `add_role(:editor)`
- Gem CanCanCan: `app/models/ability.rb` define permissões, `authorize!` nos controllers, `can?` nas views
- Gem Pundit: `app/policies/` — classes de policy por model
- Customizado: coluna `role` nos usuários, `enum role: [:user, :admin]`

---

## 10. Flask

### Rotas
- Decorators `@app.route('/path')` nas funções de view
- Blueprints: `bp = Blueprint('auth', __name__)`, `@bp.route('/login')`
- `app.register_blueprint(auth_bp, url_prefix='/auth')`
- Rotas podem estar espalhadas em múltiplos arquivos — siga os registros de blueprint

### Auth
- Flask-Login: decorator `@login_required`, `current_user`, `LoginManager`
- `login_user()` / `logout_user()` — gerenciamento de sessão
- `app.config['SECRET_KEY']` — chave de criptografia de sessão
- Customizado: verifique auth baseado em sessão ou JWT em middleware/decorators

### Templates (Jinja2)
- Diretório `templates/`
- `{% extends "base.html" %}`, `{% block content %}`, `{{ variable }}`
- `url_for('blueprint.funcao_de_view')` — geração de URL
- `{% if current_user.is_authenticated %}` — verificações de auth

### Roles
- Flask-Principal: permissões baseadas em role
- Customizado: coluna `role` no model de usuário, decorators customizados (`@admin_required`)

---

## 11. Express.js (com templates)

### Rotas
- `app.get('/path', handler)` / `app.post('/path', handler)` no arquivo principal
- Arquivos de router: `const router = express.Router()` em arquivos separados
- `app.use('/api', apiRouter)` — montagem de rotas
- Verifique `app.js`, `server.js`, `index.js` e o diretório `routes/`

### Auth
- Passport.js: `passport.use(new Strategy())`, `passport.authenticate('local')`
- Middleware customizado: `function isAuthenticated(req, res, next) { ... }`
- `express-session` — config de sessão
- JWT: pacote `jsonwebtoken`, middleware customizado para verificar tokens

### Templates
- Diretório `views/`
- EJS: arquivos `.ejs`, `<%= variavel %>`, `<%- include('partial') %>`
- Pug: arquivos `.pug`, sintaxe baseada em indentação
- Handlebars: arquivos `.hbs`, `{{variavel}}`, `{{> partial}}`
- `app.set('view engine', 'ejs')` — configuração da engine

---

## 12. Go (net/http + templates)

### Rotas
- `http.HandleFunc("/path", handler)` — biblioteca padrão
- Gorilla Mux: `r.HandleFunc("/path", handler).Methods("GET")`
- Chi: `r.Get("/path", handler)`
- Gin: `r.GET("/path", handler)`
- Echo: `e.GET("/path", handler)`
- Verifique `main.go` e arquivos `routes.go` ou `router.go`

### Auth
- Middleware customizado: `func AuthMiddleware(next http.Handler) http.Handler`
- Sessão: pacote `gorilla/sessions`
- JWT: pacote `golang-jwt/jwt`
- Procure cadeias de middleware na configuração do router

### Templates
- Pacote `html/template` — biblioteca padrão
- Diretório `templates/` ou `views/` com arquivos `.html` ou `.tmpl`
- `{{.Variable}}` — sintaxe de template
- `{{template "partial" .}}` — inclusão de template
- `{{if .User}}` — renderização condicional

---

## 13. Symfony / Twig

### Rotas
- `config/routes.yaml` — definições de rota em YAML
- Annotations/Attributes: `#[Route('/path')]` nos métodos do controller
- `src/Controller/` — classes de controller
- Execute `php bin/console debug:router` para ver todas as rotas

### Auth
- `config/packages/security.yaml` — configuração de segurança (firewalls, controle de acesso, providers)
- `src/Security/` — authenticators, voters, providers de usuário
- Atributo `#[IsGranted('ROLE_ADMIN')]` nos controllers
- `security.yaml` > `access_control` — regras de acesso baseadas em URL
- `security.yaml` > `role_hierarchy` — herança de roles

### Templates (Twig)
- Diretório `templates/` com arquivos `.html.twig`
- `{% extends 'base.html.twig' %}`, `{% block body %}`, `{{ variable }}`
- `{{ path('nome_da_rota') }}` — geração de URL
- `{% if is_granted('ROLE_ADMIN') %}` — verificações de permissão
- `{{ csrf_token('acao') }}` — tokens CSRF

### Roles
- `src/Entity/User.php` — método `getRoles()`
- Banco de dados: coluna JSON `roles` na tabela de usuários
- `role_hierarchy` em `security.yaml` — ROLE_ADMIN inclui ROLE_USER, etc.
- Voters: `src/Security/Voter/` — verificações de permissão granulares

---

## 14. Spring Boot MVC

### Rotas
- Classes `@Controller` com `@RequestMapping`, `@GetMapping`, `@PostMapping`
- `@RestController` — endpoints de API (retornam JSON)
- `src/main/java/**/controller/` — pacote de controllers
- Verifique implementações de `WebMvcConfigurer` para view resolvers e interceptors

### Auth
- Spring Security: bean `SecurityFilterChain` ou `WebSecurityConfigurerAdapter`
- `SecurityConfig.java` — define quais URLs requerem auth
- `.authorizeHttpRequests(auth -> auth.requestMatchers("/admin/**").hasRole("ADMIN"))`
- `@PreAuthorize("hasRole('ADMIN')")` — segurança a nível de método
- Implementação de `UserDetailsService` — carrega dados do usuário
- `src/main/resources/application.properties` ou `.yml` — configurações de segurança

### Templates (Thymeleaf)
- `src/main/resources/templates/` — arquivos `.html` com Thymeleaf
- `th:href="@{/path}"` — expressões de URL
- `th:if="${#authorization.expression('hasRole(''ADMIN'')')}"` — verificações de segurança em templates
- `th:each="item : ${items}"` — iteração
- `<form th:action="@{/submit}" method="post">` com CSRF automático

### Roles
- Tabelas `authorities` ou `roles` no banco de dados
- `UserDetails.getAuthorities()` — retorna authorities concedidas
- Anotações `@RolesAllowed`, `@Secured`, `@PreAuthorize`
- Hierarquia de roles: bean `RoleHierarchy`

---

## 15. ASP.NET MVC / Razor Pages

### Rotas
- `Controllers/` — controllers MVC com atributos `[Route]`
- `Pages/` — Razor Pages (roteamento baseado em arquivos, arquivos `.cshtml`)
- `Program.cs` ou `Startup.cs` — configuração de rotas (`app.MapControllerRoute()`)
- Areas: `Areas/Admin/Controllers/` — rotas agrupadas

### Auth
- Atributo `[Authorize]` em controllers/actions
- `[Authorize(Roles = "Admin")]` — baseado em role
- `[AllowAnonymous]` — isenções
- `Program.cs` — `builder.Services.AddAuthentication()`, `AddAuthorization()`
- Identity: `Microsoft.AspNetCore.Identity` — gerenciamento de usuário/role
- Auth baseado em claims: `User.Claims`, `User.IsInRole("Admin")`

### Templates (Razor)
- Arquivos `.cshtml` — sintaxe C# + HTML
- `@if (User.Identity.IsAuthenticated)` — verificações de auth
- `@if (User.IsInRole("Admin"))` — verificações de role
- `<form asp-action="Create" asp-controller="Items">` — tag helpers
- `@Html.AntiForgeryToken()` — proteção CSRF
- `_Layout.cshtml` — layout compartilhado
- `_ViewStart.cshtml` — atribuição de layout

### Roles
- Tabela `AspNetRoles`, tabela pivot `AspNetUserRoles`
- `UserManager<User>`, `RoleManager<Role>` — services de gerenciamento de role
- `[Authorize(Policy = "RequireAdmin")]` — autorização baseada em policy

---

## 16. PHP (Tradicional / Sem Framework)

### Rotas
- Sem arquivo central de rotas — cada arquivo `.php` é uma rota
- `index.php` — frequentemente o ponto de entrada, pode usar `$_GET['page']` para roteamento
- `.htaccess` — rewrites de URL do Apache (`RewriteRule ^about$ about.php`)
- `nginx.conf` — rewrites do Nginx
- Escaneie todos os arquivos `.php` na raiz web (`public/`, `www/`, `htdocs/`)
- Siga links `<a href="pagina.php">` e targets `<form action="submit.php">`

### Auth
- `session_start()` — inicialização de sessão
- `$_SESSION['user']` — auth baseada em sessão
- `header('Location: login.php')` — redirecionamentos para usuários não autenticados
- Verifique padrões `include 'auth_check.php'` no topo das páginas protegidas

### Templates
- PHP em si É a engine de template: `<?php echo $variable; ?>`, `<?= $variable ?>`
- Alguns projetos usam Smarty, Blade (standalone), ou Twig (standalone)
- Procure `include`, `require`, `include_once` para templates parciais

### Roles
- Coluna `role` na tabela de usuários (frequentemente verificada com queries SQL diretas)
- `$_SESSION['role']` — role armazenada na sessão
- `if ($_SESSION['role'] === 'admin')` — verificações de role inline

---

## 17. Remix

### Rotas
- `app/routes/` — roteamento baseado em arquivos
- `app/routes/_index.tsx` — rota raiz
- `app/routes/about.tsx` — `/about`
- `app/routes/posts.$id.tsx` — dinâmico: `/posts/:id`
- `app/routes/_layout.tsx` — rotas de layout
- Rotas aninhadas via estrutura de pastas ou notação de ponto

### Auth
- Funções `loader` — executam no servidor, podem verificar auth e redirecionar
- Funções `action` — tratam submissões de formulário
- `redirect()` de `@remix-run/node` — redirecionamentos server-side
- Sessão: `createCookieSessionStorage()` em um arquivo utilitário de sessão
- Procure funções helper `requireUser()` ou `getUser()` chamadas nos loaders

### Formulários
- `<Form method="post">` — componente de formulário Remix (enhanced client-side)
- Exports `action` em arquivos de rota tratam POST
- `useActionData()` — resultados de submissão de formulário
- `useFetcher()` — submissões de formulário sem navegação

---

## 18. Astro

### Rotas
- `src/pages/` — roteamento baseado em arquivos
- Arquivos `.astro` — componentes Astro (server-rendered por padrão)
- `.md` / `.mdx` — páginas Markdown
- `[param].astro` — rotas dinâmicas
- `[...slug].astro` — rotas catch-all

### Interatividade
- Astro é estático por padrão — sem JS client-side a menos que optado
- `client:load`, `client:visible`, `client:idle` — diretivas de hidratação
- Arquitetura de ilhas: componentes interativos incorporados em páginas estáticas
- Componentes de framework: componentes React, Vue, Svelte dentro de arquivos `.astro`

### Auth
- Sem auth nativo — verifique integrações (Astro Auth, Lucia, customizado)
- `src/middleware.ts` — middleware para verificações de auth
- Rotas de API: `src/pages/api/*.ts`
