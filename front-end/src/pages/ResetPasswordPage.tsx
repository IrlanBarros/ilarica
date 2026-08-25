import { useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { friendlyApiMessage } from '../api/http-error';
import { Button, Input } from '../components/ui';
import { confirmPasswordReset } from '../services/auth.service';

export function ResetPasswordPage(): React.JSX.Element {
  const [params] = useSearchParams(); const token = params.get('token') ?? '';
  const [password, setPassword] = useState(''); const [confirmation, setConfirmation] = useState('');
  const [loading, setLoading] = useState(false); const [done, setDone] = useState(false); const [error, setError] = useState<string | null>(null);
  async function submit(event: FormEvent): Promise<void> { event.preventDefault(); setError(null); if (!token) return setError('O link de recuperação é inválido.'); if (password.length < 8 || !/[A-Z]/.test(password) || !/\d/.test(password)) return setError('Use ao menos 8 caracteres, uma letra maiúscula e um número.'); if (password !== confirmation) return setError('As senhas não coincidem.'); setLoading(true); try { await confirmPasswordReset(token, password); setDone(true); } catch (caught) { setError(friendlyApiMessage(caught, 'O link é inválido ou expirou. Solicite outro.')); } finally { setLoading(false); } }
  if (done) return <div className="text-center"><h1 className="font-display text-2xl font-extrabold text-[#7a1e1e]">Senha atualizada</h1><p className="mt-3 text-sm text-ilarica-muted">Sua nova senha já pode ser utilizada.</p><Link to="/login" className="mt-6 inline-flex rounded-full bg-ilarica-orange px-6 py-3 font-bold text-white">Entrar</Link></div>;
  return <div><h1 className="font-display text-2xl font-extrabold text-ilarica-ink">Criar nova senha</h1><form onSubmit={submit} className="mt-6 space-y-4"><Input label="Nova senha" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} required /><Input label="Confirmar nova senha" type="password" autoComplete="new-password" value={confirmation} onChange={(event) => setConfirmation(event.target.value)} required />{error && <p role="alert" className="rounded-xl bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</p>}<Button type="submit" isLoading={loading} loadingText="Atualizando..." className="h-12 w-full bg-ilarica-orange">Atualizar senha</Button></form></div>;
}
