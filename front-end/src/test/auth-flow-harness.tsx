import { useAuth } from '../context';
import type { LoginRequest } from '../types';

interface AuthFlowHarnessProps {
  credentials?: LoginRequest;
}

const defaultCredentials: LoginRequest = {
  username: 'qa-auth@ufca.edu.br',
  password: 'Secret123',
  grant_type: 'password',
};

export function AuthFlowHarness({ credentials = defaultCredentials }: AuthFlowHarnessProps) {
  const { isAuthenticated, isHydrated, login, logout, status, user } = useAuth();

  async function handleLogin(): Promise<void> {
    await login(credentials);
  }

  return (
    <section>
      <p data-testid="status">{status}</p>
      <p data-testid="hydrated">{String(isHydrated)}</p>
      <p data-testid="authenticated">{String(isAuthenticated)}</p>
      <p data-testid="user-email">{user?.email ?? 'anonymous'}</p>
      <button type="button" onClick={() => void handleLogin()}>
        login
      </button>
      <button type="button" onClick={logout}>
        logout
      </button>
    </section>
  );
}