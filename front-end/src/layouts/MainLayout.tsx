import { Outlet, useLocation } from 'react-router-dom';

import { useAuthStore } from '../store';

export function MainLayout(): React.JSX.Element {
  const logout = useAuthStore((state) => state.logout);
  const location = useLocation();

  if (location.pathname === '/' || location.pathname === '/carrinho' || location.pathname === '/checkout' || location.pathname.startsWith('/cantina/') || location.pathname.startsWith('/pedidos/') || location.pathname.startsWith('/pagamentos/') || location.pathname.startsWith('/vendedor/')) {
    return <Outlet />;
  }

  return (
    <main className="min-h-screen bg-slate-50 text-slate-900">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-4 shadow-sm">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.25em] text-orange-500">iLarica</p>
          <h1 className="text-xl font-bold">Painel principal</h1>
        </div>
        <button
          type="button"
          onClick={logout}
          className="rounded-full bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-700"
        >
          Sair
        </button>
      </header>

      <section className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <Outlet />
      </section>
    </main>
  );
}
