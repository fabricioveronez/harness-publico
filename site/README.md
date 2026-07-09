# Site — vitrine da harness-library

Vitrine local (Astro) do marketplace. É uma **projeção pura** dos arquivos do repo:
lê `../.claude-plugin/marketplace.json`, `../plugins/*/.claude-plugin/plugin.json`,
`../plugins/*/skills/*/SKILL.md` e `../plugins/*/docs/*.md` no build. **Nenhum conteúdo é
duplicado aqui** — adicionar um plugin/skill/doc no repo atualiza o site no próximo build.

## Rodar local

```bash
cd site
npm install
npm run dev        # http://localhost:4321
npm run build      # gera dist/ + índice Pagefind
npm run preview    # serve dist/ (com busca funcionando)
```

## Arquitetura (site-first)

Este site é o **primeiro projeto real**; um template genérico de marketplace será
**extraído depois** a partir do que se provar reutilizável. Por isso branding/taxonomia
(`src/site.config.ts`) e tokens de tema (`src/styles/theme.css`) já ficam isolados da lógica.

- **Skill é a protagonista** da vitrine (grid no índice); **plugin** é filtro + página própria.
- **Unidade de instalação é o plugin** (`/plugin install <plugin>@fabricio-marketplace`).
- **Conteúdo do card** = 1º parágrafo do `docs/<skill>.md`. **Detalhe** = o doc inteiro renderizado.
- **Skill sem doc** aparece marcada como *sem documentação* (o site é também um painel de completude).
- **Busca**: Pagefind (client-side, indexado no build). Em `dev` o box degrada com aviso.

## Regra de higiene do loader (importante)

`src/content.config.ts` lê os arquivos em **profundidade fixa** com `fs`, nunca com glob
recursivo. Skills reais são só `plugins/<plugin>/skills/<skill>/SKILL.md` (SKILL.md direto na
pasta da skill); qualquer coisa mais funda — `.venv`, `skill-snapshot/`, `outputs/docs/` de
evals — é lixo e fica de fora. Docs reais são só `plugins/<plugin>/docs/<skill>.md`.

## Fora de escopo (por ora)

- Deploy (repo privado; teste local primeiro).
- Extração do template genérico.
- Docs órfãos (doc sem skill de mesmo nome) como páginas de overview.
