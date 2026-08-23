import {
  type PropsWithChildren,
  type ReactElement,
  useEffect,
  useRef,
  useState,
} from 'react';

import { login as loginRequest, logout as logoutRequest, register as registerRequest } from '../services/auth.service';
import { getMe } from '../services/user.service';
import type { LoginRequest, TokenResponse, User, UserCreate } from '../types';
import { tokenStorage } from '../api';
import { AuthContext, type AuthContextValue, type AuthStatus } from './auth-context';

export function AuthProvider({ children }: PropsWithChildren): ReactElement {
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>(() =>
    tokenStorage.get() ? 'loading' : 'unauthenticated',
  );
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;

    return () => {
      mountedRef.current = false;
    };
  }, []);

  async function hydrateCurrentUser(): Promise<User | null> {
    if (!tokenStorage.get()) {
      if (mountedRef.current) {
        setUser(null);
        setStatus('unauthenticated');
      }
      return null;
    }

    if (mountedRef.current) {
      setStatus('loading');
    }

    try {
      const authenticatedUser = await getMe();

      if (mountedRef.current) {
        setUser(authenticatedUser);
        setStatus('authenticated');
      }

      return authenticatedUser;
    } catch (error) {
      if (mountedRef.current) {
        setUser(null);
        setStatus('unauthenticated');
      }

      throw error;
    }
  }

  useEffect(() => {
    if (!tokenStorage.get()) {
      setUser(null);
      setStatus('unauthenticated');
      return;
    }

    void hydrateCurrentUser().catch(() => undefined);
  }, []);

  async function handleLogin(payload: LoginRequest): Promise<TokenResponse> {
    const tokenResponse = await loginRequest(payload);
    await hydrateCurrentUser();
    return tokenResponse;
  }

  function handleLogout(): void {
    logoutRequest();
    setUser(null);
    setStatus('unauthenticated');
  }

  async function handleRegister(payload: UserCreate): Promise<User> {
    return registerRequest(payload);
  }

  const contextValue: AuthContextValue = {
    user,
    status,
    isAuthenticated: status === 'authenticated' && user !== null,
    isHydrated: status !== 'loading',
    login: handleLogin,
    logout: handleLogout,
    register: handleRegister,
    refreshUser: hydrateCurrentUser,
  };

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
}
