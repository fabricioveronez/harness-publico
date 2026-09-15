// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Site vitrine da harness-library. Lê os plugins/skills do repo pai (../) no build.
export default defineConfig({
  site: 'https://fabricioveronez.github.io',
  base: '/harness-publico/',
  vite: {
    plugins: [tailwindcss()],
  },
});
