export type UserRole = 'customer' | 'courier' | 'canteen_staff' | 'admin';

export interface UserBase {
  name: string;
  email: string;
  role: UserRole;
}

export interface User extends UserBase {
  id: string;
  is_active: boolean;
}

export interface UserCreate {
  name: string;
  email: string;
  password: string;
  role?: UserRole;
}

export interface UserUpdate {
  name?: string | null;
  email?: string | null;
  role?: UserRole | null;
}