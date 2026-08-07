# Heurísticas de validação e classificação de divergência

Guia operacional da `validar-implementacao` para (1) classificar cada
divergência entre documento e código por **impacto e tamanho** e (2) decidir a
**direção do ajuste** pela autoridade `PRD > SPEC > código`.

## Índice

- [Por que classificar antes de agir](#por-que-classificar-antes-de-agir)
- [Régua de tamanho: pequena vs grande](#régua-de-tamanho-pequena-vs-grande)
- [Direção do ajuste (autoridade)](#direção-do-ajuste-autoridade)
- [Exemplos](#exemplos)

## Por que classificar antes de agir

O ajuste errado é pior que o drift: "consertar" o contrato para bater com um
código que se desviou apaga a intenção. Por isso toda divergência passa por uma
avaliação de impacto **antes** de qualquer edição. A classificação decide o
caminho: pequena → ajuste automático; grande → perguntar ao usuário.

## Régua de tamanho: pequena vs grande

A régua é fixa — tamanho é medido por **impacto no contrato**, não por esforço
de edição.

| Sinal | Classe |
|---|---|
| Diferença textual/nominal que não muda o comportamento contratado (nome de campo, redação ambígua mas satisfeita, nota faltando) | **Pequena** |
| Detalhe local que o código expressa diferente do doc, sem alterar Rule/Edge case/critério | **Pequena** |
| Comportamento implementado **contradiz** uma Rule ou Edge case | **Grande** |
| US do SPEC **não entregue** pelo código | **Grande** |
| Critério de aceite (§5a) **falhando** na verificação | **Grande** |
| Ajuste que exigiria **mudar o PRD** (o ponto divergente vem do PRD) | **Grande** |
| SPEC **defasado** do PRD a ponto de a projeção não refletir mais a fonte | **Grande** |
| Divergência **estrutural** em PLAN/TASKS (task nova necessária, task obsoleta) | **Grande** (delegar) |

Na dúvida entre pequena e grande, tratar como **grande** — perguntar custa
barato; ajustar errado um contrato, caro.

## Direção do ajuste (autoridade)

Classificado o tamanho, a **autoridade** decide onde o ajuste mora. Ordem:
`PRD > SPEC > código`.

1. **Código desviou do contrato** (o contrato tem razão) → é **gap de código**.
   Reportar; a correção é reimplementar via `implementar-task`. Esta skill
   **não edita código**.
2. **SPEC desviou da realidade** e a realidade está correta, **sem PRD** (ou o
   ponto não vem do PRD) → ajustar o `SPEC.md`. Pequena: automático. Grande:
   perguntar.
3. **O ponto divergente vem do PRD** → o PRD é autoridade. O ajuste correto é no
   PRD (via `escrever-prd`) e depois reprojetar o SPEC via `preparar-execucao`.
   Sempre **grande** → perguntar.
4. **Divergência estrutural em PLAN/TASKS** → **delegar** à `preparar-execucao`
   (modo reconciliação). Esta skill não reestrutura o bundle.

Regra de ouro: esta skill só edita **frontmatter** (status, no fechamento) e a
**coerência textual do SPEC** em divergências **pequenas**. Todo o resto ela
reporta ou delega.

## Exemplos

**Pequena — ajuste automático no SPEC**
> SPEC: "o campo `sobrenome` é opcional". Código e PRD: o campo se chama
> `apelido`, opcional, comportamento idêntico. → Divergência nominal, não muda o
> contrato. Sem PRD tocando o nome → ajustar o SPEC para `apelido`. Registrar.

**Grande — gap de código (reportar)**
> SPEC/PRD (Rule): "token expirado redireciona para /login". Código: retorna
> 500. → Comportamento contradiz a Rule; o contrato tem razão. Gap de código:
> reportar e sugerir `implementar-task`. Não ajustar documento.

**Grande — vem do PRD (perguntar)**
> Implementação (com aval de negócio informal) passou a exigir 2FA, mas o PRD
> não menciona 2FA. → Ajuste mudaria o PRD (autoridade). Pausar, apresentar, e
> perguntar: registrar no PRD via `escrever-prd` + reprojetar SPEC, ou reverter
> o código?

**Grande — estrutural (delegar)**
> Uma US nova apareceu no PRD depois da implementação e não tem task. →
> Reestruturação de TASKS: delegar à `preparar-execucao` (reconciliação). Não
> criar task aqui.
