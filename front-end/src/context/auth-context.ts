import { createContext } from 'react';

import type { LoginRequest, TokenResponse, User, UserCreate } from '../types';

export type AuthStatus = 'loading' | 'authenticated' | 'unauthenticated';

export interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  isAuthenticated: boolean;
  isHydrated: boolean;
  login: (payload: LoginRequest) => Promise<TokenResponse>;
  logout: () => void;
  register: (payload: UserCreate) => Promise<User>;
  refreshUser: () => Promise<User | null>;
}

export const AuthContext = createContext<AuthContextValue | null>(null);
