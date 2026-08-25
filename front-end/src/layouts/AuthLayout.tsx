import { useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';

import { tokenStorage } from '../api';
import { useAuthStore } from '../store';

export function AuthLayout(): React.JSX.Element {
  const location = useLocation();
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const isHydrated = useAuthStore((state) => state.isHydrated);

  useEffect(() => {
    if (tokenStorage.get() && !isHydrated) void checkAuth();
  }, [checkAuth, isHydrated]);

  return (
    <main className="flex min-h-dvh items-center justify-center bg-ilarica-cream sm:px-6 sm:py-10">
      <section className={`flex min-h-dvh w-full max-w-[402px] flex-col px-6 py-10 sm:min-h-0 sm:rounded-[32px] sm:border sm:border-ilarica-line sm:bg-ilarica-cream sm:py-14 sm:shadow-[0_24px_80px_rgba(31,31,31,0.08)] ${location.pathname === '/cadastro' ? 'justify-start sm:justify-center' : 'justify-center'}`}>
        <Outlet />
      </section>
    </main>
  );
}
