import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  base: '/pedidos-app/',
  plugins: [
    react(),
    federation({
      name: 'pedidos_app',
      filename: 'remoteEntry.js',
      exposes: {
        './Dashboard': './src/App.jsx',
      },
      shared: ['react', 'react-dom']
    })
  ],
  server: {
    port: 3001,
    host: '0.0.0.0',
    cors: true
  },
  preview: {
    port: 3001,
    host: '0.0.0.0',
    cors: true,
    allowedHosts: true
  },
  build: {
    target: 'esnext',
    minify: false,
    cssCodeSplit: false
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.js'],
  }
})

