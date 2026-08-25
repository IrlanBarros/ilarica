import { useEffect, useState } from 'react';

import { AppHeader } from '../components/AppHeader';
import { Button, Card } from '../components/ui';
import { listPaymentTransactions } from '../services/payment-transaction.service';
import { getMyWallet } from '../services/wallet.service';
import type { PaymentTransaction, Wallet } from '../types';

const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const date = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short', timeStyle: 'short' });

export function WalletPage(): React.JSX.Element {
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [transactions, setTransactions] = useState<PaymentTransaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  async function load(): Promise<void> { setLoading(true); setError(null); try { const [currentWallet, entries] = await Promise.all([getMyWallet(), listPaymentTransactions()]); setWallet(currentWallet); setTransactions(entries); } catch { setError('Não foi possível carregar sua carteira.'); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><AppHeader /><div className="mx-auto max-w-5xl px-5 py-10 sm:px-8 sm:py-14">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="text-sm font-bold uppercase tracking-[0.18em] text-ilarica-orange">Finanças</p><h1 className="mt-1 font-display text-4xl font-extrabold text-[#7a1e1e]">Minha carteira</h1><p className="mt-2 text-ilarica-muted">Acompanhe seu saldo e os pagamentos feitos no iLarica.</p></div><Button variant="secondary" isLoading={loading} loadingText="Atualizando..." onClick={() => { void load(); }}>Atualizar</Button></div>
    {error && <div role="alert" className="mt-7 rounded-xl border border-[#efb5b5] bg-[#fff1f1] px-4 py-3 text-[#9d2323]">{error}</div>}
    <Card className="mt-8 border-0 bg-[#7a1e1e] p-7 text-white shadow-none sm:p-9"><p className="text-xs font-bold uppercase tracking-[0.16em] text-[#ffb18f]">Saldo atual</p><strong className="mt-2 block font-display text-4xl sm:text-5xl">{loading ? '—' : money.format(Number(wallet?.balance ?? 0))}</strong><p className="mt-3 text-sm text-white/70">Saldo disponível para pagamentos com carteira digital.</p></Card>
    <Card className="mt-7 border-0 p-6 shadow-none sm:p-8"><h2 className="font-display text-2xl font-extrabold text-[#7a1e1e]">Extrato</h2>{!loading && transactions.length === 0 && <p className="mt-6 rounded-xl border border-dashed border-ilarica-line p-8 text-center text-sm text-ilarica-muted">Nenhuma movimentação registrada.</p>}<div className="mt-4 divide-y divide-ilarica-line">{transactions.map((entry) => <div key={entry.id} className="flex items-center gap-4 py-4"><span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-[#ffe7e7] font-bold text-[#d82d2d]" aria-hidden="true">↑</span><div className="min-w-0 flex-1"><p className="font-semibold">Pagamento do pedido #{entry.order_id.slice(0, 8).toUpperCase()}</p><p className="mt-0.5 text-xs text-ilarica-muted">{date.format(new Date(entry.confirmed_at ?? entry.created_at))} · {entry.status === 'succeeded' ? 'Confirmado' : 'Em processamento'}</p></div><strong className="text-[#d82d2d]">− {money.format(Number(entry.amount))}</strong></div>)}</div><p className="mt-5 text-xs text-ilarica-muted">Recargas simuladas aparecerão aqui quando o backend disponibilizar o contrato de extrato de entradas.</p></Card>
  </div></main>;
}
