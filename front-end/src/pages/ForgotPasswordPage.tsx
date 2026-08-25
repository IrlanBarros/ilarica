import { useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';

import { friendlyApiMessage } from '../api/http-error';
import { Button, Input } from '../components/ui';
import { requestPasswordReset } from '../services/auth.service';

export function ForgotPasswordPage(): React.JSX.Element {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ kind: 'success' | 'error'; text: string } | null>(null);
  async function submit(event: FormEvent): Promise<void> {
    event.preventDefault();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return setMessage({ kind: 'error', text: 'Informe um e-mail válido.' });
    setLoading(true); setMessage(null);
    try { await requestPasswordReset(email.trim().toLowerCase()); setMessage({ kind: 'success', text: 'Se a conta existir, enviaremos um link válido por 30 minutos.' }); }
    catch (error) { setMessage({ kind: 'error', text: friendlyApiMessage(error, 'Não foi possível solicitar a recuperação agora.') }); }
    finally { setLoading(false); }
  }
  return <div className="w-full"><h1 className="font-display text-2xl font-extrabold text-ilarica-ink">Recuperar senha</h1><p className="mt-2 text-sm text-ilarica-muted">Informe seu e-mail para receber um link seguro.</p><form className="mt-6 space-y-5" onSubmit={submit}><Input label="E-mail" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />{message && <p role={message.kind === 'error' ? 'alert' : 'status'} className={`rounded-xl px-4 py-3 text-sm font-semibold ${message.kind === 'error' ? 'bg-red-50 text-red-700' : 'bg-emerald-50 text-emerald-800'}`}>{message.text}</p>}<Button type="submit" isLoading={loading} loadingText="Enviando..." className="h-12 w-full bg-ilarica-orange hover:bg-[#ed5925]">Enviar link</Button></form><Link to="/login" className="mt-6 block text-center text-sm font-bold text-ilarica-orange">Voltar ao login</Link></div>;
}
