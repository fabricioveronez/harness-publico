# typescript-practices

Boas práticas e padrões de qualidade prescritivos para código TypeScript — naming, interface vs type, type safety, orientação a objetos, error handling e organização de arquivos. Aplica convenções diretamente ao código sem explicar cada decisão, priorizando consistência sobre didática. Ativa sempre que a tarefa envolver escrever ou revisar TypeScript, mesmo sem o usuário pedir explicitamente por "boas práticas".

## Pré-requisitos e configuração

- Projeto em TypeScript (qualquer versão razoavelmente moderna)
- `tsconfig.json` com `strict: true` recomendado para aproveitar todas as regras de type safety

## Dependências externas

Nenhuma.

## Skills relacionadas

- **nextjs-bootstrap** — projetos criados pelo bootstrap já nascem com `strict: true`, então typescript-practices se aplica naturalmente
- **guia-de-testes** — escrever testes em TypeScript seguindo essas convenções

## Exemplos de uso

```
Escreve esse service em TypeScript seguindo nossas práticas

Revisa esse arquivo .ts e aponta o que está fora do padrão

Converte esse código JS para TypeScript com boas práticas

Implementa o repositório de pedidos em TS

Refatora essa classe seguindo orientação a objetos
```

## Limitações conhecidas

- Guia prescritivo — pode conflitar com estilo já estabelecido no projeto. Quando houver conflito com convenções do repositório (ex.: interfaces com prefixo `I`), as convenções do projeto prevalecem; informe isso no prompt
- Orientação a objetos é tratada como padrão — a skill aponta explicitamente as situações em que abordagem funcional é preferível, mas projetos puramente funcionais exigem override manual
- Exemplos detalhados de padrões avançados (discriminated unions, type guards, generics aplicados, async patterns) ficam em `references/patterns.md` — leia apenas quando a tarefa exigir
- Não substitui ESLint/Biome — é guia de escrita, não ferramenta de lint automatizado
- Não impõe estrutura de diretórios específica — sugere princípios (co-localizar tipos, barrel apenas em módulos públicos, limite de 300 linhas) mas respeita a organização já definida no projeto
