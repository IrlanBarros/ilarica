import { Navigate, Outlet } from 'react-router-dom';

import { getRoleHome } from '../routes/role-home';
import { useAuthStore } from '../store';
import type { UserRole } from '../types';

interface RoleRouteProps {
  allowedRoles: UserRole[];
  children?: React.ReactNode;
}

export function RoleRoute({ allowedRoles, children }: RoleRouteProps): React.JSX.Element {
  const user = useAuthStore((state) => state.user);
  if (!user) return <Navigate to="/login" replace />;
  if (!allowedRoles.includes(user.role)) return <Navigate to={getRoleHome(user.role)} replace />;
  return children ? <>{children}</> : <Outlet />;
}
