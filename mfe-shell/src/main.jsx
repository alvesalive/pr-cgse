import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import '@govbr-ds/core/dist/core.css'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
