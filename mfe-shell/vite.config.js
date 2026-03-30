import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'shell_app',
      remotes: {
        // Aponta para a string que o NGINX roteia. Se rodar local fora do docker: 'http://localhost:3001/pedidos-app/assets/remoteEntry.js'
        pedidos_app: '/pedidos-app/assets/remoteEntry.js'
      },
      shared: ['react', 'react-dom', 'react-router-dom']
    })
  ],
  server: {
    port: 3000,
    host: '0.0.0.0',
    cors: true
  },
  preview: {
    port: 3000,
    host: '0.0.0.0',
    cors: true,
    allowedHosts: true
  },
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false
  }
})
