import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import { RouterProvider } from 'react-router-dom'
import './index.css'
import { router } from './routes'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Suspense fallback={<main className="grid min-h-dvh place-items-center bg-[#fff1d6] text-sm font-semibold text-[#7a1e1e]">Carregando iLarica...</main>}>
      <RouterProvider router={router} />
    </Suspense>
  </StrictMode>,
)
