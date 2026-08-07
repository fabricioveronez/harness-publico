# Heurísticas de validação

Guia do modo Validar para (1) classificar cada divergência entre documento e
código por impacto e (2) decidir onde o ajuste mora.

## Por que classificar antes de agir

O ajuste errado é pior que o drift. "Consertar" o contrato para bater com um
código que se desviou apaga a intenção original — e o pior é que fica coerente:
o documento passa a descrever o acidente, e ninguém percebe que houve um. Por
isso toda divergência passa por avaliação de impacto **antes** de qualquer edição.

## Régua de tamanho

Tamanho é medido por **impacto no contrato**, não por esforço de edição.

| Sinal | Classe |
|---|---|
| diferença textual/nominal que não muda o comportamento contratado (nome de campo, redação ambígua mas satisfeita, nota faltando) | **pequena** |
| detalhe local que o código expressa diferente do doc, sem alterar Rule/Edge case/critério | **pequena** |
| comportamento implementado **contradiz** uma Rule ou Edge case | **grande** |
| US do SPEC **não entregue** pelo código | **grande** |
| critério de aceite **falhando** na verificação | **grande** |
| ajuste que exigiria **mudar o PRD** | **grande** |
| SPEC **defasado** do PRD a ponto de a projeção não refletir mais a fonte | **grande** |
| divergência **estrutural** em PLAN/TASKS (task nova necessária, task obsoleta) | **grande** (delegar) |

Na dúvida, **grande**. Perguntar custa barato; ajustar errado um contrato, caro.

## Direção do ajuste (autoridade `PRD > SPEC > código`)

1. **Código desviou do contrato** → gap de código. Reporte; a correção é
   reimplementar no modo Implementar. Não edite código aqui.
2. **SPEC desviou da realidade** e a realidade está certa, sem PRD tocando o
   ponto → ajuste o `SPEC.md`. Pequena: automático. Grande: pergunte.
3. **O ponto vem do PRD** → o PRD é autoridade. Ajuste no PRD via `escrever-prd`
   e reprojete o SPEC no modo Preparar. Sempre **grande**.
4. **Estrutural em PLAN/TASKS** → delegue ao modo Preparar (reconciliação).

Regra de ouro: este modo só edita **frontmatter** (status, no fechamento, e sempre
pelo `transicao.py`) e a **coerência textual do SPEC** em divergências pequenas.
Todo o resto ele reporta ou delega.

## Exemplos

**Pequena — ajuste automático**
> SPEC: "o campo `sobrenome` é opcional". Código e PRD: o campo se chama `apelido`,
> opcional, comportamento idêntico. → Divergência nominal; o contrato não muda.
> Sem PRD tocando o nome, ajuste o SPEC para `apelido` e registre.

**Grande — gap de código (reportar)**
> SPEC (Rule): "token expirado redireciona para /login". Código: retorna 500. → O
> comportamento contradiz a Rule e o contrato tem razão. Reporte como gap; sugira
> o modo Implementar. Não ajuste documento.

**Grande — vem do PRD (perguntar)**
> A implementação passou a exigir 2FA, com aval informal de negócio, mas o PRD não
> menciona 2FA. → O ajuste mudaria o PRD. Pause e pergunte: registrar no PRD via
> `escrever-prd` e reprojetar, ou reverter o código?

**Grande — estrutural (delegar)**
> Uma US nova apareceu no PRD depois da implementação e não tem task. →
> Reestruturação de TASKS: delegue ao modo Preparar (reconciliação). Não crie task
> aqui.
