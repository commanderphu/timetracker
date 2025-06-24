// vite.config.js

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Dies ist die Standard-Konfiguration für Vite mit React.
// Wir entfernen alle expliziten CSS- oder PostCSS-Einstellungen von hier.
export default defineConfig({
  plugins: [react()],
})