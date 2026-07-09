// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// Site vitrine da harness-library. Lê os plugins/skills do repo pai (../) no build.
export default defineConfig({
  site: 'http://localhost:4321',
  vite: {
    plugins: [tailwindcss()],
  },
});
