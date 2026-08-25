import { useEffect, useState, type FormEvent } from 'react';

import { friendlyApiMessage } from '../api/http-error';
import { AppHeader } from '../components/AppHeader';
import { Button, Card, Input } from '../components/ui';
import { getMyCanteen, submitMyCanteenOnboarding } from '../services';
import type { Canteen } from '../types';

const statusLabels = {
  pending: 'Aguardando análise',
  approved: 'Cadastro aprovado',
  rejected: 'Ajustes solicitados',
} as const;

export function SellerOnboardingPage(): React.JSX.Element {
  const [canteen, setCanteen] = useState<Canteen | null>(null);
  const [description, setDescription] = useState('');
  const [logoUrl, setLogoUrl] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    void getMyCanteen()
      .then((data) => {
        setCanteen(data);
        setDescription(data.description ?? '');
        setLogoUrl(data.logo_url ?? '');
        setAcceptedTerms(Boolean(data.commercial_terms_accepted_at));
      })
      .catch((error: unknown) => setNotice({ kind: 'error', text: friendlyApiMessage(error, 'Não foi possível carregar o cadastro comercial.') }))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    if (saving || !acceptedTerms) return;
    setSaving(true);
    setNotice(null);
    try {
      const updated = await submitMyCanteenOnboarding({
        description: description.trim(),
        logo_url: logoUrl.trim(),
        accepted_commercial_terms: true,
      });
      setCanteen(updated);
      setNotice({ kind: 'success', text: updated.moderation_status === 'approved' ? 'Perfil comercial atualizado.' : 'Cadastro enviado para análise administrativa.' });
    } catch (error) {
      setNotice({ kind: 'error', text: friendlyApiMessage(error, 'Não foi possível enviar o cadastro comercial.') });
    } finally {
      setSaving(false);
    }
  }

  const moderationStatus = canteen?.moderation_status ?? 'pending';
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><AppHeader /><div className="mx-auto max-w-4xl px-5 py-10 sm:px-8"><div className="flex flex-wrap items-start justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.18em] text-ilarica-orange">Onboarding comercial</p><h1 className="mt-2 font-display text-4xl font-extrabold text-[#7a1e1e]">Perfil da cantina</h1><p className="mt-2 text-ilarica-muted">Apresente seu estabelecimento e aceite o acordo para solicitar aprovação.</p></div>{canteen && <span className={`rounded-full px-4 py-2 text-sm font-bold ${moderationStatus === 'approved' ? 'bg-emerald-100 text-emerald-800' : moderationStatus === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-amber-100 text-amber-800'}`}>{statusLabels[moderationStatus]}</span>}</div>
    {notice && <p role={notice.kind === 'error' ? 'alert' : 'status'} className={`mt-6 rounded-xl border px-4 py-3 text-sm font-semibold ${notice.kind === 'error' ? 'border-red-200 bg-red-50 text-red-700' : 'border-emerald-200 bg-emerald-50 text-emerald-800'}`}>{notice.text}</p>}
    {canteen?.rejection_reason && <div role="alert" className="mt-6 rounded-2xl border border-red-200 bg-red-50 p-5"><strong className="text-red-800">Ajustes solicitados pelo administrador</strong><p className="mt-2 text-sm text-red-700">{canteen.rejection_reason}</p></div>}
    {loading ? <Card className="mt-7 p-10 text-center">Carregando cadastro...</Card> : <Card className="mt-7 border-0 p-6 shadow-none sm:p-8"><form onSubmit={(event) => { void submit(event); }} className="space-y-5"><Input label="URL da logo" type="url" required disabled={saving} placeholder="https://..." value={logoUrl} onChange={(event) => setLogoUrl(event.target.value)} /><label className="grid gap-2 text-sm font-semibold text-ilarica-muted">Descrição do estabelecimento<textarea aria-label="Descrição do estabelecimento" required minLength={20} maxLength={1000} disabled={saving} value={description} onChange={(event) => setDescription(event.target.value)} rows={6} className="rounded-xl border border-[#e0d3c0] bg-white p-4 text-ilarica-ink outline-none focus:border-ilarica-orange focus:ring-2 focus:ring-ilarica-orange/20" placeholder="Conte aos clientes o que sua cantina oferece..." /></label>{logoUrl && <div className="flex items-center gap-4 rounded-2xl bg-[#fffaf2] p-4"><img src={logoUrl} alt="Prévia da logo da cantina" className="size-20 rounded-2xl object-cover" /><span className="text-sm text-ilarica-muted">Prévia da identidade exibida aos clientes.</span></div>}<label className="flex items-start gap-3 rounded-2xl border border-[#eadfce] p-4 text-sm text-ilarica-muted"><input type="checkbox" checked={acceptedTerms} disabled={saving || Boolean(canteen?.commercial_terms_accepted_at)} onChange={(event) => setAcceptedTerms(event.target.checked)} className="mt-1 size-4 accent-[#ff6534]" /><span>Li e aceito o Acordo de Parceria Comercial do iLarica. O sistema registrará a data e a hora deste aceite.</span></label>{canteen?.commercial_terms_accepted_at && <p className="text-xs font-semibold text-emerald-700">Aceite registrado em {new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(canteen.commercial_terms_accepted_at))}.</p>}<Button type="submit" isLoading={saving} loadingText="Enviando..." disabled={!acceptedTerms || description.trim().length < 20 || !/^https?:\/\//.test(logoUrl)} className="min-h-12 w-full rounded-full bg-ilarica-orange">{moderationStatus === 'rejected' ? 'Reenviar para análise' : 'Salvar e enviar para análise'}</Button></form></Card>}
  </div></main>;
}
