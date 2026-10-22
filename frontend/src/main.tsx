import React from 'react'
import ReactDOM from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import App from './App'
import ErrorBoundary from './components/ErrorBoundary'
import { BasketProvider } from './data/basket'
import './styles/index.css'

// Hash URLs work on GitHub Pages, which cannot rewrite deep links.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <HashRouter>
        <BasketProvider>
          <App />
        </BasketProvider>
      </HashRouter>
    </ErrorBoundary>
  </React.StrictMode>,
)
