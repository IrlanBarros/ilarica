import { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import { Button, Card, Input } from '../components/ui';
import { getMyCanteen, updateMyCanteen } from '../services';
import type { Canteen, CanteenBusinessHoursEntry } from '../types';

const dayLabels: Record<CanteenBusinessHoursEntry['day'], string> = { weekdays: 'Segunda a sexta', saturday: 'Sábado', sunday: 'Domingo' };
const defaultHours: CanteenBusinessHoursEntry[] = [
  { day: 'weekdays', opens_at: '08:00', closes_at: '18:00', is_open: true },
  { day: 'saturday', opens_at: '09:00', closes_at: '13:00', is_open: true },
  { day: 'sunday', opens_at: '09:00', closes_at: '13:00', is_open: false },
];

function SellerNav(): React.JSX.Element {
  const { pathname } = useLocation();
  const links = [['/vendedor/pedidos', 'Pedidos Recebidos'], ['/vendedor/cardapio', 'Meu Cardápio'], ['/vendedor/horarios', 'Horários'], ['/vendedor/configuracoes', 'Configurações']] as const;
  return <aside className="h-fit rounded-2xl bg-white p-5 lg:sticky lg:top-6 lg:w-[280px]"><h2 className="mb-2 font-display text-lg font-extrabold text-[#7a1e1e]">Gerenciamento</h2><nav className="flex gap-2 overflow-x-auto lg:flex-col">{links.map(([to, label]) => <Link key={to} to={to} aria-current={pathname === to ? 'page' : undefined} className={`shrink-0 rounded-lg px-3 py-3 text-sm lg:w-full ${pathname === to ? 'bg-[#fff0e8] font-bold text-ilarica-orange' : 'text-ilarica-muted hover:bg-[#fffaf2]'}`}>{label}</Link>)}</nav></aside>;
}

export function SellerSettingsPage({ mode }: { mode: 'hours' | 'settings' }): React.JSX.Element {
  const [canteen, setCanteen] = useState<Canteen | null>(null);
  const [hours, setHours] = useState(defaultHours);
  const [form, setForm] = useState({ name: '', location: '', is_open: false });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [notice, setNotice] = useState<{ kind: 'success' | 'error'; text: string } | null>(null);
  useEffect(() => { void getMyCanteen().then((data) => { setCanteen(data); setForm({ name: data.name, location: data.location, is_open: data.is_open }); setHours(data.opening_hours?.length ? data.opening_hours : defaultHours); }).catch(() => setNotice({ kind: 'error', text: 'Não foi possível carregar os dados da cantina.' })).finally(() => setLoading(false)); }, []);
  async function save(): Promise<void> {
    if (!canteen || saving) return;
    setSaving(true); setNotice(null);
    try { const updated = await updateMyCanteen(mode === 'hours' ? { opening_hours: hours } : form); setCanteen(updated); setNotice({ kind: 'success', text: mode === 'hours' ? 'Horários atualizados com sucesso.' : 'Configurações atualizadas com sucesso.' }); }
    catch { setNotice({ kind: 'error', text: 'Não foi possível salvar as alterações.' }); }
    finally { setSaving(false); }
  }
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><header className="border-b border-[#efe6d7] bg-white"><div className="mx-auto flex h-20 max-w-[1440px] items-center gap-3 px-5 sm:px-8 lg:px-16"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span><span className="font-display text-[27px] font-extrabold text-[#7a1e1e]">Ilarica</span><span className="ml-auto text-sm font-bold">{canteen?.name ?? 'Cantina'}</span></div></header><div className="mx-auto grid max-w-[1440px] gap-6 px-5 py-8 sm:px-8 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-10 lg:px-16 lg:py-10"><SellerNav /><section><h1 className="font-display text-4xl font-extrabold text-[#7a1e1e]">{mode === 'hours' ? 'Horários de funcionamento' : 'Configurações da cantina'}</h1><p className="mt-2 text-ilarica-muted">{mode === 'hours' ? 'Defina quando sua cantina pode receber novos pedidos.' : 'Mantenha as informações públicas e o status da operação atualizados.'}</p>
    {notice && <div role={notice.kind === 'error' ? 'alert' : 'status'} className={`mt-6 rounded-xl border px-4 py-3 text-sm ${notice.kind === 'error' ? 'border-[#efb5b5] bg-[#fff1f1] text-[#9d2323]' : 'border-[#bde3c5] bg-[#eff9f1] text-[#237b39]'}`}>{notice.text}</div>}
    {loading ? <Card className="mt-7 p-10 text-center shadow-none">Carregando configurações...</Card> : mode === 'hours' ? <Card className="mt-7 border-0 p-6 shadow-none sm:p-8"><div className="divide-y divide-ilarica-line">{hours.map((entry) => <div key={entry.day} className="grid gap-4 py-5 sm:grid-cols-[minmax(140px,1fr)_130px_20px_130px_auto] sm:items-center"><strong>{dayLabels[entry.day]}</strong><Input type="time" aria-label={`Abertura ${dayLabels[entry.day]}`} disabled={!entry.is_open || saving} value={entry.opens_at} onChange={(event) => setHours((items) => items.map((item) => item.day === entry.day ? { ...item, opens_at: event.target.value } : item))} /><span className="text-center text-sm text-ilarica-muted">até</span><Input type="time" aria-label={`Fechamento ${dayLabels[entry.day]}`} disabled={!entry.is_open || saving} value={entry.closes_at} onChange={(event) => setHours((items) => items.map((item) => item.day === entry.day ? { ...item, closes_at: event.target.value } : item))} /><button type="button" role="switch" aria-checked={entry.is_open} disabled={saving} onClick={() => setHours((items) => items.map((item) => item.day === entry.day ? { ...item, is_open: !item.is_open } : item))} className={`relative h-7 w-12 rounded-full ${entry.is_open ? 'bg-[#26a146]' : 'bg-[#929ca6]'}`}><span className={`absolute top-1 h-5 w-5 rounded-full bg-white transition ${entry.is_open ? 'left-6' : 'left-1'}`} /></button></div>)}</div><Button isLoading={saving} loadingText="Salvando..." className="mt-6 bg-ilarica-orange hover:bg-[#ed5925]" onClick={() => { void save(); }}>Salvar horários</Button></Card> : <Card className="mt-7 border-0 p-6 shadow-none sm:p-8"><div className="grid gap-5 sm:grid-cols-2"><Input label="Nome da cantina" minLength={2} disabled={saving} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /><Input label="Localização (bloco/andar)" minLength={2} disabled={saving} value={form.location} onChange={(event) => setForm({ ...form, location: event.target.value })} /></div><div className="mt-7 flex items-center justify-between rounded-2xl bg-[#fffaf2] p-5"><div><strong className="block text-[#7a1e1e]">Recebimento de pedidos</strong><span className="mt-1 block text-sm text-ilarica-muted">{form.is_open ? 'A cantina está aberta e visível para novos pedidos.' : 'A cantina está pausada para novos pedidos.'}</span></div><button type="button" role="switch" aria-label="Alterar status global da cantina" aria-checked={form.is_open} disabled={saving} onClick={() => setForm({ ...form, is_open: !form.is_open })} className={`relative h-8 w-14 rounded-full ${form.is_open ? 'bg-[#26a146]' : 'bg-[#929ca6]'}`}><span className={`absolute top-1 h-6 w-6 rounded-full bg-white transition ${form.is_open ? 'left-7' : 'left-1'}`} /></button></div><Button isLoading={saving} loadingText="Salvando..." disabled={form.name.trim().length < 2 || form.location.trim().length < 2} className="mt-6 bg-ilarica-orange hover:bg-[#ed5925]" onClick={() => { void save(); }}>Salvar configurações</Button></Card>}
  </section></div></main>;
}
