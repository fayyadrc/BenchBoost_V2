import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import ManagerPage from './pages/ManagerPage.tsx'
import { ManagerProvider } from './context/ManagerContext.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <ManagerProvider>
        <Routes>
          <Route path="/" element={<App />} />
          <Route path="/manager" element={<ManagerPage />} />
        </Routes>
      </ManagerProvider>
    </BrowserRouter>
  </StrictMode>,
)
