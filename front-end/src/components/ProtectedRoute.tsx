import { Navigate, Outlet } from 'react-router-dom';

import { tokenStorage } from '../api';
import { useAuthStore } from '../store';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export function ProtectedRoute({ children }: ProtectedRouteProps): React.JSX.Element {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const token = tokenStorage.get();

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  if (children) {
    return <>{children}</>;
  }

  return <Outlet />;
}