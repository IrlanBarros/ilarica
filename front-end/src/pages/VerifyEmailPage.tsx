import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';

import { friendlyApiMessage, normalizeApiError } from '../api/http-error';
import { Button } from '../components/ui';
import { confirmEmailVerification, requestEmailVerification } from '../services/auth.service';

type VerificationState = 'pending' | 'verifying' | 'verified' | 'error';

export function VerifyEmailPage(): React.JSX.Element {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const email = searchParams.get('email');
  const [state, setState] = useState<VerificationState>(token ? 'verifying' : 'pending');
  const [message, setMessage] = useState(
    token ? 'Validando seu link seguro...' : 'Enviamos um link de uso único para seu e-mail institucional.',
  );
  const [resending, setResending] = useState(false);

  useEffect(() => {
    if (!token) return;
    let active = true;
    void confirmEmailVerification(token)
      .then(() => {
        if (!active) return;
        setState('verified');
        setMessage('E-mail confirmado com sucesso. Sua conta está pronta para entrar.');
      })
      .catch((error: unknown) => {
        if (!active) return;
        setState('error');
        const apiError = normalizeApiError(error);
        setMessage(
          apiError.status === null || apiError.status === 400
            ? 'Este link é inválido, expirou ou já foi utilizado.'
            : friendlyApiMessage(error, 'Não foi possível validar seu e-mail agora.'),
        );
      });
    return () => { active = false; };
  }, [token]);

  async function resend(): Promise<void> {
    if (!email) return;
    setResending(true);
    try {
      await requestEmailVerification(email);
      setState('pending');
      setMessage('Um novo link foi enviado. Ele expira em 15 minutos.');
    } catch (error) {
      setState('error');
      setMessage(friendlyApiMessage(error, 'Não foi possível reenviar agora. Tente novamente em instantes.'));
    } finally {
      setResending(false);
    }
  }

  return (
    <section className="text-center" aria-live="polite">
      <div className={`mx-auto grid size-16 place-items-center rounded-full text-3xl ${state === 'verified' ? 'bg-emerald-100 text-emerald-700' : state === 'error' ? 'bg-red-100 text-red-700' : 'bg-[#fff0e8] text-ilarica-orange'}`}>
        {state === 'verified' ? '✓' : state === 'error' ? '!' : '✉'}
      </div>
      <h1 className="mt-5 font-display text-2xl font-extrabold text-ilarica-ink">
        {state === 'verified' ? 'E-mail confirmado' : 'Confirme seu e-mail'}
      </h1>
      <p className="mt-3 text-sm leading-relaxed text-ilarica-muted">{message}</p>
      {state === 'verifying' && <div className="mx-auto mt-6 size-8 animate-spin rounded-full border-4 border-[#ffd5c5] border-t-ilarica-orange" aria-label="Validando e-mail" />}
      {state === 'verified' ? (
        <Link to="/login" className="mt-7 inline-flex min-h-12 w-full items-center justify-center rounded-full bg-ilarica-orange px-6 font-bold text-white">Ir para o login</Link>
      ) : (
        <div className="mt-7 space-y-3">
          {email && <Button type="button" isLoading={resending} loadingText="Reenviando..." onClick={() => { void resend(); }} className="min-h-12 w-full rounded-full bg-ilarica-orange">Reenviar link</Button>}
          <Link to="/login" className="inline-flex min-h-11 items-center font-bold text-ilarica-orange underline">Voltar ao login</Link>
        </div>
      )}
    </section>
  );
}
