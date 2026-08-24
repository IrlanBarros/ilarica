import type { UserRole } from '../types';

const ROLE_HOME: Record<UserRole, string> = {
  customer: '/',
  courier: '/entregas',
  canteen_staff: '/vendedor/cardapio',
  admin: '/admin',
};

export function getRoleHome(role: UserRole): string {
  return ROLE_HOME[role];
}
