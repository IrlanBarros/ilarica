import { useState, type FormEvent } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';

import { normalizeApiError } from '../api/http-error';
import { Button, Input } from '../components/ui';
import { getRoleHome } from '../routes/role-home';
import { useAuthStore } from '../store';

export function LoginPage(): React.JSX.Element {
  const navigate = useNavigate();
  const location = useLocation();
  const user = useAuthStore((state) => state.user);
  const login = useAuthStore((state) => state.login);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | undefined>();
  const [passwordError, setPasswordError] = useState<string | undefined>();
  const registrationSucceeded = Boolean((location.state as { registered?: boolean } | null)?.registered);

  if (user) return <Navigate to={getRoleHome(user.role)} replace />;

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    const validEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    setEmailError(validEmail ? undefined : 'Informe um e-mail válido.');
    setPasswordError(password ? undefined : 'Informe sua senha.');
    if (!validEmail || !password) return;
    try {
      const authenticatedUser = await login({ username: email, password });
      navigate(getRoleHome(authenticatedUser.role), { replace: true });
    } catch (caughtError) {
      const apiError = normalizeApiError(caughtError);
      if (apiError.status === 401) setError('E-mail ou senha incorretos.');
      else if (apiError.status === 403) setError('Confirme seu e-mail institucional antes de entrar.');
      else setError('Não foi possível entrar. Verifique sua conexão e tente novamente.');
    }
  }

  return (
    <div className="w-full">
      <h1 className="font-display text-2xl font-extrabold text-ilarica-ink">Acesse sua conta</h1>
      {registrationSucceeded ? <p className="mt-5 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm font-semibold text-emerald-800" role="status">Cadastro concluído com sucesso. Entre com sua nova conta.</p> : null}
      <form className="mt-5 space-y-5" onSubmit={handleSubmit} noValidate>
        <Input label="E-mail Institucional" error={emailError} placeholder="seu@ufca.edu.br" type="email" autoComplete="email" value={email} onChange={(event) => { setEmail(event.target.value); setEmailError(undefined); }} className="h-12 border-ilarica-line px-4 text-sm text-ilarica-ink placeholder:text-[#a3a095] focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <Input label="Senha" error={passwordError} placeholder="••••••••" type="password" autoComplete="current-password" value={password} onChange={(event) => { setPassword(event.target.value); setPasswordError(undefined); }} className="h-12 border-ilarica-line px-4 text-sm text-ilarica-ink placeholder:text-[#a3a095] focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <div className="-mt-3 text-right"><Link to="/esqueci-senha" className="text-sm font-bold text-ilarica-orange hover:underline">Esqueci minha senha</Link></div>
        {error ? <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">{error}</p> : null}
        <Button className="h-[52px] w-full rounded-full bg-ilarica-orange text-base hover:bg-[#ed5b2a] focus-visible:ring-ilarica-orange" type="submit" size="lg" isLoading={isLoading} loadingText="Entrando...">Entrar</Button>
        <p className="text-center text-sm text-ilarica-muted">Novo por aqui?{' '}<Link className="font-bold text-ilarica-orange underline underline-offset-2 hover:text-[#ed5b2a]" to="/cadastro">Criar conta</Link></p>
      </form>
    </div>
  );
}
