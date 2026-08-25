import { useEffect, useState } from 'react';

import { friendlyApiMessage } from '../api/http-error';
import { AppHeader } from '../components/AppHeader';
import { Button, Card } from '../components/ui';
import { listCanteensForModeration, moderateCanteen } from '../services';
import type { Canteen } from '../types';

export function AdminCanteenModerationPage(): React.JSX.Element {
  const [canteens, setCanteens] = useState<Canteen[]>([]);
  const [loading, setLoading] = useState(true);
  const [actingId, setActingId] = useState<string | null>(null);
  const [rejecting, setRejecting] = useState<Canteen | null>(null);
  const [reason, setReason] = useState('');
  const [error, setError] = useState<string | null>(null);

  async function load(): Promise<void> {
    setLoading(true); setError(null);
    try { setCanteens(await listCanteensForModeration('pending')); }
    catch (caught) { setError(friendlyApiMessage(caught, 'Não foi possível carregar as solicitações.')); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);

  async function decide(canteen: Canteen, status: 'approved' | 'rejected'): Promise<void> {
    if (actingId) return;
    setActingId(canteen.id); setError(null);
    try {
      await moderateCanteen(canteen.id, { status, rejection_reason: status === 'rejected' ? reason.trim() : null });
      setCanteens((items) => items.filter((item) => item.id !== canteen.id));
      setRejecting(null); setReason('');
    } catch (caught) { setError(friendlyApiMessage(caught, 'Não foi possível registrar a decisão.')); }
    finally { setActingId(null); }
  }

  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><AppHeader /><div className="mx-auto max-w-6xl px-5 py-10 sm:px-8"><p className="text-xs font-bold uppercase tracking-[0.18em] text-ilarica-orange">Administração</p><h1 className="mt-2 font-display text-4xl font-extrabold text-[#7a1e1e]">Moderação de cantinas</h1><p className="mt-2 text-ilarica-muted">Somente estabelecimentos aprovados ficam visíveis e podem receber pedidos.</p>{error && <p role="alert" className="mt-6 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-700">{error}</p>}{loading ? <Card className="mt-7 p-10 text-center">Carregando solicitações...</Card> : canteens.length === 0 ? <Card className="mt-7 p-10 text-center"><h2 className="font-display text-xl font-bold text-[#7a1e1e]">Nenhuma solicitação pendente</h2><p className="mt-2 text-sm text-ilarica-muted">Novos cadastros aparecerão aqui para análise.</p><Button className="mt-5 bg-ilarica-orange" onClick={() => { void load(); }}>Atualizar lista</Button></Card> : <div className="mt-7 grid gap-5">{canteens.map((canteen) => <Card key={canteen.id} className="border-0 p-6 shadow-none"><div className="flex flex-col gap-5 sm:flex-row sm:items-center"><img src={canteen.logo_url ?? ''} alt={`Logo de ${canteen.name}`} className="size-24 rounded-2xl bg-[#fffaf2] object-cover" /><div className="min-w-0 flex-1"><h2 className="font-display text-xl font-extrabold text-[#7a1e1e]">{canteen.name}</h2><p className="mt-1 text-sm font-semibold text-ilarica-muted">{canteen.location}</p><p className="mt-3 text-sm leading-relaxed">{canteen.description}</p><p className="mt-2 text-xs font-semibold text-emerald-700">Acordo aceito em {canteen.commercial_terms_accepted_at ? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' }).format(new Date(canteen.commercial_terms_accepted_at)) : 'não informado'}</p></div><div className="flex gap-3"><Button variant="secondary" disabled={Boolean(actingId)} onClick={() => setRejecting(canteen)}>Rejeitar</Button><Button isLoading={actingId === canteen.id && !rejecting} loadingText="Aprovando..." disabled={Boolean(actingId)} className="bg-emerald-600 hover:bg-emerald-700" onClick={() => { void decide(canteen, 'approved'); }}>Aprovar</Button></div></div></Card>)}</div>}
    {rejecting && <div className="fixed inset-0 z-50 grid place-items-center bg-black/45 px-4"><section role="dialog" aria-modal="true" aria-labelledby="reject-title" className="w-full max-w-lg rounded-2xl bg-white p-6"><h2 id="reject-title" className="font-display text-xl font-extrabold text-[#7a1e1e]">Solicitar ajustes</h2><p className="mt-2 text-sm text-ilarica-muted">Explique claramente o que {rejecting.name} precisa corrigir.</p><textarea aria-label="Motivo da rejeição" minLength={5} maxLength={500} value={reason} onChange={(event) => setReason(event.target.value)} rows={5} className="mt-4 w-full rounded-xl border border-[#e0d3c0] p-3 outline-none focus:border-ilarica-orange focus:ring-2 focus:ring-ilarica-orange/20" /><div className="mt-5 flex justify-end gap-3"><Button variant="secondary" disabled={Boolean(actingId)} onClick={() => { setRejecting(null); setReason(''); }}>Cancelar</Button><Button isLoading={actingId === rejecting.id} loadingText="Rejeitando..." disabled={reason.trim().length < 5} className="bg-red-600 hover:bg-red-700" onClick={() => { void decide(rejecting, 'rejected'); }}>Confirmar rejeição</Button></div></section></div>}
  </div></main>;
}
