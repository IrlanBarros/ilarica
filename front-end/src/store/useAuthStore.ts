import { create } from 'zustand';

import { logout as authLogout, login as authLogin, register as authRegister } from '../services/auth.service';
import { getMe } from '../services/user.service';
import { tokenStorage } from '../api/token-storage';
import type { LoginRequest, TokenResponse, User, UserCreate } from '../types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isHydrated: boolean;
  login: (credentials: LoginRequest) => Promise<User>;
  register: (payload: UserCreate) => Promise<User>;
  logout: () => void;
  checkAuth: () => Promise<User | null>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: false,
  isHydrated: !tokenStorage.get(),

  async login(credentials: LoginRequest): Promise<User> {
    set({ isLoading: true });

    try {
      const tokenResponse: TokenResponse = await authLogin(credentials);
      tokenStorage.set(tokenResponse.access_token);

      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false, isHydrated: true });
      return user;
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false, isHydrated: true });
      throw error;
    }
  },

  async register(payload: UserCreate): Promise<User> {
    set({ isLoading: true });

    try {
      const user = await authRegister(payload);
      set({ isLoading: false });
      return user;
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },

  logout(): void {
    authLogout();
    set({ user: null, isAuthenticated: false, isLoading: false, isHydrated: true });
  },

  async checkAuth(): Promise<User | null> {
    const token = tokenStorage.get();
    if (!token) {
      set({ user: null, isAuthenticated: false, isLoading: false, isHydrated: true });
      return null;
    }

    set({ isLoading: true });

    try {
      const user = await getMe();
      set({ user, isAuthenticated: true, isLoading: false, isHydrated: true });
      return user;
    } catch {
      tokenStorage.clear();
      set({ user: null, isAuthenticated: false, isLoading: false, isHydrated: true });
      return null;
    }
  },
}));
