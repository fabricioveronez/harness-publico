# brainstorm-for-systems

Brainstorm de sistema que já sai com a documentação técnica: conduz a conversa com a lente de especificação do `brainstorm`, grava cada decisão durável como ADR `proposto` e cada termo do domínio no glossário no momento em que cristalizam, e no portão da consolidação aceita os ADRs confirmados, apaga os revertidos e gera o TRD via `escrever-trd`.

## Quando usar

Acionada só pelo usuário (`/brainstorm-for-systems`), quando o assunto é um sistema a construir e você quer terminar a conversa com ADRs e TRD prontos. Para explorar sem registrar nada, use `/brainstorm`.

## Composição

| Peça | Papel |
|---|---|
| `brainstorm` | conduz a conversa (lente de especificação forçada) |
| `escrever-trd` | Modo Decision para ADR; Criação/Edição para o TRD no portão |

As duas são obrigatórias: faltando qualquer uma, a skill avisa e para. Não vêm no pacote do `sdd`; o `sdd init` avisa quando não as encontra.
| `docs/glossary.md` | vocabulário do domínio, com sinônimos a evitar |

Detalhes: `skills/brainstorm-for-systems/references/` (critério de ADR, portão da Fase 4). Guia geral do fluxo: `docs/uso.md`.
