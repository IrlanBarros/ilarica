import { useEffect } from 'react';
import { Navigate, Outlet } from 'react-router-dom';

import { tokenStorage } from '../api';
import { useAuthStore } from '../store';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps): React.JSX.Element {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isHydrated = useAuthStore((state) => state.isHydrated);
  const checkAuth = useAuthStore((state) => state.checkAuth);
  const token = tokenStorage.get();

  useEffect(() => {
    if (token && !isHydrated) {
      void checkAuth();
    }
  }, [checkAuth, isHydrated, token]);

  if (token && !isHydrated) {
    return <p className="p-8 text-center text-slate-600">Carregando sua conta...</p>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (children) {
    return <>{children}</>;
  }

  return <Outlet />;
}
