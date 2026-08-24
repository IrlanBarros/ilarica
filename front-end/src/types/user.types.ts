import type { UUID } from './api.types';

export type UserRole = 'customer' | 'courier' | 'canteen_staff' | 'admin';

export interface UserBase {
  name: string;
  email: string;
  whatsapp: string;
  role: UserRole;
}

export interface User extends UserBase {
  id: UUID;
  is_active: boolean;
  is_email_validated: boolean;
}

export interface UserCreate {
  name: string;
  email: string;
  whatsapp: string;
  password: string;
  role?: Extract<UserRole, 'customer' | 'courier'>;
}

export interface UserUpdate {
  name?: string | null;
  email?: string | null;
  whatsapp?: string | null;
  role?: UserRole | null;
}
