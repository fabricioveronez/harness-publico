# Modo Validar — conferir a entrega e fechar o ciclo

Confere se o que foi **construído** é coerente com o que foi **especificado**,
trata o drift entre documento e código, e fecha o ciclo promovendo o status.

Diferença em relação ao gate final do modo Implementar: aquele reporta o estado
das tasks e dos critérios. **Este julga a coerência da entrega** contra o
contrato, ajusta drift e fecha.

## 1. Carregar

Leia o bundle: `SPEC.md` (o contrato), `PLAN.md` (arquivos afetados, comando de
teste, estratégia de teste), `TASKS.md` (estado `[X]`).

Quando `prd:` aponta um slug, carregue o PRD — ele é a fonte de verdade. Com
`prd: none`, o SPEC é a fonte. Carregue o TRD se o PLAN o referencia.

## 2. Pré-condições

- **Tasks pendentes** → avise que a implementação não terminou e sugira o modo
  Implementar. O usuário pode pedir validação parcial mesmo assim — registre como
  parcial e **não feche**.
- **Linha de base verde** → rode o `Comando de teste:`. Vermelho pré-existente
  contamina o julgamento: reporte e pare antes de avaliar coerência.

## 3. Conferir código × contrato

```bash
python3 scripts/cobertura.py --bundle .aidev/{slug}
```

Ele dá a matriz US × critério × task e os alvos automatizáveis. Execute os alvos —
são os mesmos que o gate final executou, porque estão **declarados** no SPEC, não
reinterpretados a partir de prosa. Liste os manuais.

Para cada US: existe código que a entrega? Cada Rule está honrada no comportamento
implementado? Cada Edge case tem tratamento correspondente?

Registre cada desvio como um item de divergência: o que o contrato diz, o que o
código faz, e onde.

## 4. Conferir SPEC × PRD

Só quando há PRD. O SPEC é projeção dele — confira se a projeção continua fiel:
US, Rules, Edge cases e critérios refletem o PRD atual. Divergência aqui significa
que o SPEC envelheceu contra a fonte, e o conserto é reprojetar no modo Preparar.

## 5. Classificar antes de agir

A régua está em `heuristicas-validacao.md`. Resumo:

| Sinal | Classe |
|---|---|
| diferença textual/nominal que não muda o comportamento contratado | pequena |
| detalhe local que o código expressa diferente, sem alterar Rule/Edge/critério | pequena |
| comportamento implementado **contradiz** Rule ou Edge case | grande |
| US do SPEC **não entregue** | grande |
| critério de aceite **falhando** | grande |
| ajuste que exigiria mudar o **PRD** | grande |
| SPEC defasado do PRD a ponto de a projeção não refletir a fonte | grande |
| divergência **estrutural** em PLAN/TASKS | grande (delegar) |

Na dúvida entre pequena e grande, trate como **grande**. Perguntar custa barato;
ajustar errado um contrato, caro.

**Pequena** → ajuste o texto do SPEC automaticamente e registre no relatório.
**Grande** → **pause e pergunte** antes de qualquer alteração, apresentando a
divergência, o impacto e as opções.

### Direção do ajuste, pela autoridade `PRD > SPEC > código`

1. **Código desviou do contrato** → é gap de código. Reporte; a correção é
   reimplementar no modo Implementar. Este modo **não edita código**.
2. **SPEC desviou da realidade** e a realidade está certa, sem PRD tocando o ponto
   → ajuste o `SPEC.md`. Pequena: automático. Grande: pergunte.
3. **O ponto vem do PRD** → o PRD é autoridade. O ajuste correto é no PRD (via
   `escrever-prd`) e depois reprojetar o SPEC no modo Preparar. Sempre grande.
4. **Estrutural em PLAN/TASKS** → delegue ao modo Preparar (reconciliação). Este
   modo não reestrutura o bundle.

A regra que sustenta as quatro: **nunca conserte o contrato para bater com um
código que se desviou**. Isso apaga a intenção original e é o modo de falha mais
caro do ciclo — o documento passa a descrever o acidente, e ninguém percebe.

## 6. Fechar

Só quando **não há divergência grande em aberto** — as pequenas foram ajustadas,
as grandes foram resolvidas pelo usuário ou delegadas e sanadas.

```bash
python3 scripts/transicao.py bundle {slug} --para concluido
```

O script fecha `SPEC.md`, `PLAN.md` e `TASKS.md`, e então **verifica o conjunto**:

- **sem manifesto** (1 fatia) → fecha o PRD junto;
- **com manifesto e alguma fatia aberta** → fecha só o bundle e reporta quais
  faltam. PRD e manifesto ficam abertos;
- **com manifesto e esta era a última** → fecha manifesto e PRD na mesma operação.

Essa guarda é a razão de o fechamento passar pelo script. Com N fatias a validação
roda uma vez por fatia; fechar o PRD no primeiro fechamento trancaria as irmãs —
PRD `concluido` é imutável, e com ele o modo Implementar aborta e o modo Preparar
recusa reconciliar. A feature ficaria no meio, sem saída a não ser abrir um PRD
novo. Não contorne editando frontmatter à mão.

O bundle **permanece no lugar**, congelado pelo status como registro do que foi
construído.

## 7. Relatório

Conforme `templates/template-relatorio.md`: cobertura de US e de critérios,
resultado dos alvos executados, divergências com classificação e tratamento dado,
e o veredito.

```
Modo: validar
Estado: <coerente e fechado | divergências tratadas | pausado por divergência grande | validação parcial>
Cobertura: <N/M USs · N/M critérios>
Divergências: <pequenas ajustadas: N | grandes em aberto: N>
Fechamento: <bundle concluído | conjunto aguardando N fatia(s) | não fechado>
Próxima ação sugerida: <1 linha>
```

## Fora deste modo

Não edita código, não reestrutura PLAN/TASKS, não edita o corpo do PRD (só promove
o status pelo script, sob a guarda), não ajusta divergência grande sem
confirmação, e não move nem apaga o bundle — o fechamento é por status, no lugar.
