# criar-plan

Gera e mantém o scaffolding de execução (`PLAN.md` + `TASKS.md`) a partir de
um PRD pronto. Cobre três modos — **criação** (do zero), **edição** (reabre
preservando `[X]`) e **reconciliação sob demanda** (releitura do PRD quando
ele muda). PLAN descreve a abordagem técnica; TASKS é o checklist de
execução. Ambos ficam em `./aidev/{nnn-slug-do-prd}/`, um diretório efêmero
gitignorado — o PRD permanece a fonte de verdade histórica.

## Pré-requisitos e configuração

- Um PRD em `status: pronto` ou `em-progresso` no projeto alvo (gerado pela
  skill `escrever-prd`). PRDs com `status: concluido` são imutáveis — a skill
  recusa gerar plano para eles.
- A skill pergunta o diretório de PRDs na primeira invocação (default
  sugerido: `./docs/prds/`).
- A skill verifica o `.gitignore` do projeto alvo e pede confirmação para
  adicionar `aidev/` antes de gravar qualquer arquivo. Se o usuário recusar,
  a skill aborta sem gravar.

## Dependências externas

Nenhuma. A skill é autossuficiente. Se existir um TRD (`./docs/trd.md`,
`./TRD.md` ou `./docs/TRD.md`) é carregado como contexto técnico global; se
não existir, entra em **mini-modo de coleta** (entrevista curta sobre stack
e convenções).

## Skills relacionadas

- **escrever-prd** — pré-requisito. Gera o PRD que esta skill consome.
- **implementar-task** (futura) — executa as tasks geradas e marca `[X]`
  conforme as entrega.
- **validar-implementacao** (futura) — verifica coerência código ↔ PRD ao
  final.

## Exemplos de uso

```
Gera o plano do PRD 003

Quebra o PRD de autenticação em tasks

Cria PLAN e TASKS para a feature de pagamentos

Preciso do plano de implementação do PRD 007

Reabre o plano do PRD 003 — quero adicionar uma task para rate limiting

Reconcilia o plano do PRD 005: adicionei uma US nova

Atualiza as tasks, o PRD mudou
```

## Limitações conhecidas

- PLAN e TASKS vivem em `./aidev/{slug}/`, que é **gitignorado**. Trocar de
  máquina ou apagar o diretório perde o progresso local — regenerar do PRD
  (custo aceito; PRD é a fonte de verdade, PLAN/TASKS são scaffolding).
- A skill **não marca `[X]`** em tasks — isso é papel de quem executa
  (humano ou skill `implementar-task`).
- A skill **não edita o PRD** — qualquer mudança de comportamento volta
  para `escrever-prd`.
- **Reconciliação é sempre manual**: só roda sob pedido explícito do
  usuário. A skill não detecta automaticamente mudanças no PRD.
- Cobertura depende da qualidade do PRD — USs sem `Rules` ou `Edge cases`
  forçam inferência e podem gerar tasks frágeis. A skill alerta nesses
  casos antes de prosseguir.
- **PRD com `status: concluido` é rejeitado** — por design, PRDs concluídos
  são imutáveis. Se a feature precisa evoluir, abrir novo PRD.
