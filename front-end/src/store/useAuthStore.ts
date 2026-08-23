import { create } from 'zustand';

import { logout as authLogout, login as authLogin } from '../services/auth.service';
import { getMe } from '../services/user.service';
import { tokenStorage } from '../api/token-storage';
import type { LoginRequest, TokenResponse, User } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginRequest) => Promise<User>;
  logout: () => void;
  checkAuth: () => Promise<User | null>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,

  async login(credentials: LoginRequest): Promise<User> {
    set({ isLoading: true });

    try {
      const tokenResponse: TokenResponse = await authLogin(credentials);
      tokenStorage.set(tokenResponse.access_token);

      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false });
      return user;
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      throw error;
    }
  },

  logout(): void {
    authLogout();
    set({ user: null, isAuthenticated: false, isLoading: false });
  },

  async checkAuth(): Promise<User | null> {
    const token = tokenStorage.get();
    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false });
      return null;
    }

    set({ isLoading: true });

    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false });
      return user;
    } catch {
      tokenStorage.clear();
      set({ user: null, isAuthenticated: false, isLoading: false });
      return null;
    }
  },
}));