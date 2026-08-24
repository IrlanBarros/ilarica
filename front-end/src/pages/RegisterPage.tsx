import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { normalizeApiError } from '../api/http-error';
import { Button, Input } from '../components/ui';
import { useAuthStore } from '../store';
import type { UserCreate } from '../types';

type PublicRole = NonNullable<UserCreate['role']>;

export function RegisterPage(): React.JSX.Element {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [form, setForm] = useState({ name: '', email: '', whatsapp: '', password: '', passwordConfirmation: '', role: 'customer' as PublicRole });
  const [error, setError] = useState<string | null>(null);

  function updateField(field: keyof typeof form, value: string): void {
    setForm((current) => ({ ...current, [field]: value }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    if (form.password !== form.passwordConfirmation) {
      setError('A confirmação de senha deve ser igual à senha.');
      return;
    }
    try {
      await register({ name: form.name, email: form.email, whatsapp: form.whatsapp, password: form.password, role: form.role });
      navigate('/login', { replace: true, state: { registered: true } });
    } catch (caughtError) {
      const apiError = normalizeApiError(caughtError);
      if (apiError.status === 403) setError('Este tipo de conta não pode ser criado pelo cadastro público.');
      else if (apiError.status === 422) setError('Revise os dados informados. Use um e-mail institucional da UFCA.');
      else setError(apiError.message);
    }
  }

  return (
    <form className="space-y-4" onSubmit={handleSubmit} noValidate>
      <Input label="Nome completo" autoComplete="name" value={form.name} onChange={(event) => updateField('name', event.target.value)} required />
      <Input label="E-mail institucional" type="email" autoComplete="email" value={form.email} onChange={(event) => updateField('email', event.target.value)} required />
      <Input label="WhatsApp com DDI e DDD" type="tel" autoComplete="tel" value={form.whatsapp} onChange={(event) => updateField('whatsapp', event.target.value)} required />
      <label className="block text-sm font-medium text-slate-700">Tipo de conta
        <select className="mt-1.5 h-10 w-full rounded-xl border border-slate-300 bg-white px-3 text-sm focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500" value={form.role} onChange={(event) => updateField('role', event.target.value)}>
          <option value="customer">Cliente</option><option value="courier">Entregador</option>
        </select>
      </label>
      <Input label="Senha" type="password" autoComplete="new-password" value={form.password} onChange={(event) => updateField('password', event.target.value)} required />
      <Input label="Confirmação de senha" type="password" autoComplete="new-password" value={form.passwordConfirmation} onChange={(event) => updateField('passwordConfirmation', event.target.value)} required />
      {error ? <p className="rounded-xl bg-red-50 p-3 text-sm text-red-700" role="alert">{error}</p> : null}
      <Button className="w-full" type="submit" size="lg" isLoading={isLoading} loadingText="Criando conta...">Criar conta</Button>
      <p className="text-center text-sm text-slate-600">Já possui conta?{' '}<Link className="font-semibold text-orange-600 hover:text-orange-500" to="/login">Entrar</Link></p>
    </form>
  );
}
