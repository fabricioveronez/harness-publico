---
prd_number: "003"
status: pronto
priority: alta
created: 2026-01-10
issue: "#42"
depends_on: ["001"]
references: []
---

# PRD 003: Convites por email

## 1. Contexto

Administradores precisam convidar membros para uma organização.

## 2. Solução Proposta

Enviar convite individual por email com validade de sete dias.

### Fora do escopo

- Convites em lote.

## 3. Funcionalidades

### US01: Enviar convite

Como administrador, quero convidar uma pessoa para participar da organização.

**Rules:**
- O convite expira em sete dias.

**Edge cases:**
- Email já convidado → informar que existe convite pendente.

### US02: Aceitar convite

Como convidado, quero aceitar o convite para entrar na organização.

**Rules:**
- O convite só pode ser aceito uma vez.

**Edge cases:**
- Convite já aceito → abrir a organização existente.

## 4. Fluxo de Negócio

Administrador envia → convidado recebe → convidado aceita.

## 5. Critérios de Aceite

| Critério | Razão de negócio | Como verificar |
|---|---|---|
| Convite válido adiciona o membro | Permitir colaboração | Teste de ponta a ponta |

## 6. Milestones

### Milestone 1: Envio de convite disponível

**Por que é um marco:** administradores conseguem iniciar a entrada de membros.

**Funcionalidades:** US01

**Checklist de aceite:**
- [x] Email de convite é enviado.

**Aprovador:** Product Manager

### Milestone 2: Entrada por convite disponível

**Por que é um marco:** convidados conseguem participar da organização.

**Funcionalidades:** US02

**Checklist de aceite:**
- [ ] Convite válido adiciona o membro.

**Aprovador:** Product Manager

## 7. Riscos e Dependências

Depende do PRD 001.

## 8. Referências

Nenhuma.

## 9. Registro de Decisões

- **2026-01-10:** convite expira em sete dias. Motivo: limitar exposição.
