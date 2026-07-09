# Armadilhas Comuns em Testes E2E de Navegação

Casos extremos conhecidos, cenários complexos e soluções práticas que surgem durante a geração e execução de testes E2E. Organizado por categoria.

---

## Índice

1. [Auth e Gerenciamento de Sessão](#1-auth-e-gerenciamento-de-sessão)
2. [Formulários e Tratamento de Inputs](#2-formulários-e-tratamento-de-inputs)
3. [Timing e Estado Assíncrono](#3-timing-e-estado-assíncrono)
4. [Aplicações Server-Rendered](#4-aplicações-server-rendered)
5. [Ambiente e Infraestrutura](#5-ambiente-e-infraestrutura)
6. [Isolamento de Dados e Estado](#6-isolamento-de-dados-e-estado)
7. [Particularidades por Framework](#7-particularidades-por-framework)

---

## 1. Auth e Gerenciamento de Sessão

### 1.1 Persistência de Cookie/Sessão Entre Passos

**Problema:** Ferramentas de automação de browser podem perder cookies de sessão entre passos de navegação, fazendo o usuário parecer deslogado no meio do teste.

**Sintomas:** Teste passa no login (T03), mas o próximo teste (T04 Dashboard) redireciona de volta para a página de login.

**Solução:**
- Garanta que a instância do browser fique aberta em todos os passos dentro de um fluxo e entre fluxos dependentes.
- Não feche e reabra o browser entre testes dependentes. Se a ferramenta exigir reabertura, re-autentique primeiro.
- Verifique a persistência da sessão após o login checando uma página protegida imediatamente.

### 1.2 OAuth / Redirecionamentos para Provedores Externos

**Problema:** Fluxos de login que redirecionam para provedores externos (Google, GitHub, Facebook, Apple) não podem ser testados em ambiente E2E padrão — a página de login externa está fora do seu controle.

**Sintomas:** Clicar em "Login com Google" abre um formulário de login do Google com o qual o teste não consegue interagir (captchas, 2FA, restrições de domínio).

**Solução:**
- Verifique se o projeto tem uma **rota de bypass/login de dev** (comum em modo de desenvolvimento — ex.: `/api/auth/dev-login`, um endpoint só para testes que cria uma sessão sem OAuth).
- Verifique se há usuários seed com **login por credenciais** (email + senha) que podem ser usados em vez de OAuth.
- Se o único método de login for OAuth e não houver bypass, documente nas Observações dos casos de teste: "Login requer OAuth (Google). Login E2E não pode ser automatizado sem bypass de dev. Todos os testes que dependem de auth estão BLOQUEADOS."
- Sugira ao usuário adicionar uma rota de login só para dev para fins de teste.

### 1.3 Expiração de Token JWT no Meio do Teste

**Problema:** Suites de teste longas podem exceder o tempo de vida do token JWT de acesso (comumente 15 minutos a 1 hora). O token expira no meio do teste e chamadas de API subsequentes falham com 401.

**Sintomas:** Os primeiros testes passam, mas testes posteriores falham com erros de não autorizado apesar do login ter passado.

**Solução:**
- Verifique a configuração JWT do projeto para o tempo de vida do token (procure `expiresIn`, `maxAge`, `JWT_EXPIRATION` em env/config).
- Se o tempo de vida for curto (< 30 min), note nos Pré-requisitos: "Token expira em X minutos — re-autentique se a suite demorar mais."
- Se existir mecanismo de refresh token, garanta que a automação do browser permita atualizações de cookie/storage.

### 1.4 Problemas de CORS (Frontend e Backend em Portas Diferentes)

**Problema:** Em desenvolvimento, o frontend pode rodar em `localhost:3000` e a API em `localhost:8000`. A segurança do browser bloqueia requisições cross-origin.

**Sintomas:** Navegação funciona, mas chamadas de API falham silenciosamente ou retornam erros CORS no console. Formulários são submetidos mas nada acontece.

**Solução:**
- Verifique se o projeto usa um proxy (Next.js `rewrites`, Vite `proxy`, webpack `devServer.proxy`).
- Se não houver proxy, garanta que o backend tenha CORS configurado para a origin do frontend em desenvolvimento.
- Documente ambas as URLs nos Pré-requisitos se forem diferentes.

### 1.5 Autenticação Multi-Fator (MFA/2FA)

**Problema:** Se o MFA estiver habilitado para contas de teste, o fluxo de login requer um código TOTP ou SMS que não pode ser facilmente automatizado.

**Sintomas:** Formulário de login tem sucesso mas depois pede um código de verificação que o teste não consegue fornecer.

**Solução:**
- Verifique se o MFA pode ser desabilitado para contas de teste/seed.
- Procure bypass de MFA para modo de teste (alguns provedores de auth aceitam um código fixo como `000000` em desenvolvimento).
- Se o MFA não puder ser contornado, documente como bloqueador nas Observações.

---

## 2. Formulários e Tratamento de Inputs

### 2.1 Tokens CSRF em Formulários Server-Rendered

**Problema:** Frameworks server-rendered (Django, Laravel, Rails, Symfony) injetam tokens CSRF ocultos nos formulários. Se o teste submeter um formulário sem o token adequado, o servidor rejeita com 403 Forbidden.

**Sintomas:** Submissão de formulário retorna 403 ou erro "CSRF token missing/invalid".

**Solução:**
- Ao usar automação de browser (playwright-cli, Selenium), isso geralmente NÃO é um problema — o browser carrega a página com o token já incorporado no formulário, e submeter via click/fill o usa naturalmente.
- Isso só vira problema se você tentar submeter formulários via requisições HTTP diretas (curl, fetch) em vez de interação com o browser.
- Se testando via API diretamente, extraia o token CSRF do HTML da página ou dos cookies primeiro.

### 2.2 Editores de Texto Rico (TinyMCE, Quill, CKEditor, ProseMirror, Tiptap)

**Problema:** Editores de texto rico renderizam dentro de iframes ou usam divs `contenteditable`. Comandos `fill` padrão não funcionam porque o input não é um `<input>` ou `<textarea>` regular.

**Sintomas:** Comando `fill` não faz nada, digita no elemento errado, ou o editor aparece vazio após digitar.

**Solução:**
- Identifique o tipo de editor olhando os imports ou a estrutura do DOM.
- Para **editores baseados em iframe** (TinyMCE, CKEditor clássico): mude para o contexto do iframe primeiro, depois interaja com o body `contenteditable` dentro dele.
- Para **editores baseados em contenteditable** (Quill, Tiptap, ProseMirror): clique no container do editor para focar, depois use digitação por teclado (comando `type`) em vez de `fill`.
- Alguns editores expõem uma API JavaScript — use `eval` para definir conteúdo programaticamente: `editor.setContent('texto de teste')`.
- Nos passos de teste, documente: "Clique na área do editor, depois digite o conteúdo" em vez de "Preencha o campo do editor."

### 2.3 Date/Time Pickers Customizados

**Problema:** Date pickers customizados (react-datepicker, flatpickr, MUI DatePicker, etc.) não usam `<input type="date">` nativo. Eles renderizam calendários dropdown customizados que requerem clicar em células de dia específicas.

**Sintomas:** Comando `fill` com uma string de data não funciona ou preenche o input oculto mas não atualiza a UI.

**Solução:**
- Tente clicar no input de data para abrir o picker, depois navegue até o mês/ano correto, então clique na célula do dia específico.
- Alguns pickers aceitam input de teclado — tente limpar o campo e digitar a data no formato esperado.
- Como último recurso, use `eval` para definir o valor programaticamente e disparar um evento de change.
- Nos passos de teste, seja explícito: "Clique no campo de data > Navegue para [mês] > Clique no dia [15]" em vez de "Digite a data 2024-03-15."

### 2.4 Campos de Auto-Complete / Typeahead

**Problema:** Campos de busca-enquanto-digita buscam sugestões de uma API após um delay de debounce. Digitar o valor completo e pressionar Enter pode não funcionar se o dropdown ainda não aparecer.

**Sintomas:** Campo é preenchido mas nenhuma sugestão aparece, ou a sugestão errada é selecionada, ou o formulário submete com o texto bruto em vez da opção selecionada.

**Solução:**
- Digite alguns caracteres (não o valor completo), depois aguarde o dropdown aparecer (espere o container de sugestões ficar visível).
- Clique na sugestão desejada do dropdown em vez de pressionar Enter.
- Nos passos de teste: "Digite 'Joa' no campo de busca > Aguarde dropdown de sugestões > Clique em 'João Silva' das sugestões."

### 2.5 Campos de Upload de Arquivo

**Problema:** Inputs de upload de arquivo (`<input type="file">`) requerem um caminho de arquivo real no disco. Você não pode simplesmente digitar um nome de arquivo.

**Sintomas:** Comando `fill` não faz nada em inputs de arquivo. Botão de upload não responde ao clique.

**Solução:**
- Use o comando dedicado de upload de arquivo da automação do browser (ex.: `playwright-cli upload ./caminho/para/arquivo.pdf`).
- Garanta que um arquivo de teste exista no caminho esperado antes do teste rodar. Crie um nos Pré-requisitos se necessário.
- Para zonas de upload drag-and-drop, use a API de drag-and-drop de arquivo da ferramenta se disponível, ou recorra ao input de arquivo oculto.
- Nos passos de teste: "Faça upload do arquivo `test-data/exemplo.pdf` para o campo de upload" e note que o arquivo deve existir.

### 2.6 Validação de Formulário no Blur (Não no Submit)

**Problema:** Alguns formulários validam campos quando o usuário sai do campo (evento blur), não ao submeter. Se o teste preenche todos os campos e clica em submit sem disparar o blur, mensagens de validação podem não aparecer como esperado.

**Sintomas:** Teste preenche um campo com dado inválido e clica em submit — espera um erro de validação mas o formulário submete com sucesso (ou vice-versa).

**Solução:**
- Após preencher cada campo, clique no próximo campo (ou pressione Tab) para disparar a validação de blur antes de verificar mensagens de validação.
- Teste ambos os cenários: validação no nível do campo (no blur) e validação no nível do formulário (no submit).

---

## 3. Timing e Estado Assíncrono

### 3.1 Inputs de Busca com Debounce

**Problema:** Inputs de busca frequentemente têm debounce de 300-500ms. Digitar e imediatamente verificar resultados não encontrará nada porque a busca ainda não foi disparada.

**Sintomas:** Área de resultados de busca está vazia ou ainda mostrando resultados anteriores logo após digitar.

**Solução:**
- Após digitar a query de busca, aguarde os resultados aparecerem (espere um elemento de resultado específico ou o indicador de carregamento desaparecer).
- NÃO use delays fixos (`sleep 500ms`). Em vez disso, aguarde uma mudança visível: container de resultados se popula, spinner de carregamento desaparece, ou um texto específico aparece.
- Nos passos de teste: "Digite 'query' no campo de busca > Aguarde resultados aparecerem > Verifique que a lista de resultados contém [item esperado]."

### 3.2 Animações e Transições Atrasando Visibilidade de Elementos

**Problema:** Transições e animações CSS (fade-in, slide-in, abertura de modal) podem fazer elementos existirem no DOM mas ainda não serem interativos. Clicar durante uma animação pode falhar ou clicar no elemento errado.

**Sintomas:** Elemento é encontrado mas o clique não faz nada, ou clica em um overlay/backdrop em vez do botão.

**Solução:**
- Aguarde o elemento estar completamente visível e habilitado antes de interagir.
- Para modais: aguarde a animação do backdrop completar e o conteúdo do modal estar visível.
- Para notificações toast: elas podem se auto-dispensar — verifique-as rapidamente ou aguarde especificamente por elas.

### 3.3 WebSocket / Atualizações em Tempo Real

**Problema:** Funcionalidades guiadas por WebSockets (chat, notificações, atualizações ao vivo) não disparam requisições HTTP que a automação do browser pode interceptar. A UI atualiza assincronamente sem navegação.

**Sintomas:** Teste executa uma ação que deveria disparar uma atualização em tempo real, mas a UI não muda dentro do tempo esperado.

**Solução:**
- Após disparar uma ação, aguarde o elemento DOM específico atualizar em vez de aguardar uma requisição de rede.
- Se testando chat/mensagens, permita tempo extra para entrega via WebSocket.
- Documente nos passos de teste: "Aguarde badge de notificação mostrar contagem [1]" em vez de "Verifique que notificação foi enviada."

### 3.4 Atualizações de UI Otimistas

**Problema:** Alguns apps atualizam a UI imediatamente (atualização otimista) e revertem se a chamada de API falhar. O teste pode verificar sucesso durante a breve janela otimista, mas a operação real falhou.

**Sintomas:** Teste marca um passo como passado (item apareceu na lista), mas segundos depois o item desaparece e um toast de erro aparece.

**Solução:**
- Após ações que modificam dados (criar, editar, deletar), aguarde um momento e verifique que o estado está estável — confirme que nenhuma mensagem de erro aparece.
- Se o app mostrar notificações toast/snackbar, verifique ambas: a mensagem de sucesso esperada aparece E nenhuma mensagem de erro segue.
- Para fluxos críticos, verifique que os dados persistiram atualizando a página e verificando novamente.

### 3.5 Spinners de Carregamento / Skeleton Screens

**Problema:** Muitos apps mostram indicadores de carregamento (spinners, placeholders skeleton, efeitos shimmer) antes do conteúdo real renderizar. Verificar conteúdo enquanto estados de carregamento estão visíveis falhará.

**Sintomas:** Teste procura um texto ou elemento específico mas encontra o skeleton de carregamento.

**Solução:**
- Aguarde o indicador de carregamento desaparecer antes de verificar conteúdo.
- Procure pelos elementos de conteúdo reais em vez de verificar a ausência do loader (o loader pode estar oculto mas ainda no DOM).

---

## 4. Aplicações Server-Rendered

### 4.1 Padrão POST-Redirect-GET (PRG)

**Problema:** Apps server-rendered tipicamente tratam submissões de formulário via POST, depois redirecionam (302) para uma página GET. O teste deve aguardar o redirecionamento completar antes de verificar a página de resultado.

**Sintomas:** Teste submete um formulário e imediatamente verifica — mas a página ainda não redirecionou, então as verificações falham ou checam a página errada.

**Solução:**
- Após clicar no botão de submit, aguarde a URL mudar para o destino de redirecionamento esperado.
- Alternativamente, aguarde um elemento específico na página de resultado aparecer.
- Nos passos de teste: "Clique em submit > Aguarde redirecionamento para /itens > Verifique que mensagem de sucesso está visível."

### 4.2 Flash Messages (Exibição Única)

**Problema:** Frameworks server-rendered usam flash messages (Django `messages`, Rails `flash`, Laravel `session()->flash()`) que aparecem uma vez após um redirecionamento e desaparecem no próximo carregamento de página.

**Sintomas:** Teste submete um formulário, redirecionamento acontece, mas quando o teste verifica, a flash message já foi consumida por outra navegação.

**Solução:**
- Verifique a flash message IMEDIATAMENTE após o redirecionamento completar, antes de qualquer outra navegação.
- Não navegue nem atualize antes de checar a flash message.
- Nos passos de teste, faça a verificação da flash a primeira coisa após o redirecionamento: "Aguarde redirecionamento > Verifique que flash message 'Item criado com sucesso' está visível."

### 4.3 Timeout de Sessão Server-Side

**Problema:** Sessões server-side têm um timeout configurado (frequentemente 30 minutos de inatividade). Se a suite de teste demorar muito, a sessão expira mesmo que o browser ainda tenha o cookie de sessão.

**Sintomas:** Similar à expiração de JWT — testes posteriores falham com redirecionamento para login apesar do login anterior ter passado.

**Solução:**
- Verifique a configuração de timeout de sessão (Django `SESSION_COOKIE_AGE`, Laravel `lifetime` em `session.php`, Rails `expire_after`).
- Documente nos Pré-requisitos se o timeout for curto.
- Para suites longas, adicione um passo de re-autenticação na árvore de dependências se necessário.

### 4.4 Recarregamentos Completos de Página Limpando Estado JavaScript

**Problema:** Em apps server-rendered, toda navegação é um carregamento completo de página. Qualquer estado JavaScript (variáveis, event listeners, dados em memória) é perdido entre páginas. Isso é esperado mas pode confundir testes escritos com premissas de SPA.

**Sintomas:** Teste espera que estado persista após navegação (ex.: um filtro selecionado) mas a página recarrega e o estado é resetado.

**Solução:**
- Entenda que apps server-rendered dependem de parâmetros de URL, cookies ou sessões server-side para persistência de estado — não memória JavaScript.
- Verifique que o estado está na URL (`/itens?filtro=ativo`) ou persistido server-side após navegação.
- Não assuma que estado client-side sobrevive a transições de página.

---

## 5. Ambiente e Infraestrutura

### 5.1 Porta Já em Uso

**Problema:** O servidor dev não consegue iniciar porque outro processo (execução anterior de teste, outro servidor dev, serviço não relacionado) já está usando a porta.

**Sintomas:** Comando de início do servidor falha com "EADDRINUSE" ou "Address already in use."

**Solução:**
- Antes de iniciar o servidor, verifique se a porta já está ocupada.
- Se o projeto tem scripts de health check, use-os para detectar um servidor rodando antes de iniciar um novo.
- Mate processos órfãos se necessário (procure o script de shutdown do projeto).
- Documente os comandos de start/stop nos Pré-requisitos.

### 5.2 Variáveis de Ambiente ou Arquivo `.env` Faltando

**Problema:** O projeto requer variáveis de ambiente (URL do banco, chaves de API, segredos de auth) que não estão definidas. O servidor inicia mas crasha ou se comporta incorretamente.

**Sintomas:** Servidor inicia mas páginas mostram erros 500, conexão com banco falha, ou auth não funciona.

**Solução:**
- Verifique se há `.env.example`, `.env.sample`, ou instruções de configuração no README.
- Confirme que todas as variáveis de ambiente necessárias estão definidas antes de iniciar o servidor.
- Se o projeto tem um script de setup/init, execute-o primeiro.
- Documente as variáveis de ambiente necessárias nos Pré-requisitos.

### 5.3 Banco de Dados Não Migrado ou Sem Seed

**Problema:** O banco de dados existe mas não tem tabelas (migrations não executadas) ou sem dados de teste (seeds não executados). Páginas carregam mas mostram estados vazios ou erros.

**Sintomas:** Login falha porque não existem usuários. Dashboard mostra estado vazio porque não há itens com seed. API retorna 500 porque uma tabela não existe.

**Solução:**
- Verifique os comandos de migration e seed do projeto (Prisma, Django, Laravel, Rails, etc.).
- Execute migrations e seeds como parte dos Pré-requisitos.
- Documente os comandos exatos: "Execute `npm run db:migrate` depois `npm run db:seed`."

### 5.4 Versão Errada de Node/Python/Ruby/PHP

**Problema:** O projeto requer uma versão específica de runtime. Rodar com a versão errada causa erros crípticos.

**Sintomas:** Build falha com erros de sintaxe, dependências não instalam, ou o servidor crasha na inicialização.

**Solução:**
- Verifique arquivos de versão: `.node-version`, `.nvmrc`, `.python-version`, `.ruby-version`, `Gemfile` (restrição de versão Ruby), `composer.json` (restrição de versão PHP).
- Documente a versão de runtime necessária nos Pré-requisitos.

---

## 6. Isolamento de Dados e Estado

### 6.1 Violações de Constraint Única dos Dados Seed

**Problema:** Um teste tenta criar um item com nome/email/slug que já existe nos dados seed. O banco rejeita com erro de constraint única.

**Sintomas:** Teste "Criar item" falha com "UNIQUE constraint failed" ou "duplicate key value violates unique constraint."

**Solução:**
- Use dados de teste únicos que não colidirão com seeds — inclua timestamps ou sufixos aleatórios nos valores de teste (ex.: "Item de Teste 1709312456" em vez de "Item de Teste").
- Nos passos de teste, use valores claramente únicos: "Preencha o nome com 'Item E2E [timestamp]'."
- Alternativamente, verifique se o projeto tem um comando de reset de banco que pode ser executado antes dos testes.

### 6.2 Vazamento de Dados de Teste Entre Fluxos

**Problema:** O teste T05 cria um item que T06 precisa editar. Mas e se o item de T05 tiver um ID dinâmico? T06 não sabe qual item selecionar.

**Sintomas:** T06 não consegue encontrar o item criado por T05, ou clica no item errado.

**Solução:**
- Projete os passos de teste para encontrar itens por atributos visíveis (nome, título) em vez de por ID ou posição.
- Em T05, use um nome reconhecível. Em T06: "Encontre o item chamado 'Item E2E de Teste' na lista > Clique nele."
- Se os itens são ordenados, note a posição esperada: "Clique no primeiro item da lista" — mas isso é frágil se os dados seed mudarem.

### 6.3 Executar Testes Múltiplas Vezes Sem Reset

**Problema:** Executar a suite de teste uma segunda vez falha porque a primeira execução já criou dados de teste. Constraints únicas disparam, contagens não batem, ou fluxos encontram itens inesperados.

**Sintomas:** Testes passam na primeira execução mas falham na segunda com erros de duplicata ou contagens erradas.

**Solução:**
- Inclua uma nota de "limpeza" nos Pré-requisitos: "Resete o banco antes de executar os testes: `[comando]`."
- Ou projete testes para serem idempotentes — use dados únicos em cada execução e limpe depois de si mesmos (delete itens criados no último fluxo de teste).

---

## 7. Particularidades por Framework

### 7.1 Next.js: Server Components vs Client Components

**Problema:** O Next.js App Router usa Server Components por padrão. Elementos interativos (onClick, onChange, useState) só funcionam em Client Components. Um teste pode tentar interagir com um elemento que não tem handlers de evento porque é renderizado como Server Component.

**Sintomas:** Clicar em um botão não faz nada — sem navegação, sem mudança de estado, sem erro. O elemento existe mas é inerte.

**Solução:**
- Verifique se o componente tem a diretiva `"use client"`. Se não tiver, é um Server Component e não terá handlers de evento interativos.
- Durante a descoberta (Fase 1), note quais componentes são client vs server para evitar gerar passos de teste para elementos server-rendered não interativos.

### 7.2 Next.js: Redirecionamentos de Middleware

**Problema:** O middleware Next.js pode redirecionar requisições antes da página sequer renderizar. O teste navega para `/dashboard` mas é redirecionado para `/login` pelo middleware.

**Sintomas:** Teste navega para uma página e a URL muda inesperadamente. Verificações para a página original falham.

**Solução:**
- Leia o arquivo de middleware durante a descoberta para entender as regras de redirecionamento.
- Nos passos de teste, leve em conta os redirecionamentos: "Navegue para /dashboard > Verifique que URL é /login (redirecionamento esperado para usuários não autenticados)."

### 7.3 Django: Admin Site vs Rotas da Aplicação

**Problema:** O admin nativo do Django (`/admin/`) usa um sistema de auth e UI completamente separado da aplicação principal. Testes podem confundir login no admin com login na aplicação.

**Sintomas:** Teste faz login em `/admin/` com sucesso mas não consegue acessar a aplicação principal, ou vice-versa.

**Solução:**
- Trate admin e aplicação como escopos de teste separados com fluxos de login separados.
- Durante a descoberta, distingua claramente entre rotas de admin e rotas da aplicação.

### 7.4 Laravel: Grupos de Middleware

**Problema:** Laravel aplica grupos de middleware (`web`, `api`, `auth`) a grupos de rota. Rotas no grupo `api` não têm middleware de sessão/CSRF, enquanto rotas `web` têm. Testar o grupo errado com as premissas erradas leva a falhas.

**Sintomas:** Rotas de API funcionam sem CSRF mas rotas web o requerem. Sessão não persiste em rotas de API.

**Solução:**
- Durante a descoberta, note quais grupos de middleware se aplicam a quais rotas.
- Para testes E2E com browser, foque nas rotas `web` (browser trata CSRF automaticamente).

### 7.5 Rails: Turbo/Turbolinks (Hotwire)

**Problema:** Rails 7+ usa Turbo (anteriormente Turbolinks) para navegação similar a SPA dentro de um app server-rendered. Links não disparam recarregamentos completos de página — Turbo os intercepta e substitui o body da página via AJAX.

**Sintomas:** Teste espera um carregamento completo de página após clicar em um link, mas a URL muda sem um reload completo. Verificações de timing baseadas em eventos de carregamento de página falham.

**Solução:**
- Trate apps Rails com Turbo como híbridos — navegação é client-side (como SPA) mas renderização é server-side.
- Aguarde o Turbo terminar de substituir conteúdo em vez de aguardar eventos de carregamento de página.
- Procure `data-turbo="false"` em links que optam por sair do Turbo (esses fazem reloads completos).

### 7.6 SPA: Navegação Pelo Botão Voltar/Avançar do Browser

**Problema:** Em SPAs, os botões voltar/avançar do browser usam a History API. Alguns apps não tratam adequadamente o estado do histórico, levando a navegação quebrada ou UI desatualizada.

**Sintomas:** Teste clica no botão voltar mas a UI não atualiza, ou mostra uma versão desatualizada da página anterior.

**Solução:**
- Se a navegação voltar/avançar faz parte do fluxo de teste, teste-a explicitamente e note que pode se comportar diferentemente de cliques em links.
- Após navegação para trás, aguarde a UI atualizar completamente antes de verificar.

### 7.7 PHP (Tradicional): Sem Roteamento Client-Side

**Problema:** Apps PHP tradicionais (sem frameworks ou com frameworks mínimos) usam roteamento baseado em arquivos — cada arquivo `.php` é uma página separada. Não há definições de rota para descobrir; você precisa encontrar todos os arquivos `.php` e entender seu propósito.

**Sintomas:** Fase de descoberta não consegue encontrar um arquivo central de rotas porque não existe um.

**Solução:**
- Escaneie todos os arquivos `.php` na raiz web.
- Procure links `<a href="...">` e targets `<form action="...">` para mapear o grafo de navegação.
- Verifique `.htaccess` ou config do nginx para rewrites de URL que mapeiam URLs amigáveis para arquivos PHP.
