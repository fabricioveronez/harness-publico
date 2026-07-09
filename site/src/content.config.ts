import { defineCollection, reference, z } from 'astro:content';
import type { Loader } from 'astro/loaders';
import { readFile, readdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import matter from 'gray-matter';
import { site } from './site.config';

// ---------------------------------------------------------------------------
// Regra de higiene (ver plano): NUNCA globar recursivamente. Os arquivos reais
// vivem em profundidade fixa; qualquer coisa mais funda é lixo (.venv, snapshots,
// outputs de eval). Por isso lemos diretórios em níveis exatos com fs, não glob.
//   skills reais: <repo>/plugins/<plugin>/skills/<skill>/SKILL.md
//   docs reais:   <repo>/plugins/<plugin>/docs/<skill>.md
// ---------------------------------------------------------------------------

function repoRootFrom(configRoot: URL): string {
  // configRoot aponta para .../site/ ; o repo é o pai.
  return fileURLToPath(new URL('../', configRoot));
}

async function listDirs(dir: string): Promise<string[]> {
  if (!existsSync(dir)) return [];
  const entries = await readdir(dir, { withFileTypes: true });
  return entries.filter((e) => e.isDirectory()).map((e) => e.name);
}

// Extrai um resumo curto do doc: o texto entre o H1 e o primeiro H2.
// Fallback: primeiro parágrafo não-vazio que não seja heading.
function extractBlurb(markdown: string): string {
  const body = matter(markdown).content;
  const lines = body.split(/\r?\n/);
  const collected: string[] = [];
  let seenH1 = false;
  for (const raw of lines) {
    const line = raw.trim();
    if (!seenH1) {
      if (line.startsWith('# ')) seenH1 = true;
      continue;
    }
    if (line.startsWith('## ')) break;
    if (line === '') {
      if (collected.length > 0) break; // fim do primeiro parágrafo
      continue;
    }
    if (line.startsWith('#')) continue;
    collected.push(line);
  }
  return collected.join(' ').trim();
}

// --- Loader: plugins (grupos) -------------------------------------------------
function pluginsLoader(): Loader {
  return {
    name: 'harness-plugins',
    async load({ store, parseData, config }) {
      const repo = repoRootFrom(config.root);
      const marketplacePath = path.join(repo, '.claude-plugin', 'marketplace.json');
      const marketplace = JSON.parse(await readFile(marketplacePath, 'utf8')) as {
        plugins: { name: string; source: string; description: string }[];
      };

      store.clear();
      for (const p of marketplace.plugins) {
        const pluginJsonPath = path.join(repo, 'plugins', p.name, '.claude-plugin', 'plugin.json');
        let version = '';
        if (existsSync(pluginJsonPath)) {
          const pj = JSON.parse(await readFile(pluginJsonPath, 'utf8')) as { version?: string };
          version = pj.version ?? '';
        }
        const data = await parseData({
          id: p.name,
          data: {
            name: p.name,
            description: p.description,
            version,
            installCommand: `npx skills add ${site.repo.slug}/plugins/${p.name}/skills`,
          },
        });
        store.set({ id: p.name, data });
      }
    },
  };
}

// --- Loader: skills (itens, protagonistas) -----------------------------------
function skillsLoader(): Loader {
  return {
    name: 'harness-skills',
    async load({ store, parseData, renderMarkdown, config }) {
      const repo = repoRootFrom(config.root);
      const pluginsDir = path.join(repo, 'plugins');

      store.clear();
      const seen = new Set<string>();

      const pluginNames = await listDirs(pluginsDir);
      for (const plugin of pluginNames) {
        const skillsDir = path.join(pluginsDir, plugin, 'skills');
        const skillDirs = await listDirs(skillsDir);
        for (const skillDir of skillDirs) {
          const skillMd = path.join(skillsDir, skillDir, 'SKILL.md');
          if (!existsSync(skillMd)) continue; // pasta sem SKILL.md direto não é skill

          if (seen.has(skillDir)) {
            throw new Error(
              `Nome de skill duplicado entre plugins: "${skillDir}". Ids/URLs precisam ser únicos.`,
            );
          }
          seen.add(skillDir);

          const fm = matter(await readFile(skillMd, 'utf8'));
          const name = (fm.data.name as string) ?? skillDir;
          const description = String(fm.data.description ?? '').trim();

          const docPath = path.join(pluginsDir, plugin, 'docs', `${skillDir}.md`);
          const hasDoc = existsSync(docPath);

          let blurb = '';
          let rendered;
          if (hasDoc) {
            const docRaw = await readFile(docPath, 'utf8');
            blurb = extractBlurb(docRaw);
            rendered = await renderMarkdown(docRaw, {
              fileURL: new URL(`plugins/${plugin}/docs/${skillDir}.md`, config.root),
            });
          }

          const data = await parseData({
            id: skillDir,
            data: { name, plugin, description, blurb, hasDoc },
          });
          store.set({ id: skillDir, data, rendered });
        }
      }
    },
  };
}

const plugins = defineCollection({
  loader: pluginsLoader(),
  schema: z.object({
    name: z.string(),
    description: z.string(),
    version: z.string(),
    installCommand: z.string(),
  }),
});

const skills = defineCollection({
  loader: skillsLoader(),
  schema: z.object({
    name: z.string(),
    plugin: reference('plugins'),
    description: z.string(),
    blurb: z.string(),
    hasDoc: z.boolean(),
  }),
});

export const collections = { plugins, skills };
