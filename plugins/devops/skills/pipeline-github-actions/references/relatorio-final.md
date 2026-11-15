# Relatório final

Em pt-BR, neste formato. A tabela de resultado é por job, não por run: `skipped` aparece como **não testado**.

```markdown
## Resultado

| Workflow | Gatilho testado | Job | Resultado |
|---|---|---|---|
| CI | pull_request | verificar | ✅ |
| CI | push main | publicar | ✅ |
| Provisionamento | workflow_dispatch | plan | ⚪ skipped — não testado |

## Verificação externa
- (o que foi conferido fora do GitHub e como: curl, certificado, portas, API do provedor, registry)

## Correções feitas
- `abc1234` fix(escopo): ... — causa: ...

## Não exercitado
- (caminhos/jobs que não rodaram e como testá-los)

## Pendências
- (docs que ficaram desatualizados, segredo que vazou e deve ser rotacionado, follow-ups)
```
