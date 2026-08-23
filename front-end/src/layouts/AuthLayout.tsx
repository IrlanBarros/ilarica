import { Outlet } from 'react-router-dom';

export function AuthLayout(): React.JSX.Element {
  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-orange-50 via-white to-amber-100 px-4">
      <section className="w-full max-w-md rounded-3xl border border-orange-100 bg-white/90 p-8 shadow-xl shadow-orange-100/40 backdrop-blur">
        <div className="mb-6 text-center">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-orange-500">iLarica</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-900">Acesse sua conta</h1>
        </div>
        <Outlet />
      </section>
    </main>
  );
}