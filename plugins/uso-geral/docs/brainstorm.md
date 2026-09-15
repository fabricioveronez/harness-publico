# brainstorm

Modo de maturação de ideias que pesquisa, analisa criticamente, aponta trade-offs e sugere melhorias sem criar ou executar nada até o usuário solicitar explicitamente. Use antes de implementar qualquer ideia de produto, feature, sistema, skill ou fluxo que ainda não está especificada o suficiente. O valor está em questionar premissas, não em validar o que você já pensa.

## Áreas especializadas

Além do modo generalista, a skill tem uma lente própria para **especificação de projeto de desenvolvimento**: levanta requisitos de negócio e de arquitetura, marca o que foi deduzido em vez de decidido, e verifica stack e versões em fonte externa antes de registrar. Ela infere a área e pede confirmação junto com as primeiras perguntas — se errar, você corrige numa frase.

Essa lente não desce ao nível de implementação: nada de estimativa, cronograma, código, endpoints ou modelagem de tabela. A saída é a **base para escrever a spec**, não a spec — o raciocínio, as alternativas descartadas e as pendências ficam preservados para quem for formalizar depois.

Outras áreas entram com o tempo; o que é comum a todas vive no `SKILL.md`, o que é específico vive em `references/`.

## Retomar um brainstorm salvo

Quando você documenta um brainstorm (Fase 5), o arquivo guarda o estado da sessão: o que foi decidido, o que é inferência, o que ficou em aberto e o que foi verificado em fonte externa e quando. Apontar esse arquivo numa sessão nova retoma de onde parou — a skill reabre pelo estado em vez de repetir perguntas, e sinaliza o que envelheceu desde a última consulta.

## Pré-requisitos e configuração

Nenhum. Funciona sem configuração prévia.

## Dependências externas

Nenhuma para o modo generalista. Na lente de especificação de projeto, consultas a **Context7** (documentação de bibliotecas e frameworks) e **busca web** são usadas para verificar versões, ferramentas e stack — sem elas, esses itens viram pergunta em vez de fato verificado.

## Skills relacionadas

- **banco-de-ideias** — após madurar a ideia no brainstorm, use banco-de-ideias para registrá-la no Notion antes de implementar
- **escrever-prd** — use escrever-prd para formalizar a ideia após o brainstorm, gerando um documento de requisitos estruturado
- **skill-creator** — quando a ideia for uma nova skill, use skill-creator após sair do modo brainstorm

## Exemplos de uso

```
Quero criar um sistema de automação de posts no LinkedIn

Tenho uma ideia de app de finanças pessoais com IA, pensa comigo

Entra em modo brainstorm — quero criar uma skill para gerar relatórios de projetos

Me ajuda a planejar a arquitetura de uma API de notificações

Quero especificar um projeto novo antes de começar a codar: um sistema de agendamento para clínicas

Continua o brainstorm de ontem — docs/brainstorm-sistema-agendamento.md
```

## Limitações conhecidas

- Nenhum arquivo é criado, editado ou executado durante o brainstorm — é um modo puramente conversacional
- A skill sai do modo brainstorm apenas quando o usuário usar frases como "pode criar", "implementa", "vai em frente"
- Não substitui pesquisa de mercado ou validação com usuários reais
- A lente de especificação não produz estimativa, cronograma, código, endpoints nem modelagem de tabela — custo entra só como restrição declarada por você, nunca como número
- O documento gerado é base para escrever a spec, não a spec final: preserva o raciocínio e as pendências em vez de apresentar só o resultado
- Fatos externos ficam datados no documento — numa retomada, o que foi verificado há muito tempo precisa ser reconsultado
