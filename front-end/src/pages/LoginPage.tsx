import { useState, type FormEvent } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';

import { normalizeApiError } from '../api/http-error';
import { Button, Input } from '../components/ui';
import { getRoleHome } from '../routes/role-home';
import { useAuthStore } from '../store';

export function LoginPage(): React.JSX.Element {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);

  if (user) return <Navigate to={getRoleHome(user.role)} replace />;

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    try {
      const authenticatedUser = await login({ username: email, password });
      navigate(getRoleHome(authenticatedUser.role), { replace: true });
    } catch (caughtError) {
      const apiError = normalizeApiError(caughtError);
      setError(apiError.status === 401 ? 'E-mail ou senha incorretos.' : apiError.message);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit} noValidate>
      <Input label="E-mail" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
      <Input label="Senha" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
      {error ? <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p> : null}
      <Button className="w-full" type="submit" size="lg" isLoading={isLoading} loadingText="Entrando...">Entrar</Button>
      <p className="text-center text-sm text-slate-600">Ainda não tem conta?{' '}<Link className="font-semibold text-orange-600 hover:text-orange-500" to="/cadastro">Cadastre-se</Link></p>
    </form>
  );
}
