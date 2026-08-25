import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { normalizeApiError } from '../api/http-error';
import chevronLeft from '../assets/figma/chevron-left.svg';
import { Button, Input } from '../components/ui';
import { formatBrazilianPhone, isValidBrazilianMobile, toBrazilianWhatsappPayload } from '../lib/phone';
import { useAuthStore } from '../store';
import type { UserCreate } from '../types';

type PublicRole = NonNullable<UserCreate['role']>;

export function RegisterPage(): React.JSX.Element {
  const navigate = useNavigate();
  const register = useAuthStore((state) => state.register);
  const isLoading = useAuthStore((state) => state.isLoading);
  const [form, setForm] = useState({ name: '', email: '', whatsapp: '', password: '', passwordConfirmation: '', role: 'customer' as PublicRole });
  const [error, setError] = useState<string | null>(null);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<Partial<Record<keyof typeof form, string>>>({});

  function updateField(field: keyof typeof form, value: string): void {
    setForm((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: undefined }));
  }

  function validate(): boolean {
    const errors: Partial<Record<keyof typeof form, string>> = {};
    const normalizedEmail = form.email.trim().toLowerCase();
    if (form.name.trim().length < 2) errors.name = 'Informe seu nome completo.';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(normalizedEmail)) errors.email = 'Informe um e-mail válido.';
    else if (!normalizedEmail.endsWith('@aluno.ufca.edu.br') && !normalizedEmail.endsWith('@ufca.edu.br')) errors.email = 'Use seu e-mail institucional da UFCA.';
    if (!isValidBrazilianMobile(form.whatsapp)) errors.whatsapp = 'Informe um celular válido com DDD.';
    if (form.password.length < 8 || form.password.length > 128) errors.password = 'A senha deve ter entre 8 e 128 caracteres.';
    else if (!/[A-Z]/.test(form.password) || !/\d/.test(form.password)) errors.password = 'Use pelo menos uma letra maiúscula e um número.';
    if (form.password !== form.passwordConfirmation) errors.passwordConfirmation = 'A confirmação deve ser igual à senha.';
    if (!acceptedTerms) setError('Você precisa aceitar os Termos de Uso e a Política de Privacidade.');
    setFieldErrors(errors);
    return Object.keys(errors).length === 0 && acceptedTerms;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    if (!validate()) return;
    try {
      await register({ name: form.name.trim(), email: form.email.trim().toLowerCase(), whatsapp: toBrazilianWhatsappPayload(form.whatsapp), password: form.password, role: form.role });
      navigate(`/verificar-email?email=${encodeURIComponent(form.email.trim().toLowerCase())}`, { replace: true });
    } catch (caughtError) {
      const apiError = normalizeApiError(caughtError);
      if (apiError.status === 403) setError('Este tipo de conta não pode ser criado pelo cadastro público.');
      else if (apiError.status === 422) setError('Revise os dados informados. Use um e-mail institucional da UFCA.');
      else setError('Não foi possível concluir o cadastro. Verifique sua conexão e tente novamente.');
    }
  }

  return (
    <div className="w-full">
      <header className="flex items-center gap-3">
        <Link aria-label="Voltar para o login" className="grid size-6 place-items-center" to="/login"><img alt="" className="size-6" src={chevronLeft} /></Link>
        <h1 className="font-display text-[22px] font-extrabold text-ilarica-ink">Criar Conta</h1>
      </header>

      <div className="mt-5 flex h-11 rounded-full bg-ilarica-line p-1" role="group" aria-label="Tipo de conta">
        <button className={`flex-1 rounded-full text-[13px] font-bold transition-colors ${form.role === 'customer' ? 'bg-white text-ilarica-orange' : 'text-ilarica-muted'}`} type="button" aria-pressed={form.role === 'customer'} onClick={() => updateField('role', 'customer')}>Quero ser Cliente</button>
        <button className={`flex-1 rounded-full text-[13px] font-semibold transition-colors ${form.role === 'courier' ? 'bg-white text-ilarica-orange' : 'text-ilarica-muted'}`} type="button" aria-pressed={form.role === 'courier'} onClick={() => updateField('role', 'courier')}>Ser Entregador</button>
      </div>

      <form className="mt-5 space-y-4" onSubmit={handleSubmit} noValidate>
        <Input label="Nome Completo" error={fieldErrors.name} placeholder="Seu nome completo" autoComplete="name" value={form.name} onChange={(event) => updateField('name', event.target.value)} className="h-11 border-ilarica-line px-4 text-sm focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <Input label="E-mail Institucional (.edu.br)" error={fieldErrors.email} placeholder="seu@aluno.ufca.edu.br" type="email" autoComplete="email" value={form.email} onChange={(event) => updateField('email', event.target.value)} className="h-11 border-ilarica-line px-4 text-sm focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <Input label="WhatsApp" error={fieldErrors.whatsapp} prefix="+55" placeholder="(88) 99999-9999" type="tel" inputMode="numeric" autoComplete="tel-national" value={form.whatsapp} onChange={(event) => updateField('whatsapp', formatBrazilianPhone(event.target.value))} className="h-11 border-ilarica-line pr-4 text-sm focus:border-ilarica-orange focus:ring-ilarica-orange" maxLength={15} required />
        <Input label="Senha" error={fieldErrors.password} placeholder="••••••••" type="password" autoComplete="new-password" value={form.password} onChange={(event) => updateField('password', event.target.value)} className="h-11 border-ilarica-line px-4 text-sm focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <Input label="Confirmar Senha" error={fieldErrors.passwordConfirmation} placeholder="••••••••" type="password" autoComplete="new-password" value={form.passwordConfirmation} onChange={(event) => updateField('passwordConfirmation', event.target.value)} className="h-11 border-ilarica-line px-4 text-sm focus:border-ilarica-orange focus:ring-ilarica-orange" required />
        <label className="flex items-start gap-3 text-sm text-ilarica-muted"><input type="checkbox" checked={acceptedTerms} onChange={(event) => { setAcceptedTerms(event.target.checked); setError(null); }} className="mt-1 size-4 accent-[#ff6534]" /><span>Li e aceito os <Link to="/termos" className="font-bold text-ilarica-orange underline">Termos de Uso</Link> e a <Link to="/privacidade" className="font-bold text-ilarica-orange underline">Política de Privacidade</Link>.</span></label>
        {error ? <p className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700" role="alert">{error}</p> : null}
        <Button className="h-12 w-full rounded-full bg-ilarica-orange text-[15px] hover:bg-[#ed5b2a] focus-visible:ring-ilarica-orange" type="submit" isLoading={isLoading} loadingText="Cadastrando...">Cadastrar</Button>
      </form>
    </div>
  );
}
