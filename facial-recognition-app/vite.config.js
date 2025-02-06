import { defineConfig } from 'vite/dist/node/index.js'
import react from '@vitejs/plugin-react/dist/index.d.mts'
import tailwindcss from '@tailwindcss/vite/dist/index.d.mts'


// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
})
