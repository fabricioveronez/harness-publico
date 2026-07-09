# Anatomia de um runbook de deploy/ops

Estrutura canônica de um runbook. É um **default forte, adaptável ao alvo** — não uma camisa de força. Inclua as seções-núcleo sempre; adapte o conteúdo ao tipo de deploy (VM+systemd, container, Kubernetes, serverless, PaaS). Se uma seção não se aplica ao caso, diga por que em vez de deixá-la vazia.

## Índice
1. Cabeçalho e resumo
2. Arquitetura do deploy
3. Pré-requisitos
4. Valores/configuração do ambiente
5. Procedimento de deploy
6. Verificação (executável)
7. Operação do dia a dia
8. Rollback
9. Troubleshooting
10. Segurança / notas
11. Adaptação por tipo de alvo

---

## 1. Cabeçalho e resumo
Uma frase do que o documento faz e **fronteira de escopo** (deploy do serviço X; infra é pré-requisito, fora do escopo). Liste em 2–3 bullets: stack/runtime, onde roda, forma de entrega. Isso orienta o leitor em segundos.

## 2. Arquitetura do deploy
Um diagrama ASCII simples do caminho da requisição até o dado, mostrando **onde a app roda** e **como recebe tráfego e fala com dependências** (banco, fila, cache). Exemplo de forma (adapte ao alvo):
```
Internet → [entrada: LB / Ingress / API GW] → [runtime: VM+systemd / container / pod / função] → [dados: banco / fila]
                                                └─ health check em <rota>
```
Anote fatos que impactam operação: health check (rota/porta), rede (endpoint privado do banco), portas.

## 3. Pré-requisitos
**Só o que o operador realmente precisa.** Separe em dois grupos:
- **Na máquina/ambiente do operador**: ferramentas (ssh, kubectl, cli da cloud, docker…), acesso.
- **Ambiente-alvo já existente (pré-requisito de infra, fora do escopo)**: o que precisa estar de pé (VM acessível, cluster, banco `available`, rede/SG liberando as portas, DNS). É condição de entrada, não passo do deploy.

## 4. Valores/configuração do ambiente
Tabela dos valores que o deploy consome, com **origem** e se é obrigatório. Segredos entram como placeholders + ponteiro para config gitignored/secret manager — **nunca** o valor. Ex.:

| Variável | Obrigatório | Descrição |
|---|:--:|---|
| `HOST` | sim | Host/endpoint do runtime-alvo |
| `DB_ENDPOINT` | sim | `host:porta` do banco |
| `DB_PASSWORD` | sim | Senha (em config/secret, fora do doc) |

## 5. Procedimento de deploy
Os passos para entregar e subir a app. No **modo Grounded**, derive-os dos comandos/scripts reais; se há um script (`deploy.sh`, pipeline), descreva o que ele faz em passos numerados e mostre o comando de invocação. Idempotência e "como refazer (redeploy)" são valiosos. Cubra: entrega do código/imagem → dependências → configuração (env/secret) → registrar/subir o serviço (systemd/kubectl/deploy) → habilitar no boot.

## 6. Verificação (executável)
**Comandos copy-paste** que provam sucesso ponta-a-ponta — não descrições. Boa verificação cobre camadas:
- serviço no host/plataforma ativo (`systemctl is-active`, `kubectl get pods`, status da função);
- health check pela entrada pública (`curl -w '%{http_code}'` na rota de health);
- caminho de dados real (uma escrita e uma leitura que provem conexão com o banco).
Use placeholders (`<HOST>`, `<URL>`) para o operador substituir. No modo Descrição, marque este bloco como **não verificado** até alguém rodar.

## 7. Operação do dia a dia
Comandos rotineiros: ver status, reiniciar, parar, seguir logs. Adapte ao alvo (`systemctl`/`journalctl`, `kubectl logs`/`rollout`, console da plataforma).

## 8. Rollback
Como reverter com segurança e como só **parar**. Seja explícito sobre o que o rollback **não** desfaz (ex.: migrations, dados já gravados). Se o deploy versiona releases, mostre como voltar à anterior; se não, mostre como reenviar a versão anterior.

## 9. Troubleshooting
Tabela `Sintoma | Causa provável | Ação`. No **modo Grounded**, popule com as **falhas realmente encontradas** na execução (erro concreto → causa → correção aplicada). Inclua também bugs conhecidos do serviço que impactam operação (marcando "código, não deploy" quando for o caso). Evite entradas genéricas que não ajudam ninguém.

## 10. Segurança / notas
Usuário/permissões de runtime (least privilege), como o segredo é injetado sem ficar exposto, TLS/HTTPS, e dívidas conhecidas (ex.: `SECRET_KEY` hardcoded a corrigir). Curto e honesto.

---

## 11. Adaptação por tipo de alvo
A **estrutura** acima é a mesma; muda o **vocabulário e os comandos** de cada seção:

| Seção | VM + systemd | Container / Compose | Kubernetes | Serverless / PaaS |
|---|---|---|---|---|
| Entrega | rsync/git + venv/build | build+push da imagem | imagem + manifests/helm | deploy do pacote/função |
| Subir serviço | `systemctl enable --now` | `docker compose up -d` | `kubectl apply` / `helm upgrade` | `deploy`/`push` da plataforma |
| Operação | `systemctl`/`journalctl` | `docker logs`/`ps` | `kubectl logs`/`rollout` | logs/console da plataforma |
| Rollback | reenviar versão + restart | tag anterior + up | `kubectl rollout undo` | promover versão anterior |
| Verificação | `curl` health + status | `curl` + `docker ps` | `kubectl get`/probe + `curl` | endpoint + métricas da plataforma |
