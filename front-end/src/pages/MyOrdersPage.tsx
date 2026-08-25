import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';

import { AppHeader } from '../components/AppHeader';
import { Button, Card } from '../components/ui';
import { formatDeliveryDestination } from '../lib/order-destination';
import { useControlledPolling } from '../lib/useControlledPolling';
import { listMyOrders } from '../services';
import type { CustomerOrder } from '../types';

const money = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const statusLabels: Record<string, string> = {
  draft: 'Pedido criado', 'Awaiting Payment': 'Aguardando pagamento', paid: 'Pagamento confirmado',
  preparing: 'Em preparo', ready_for_pickup: 'Pronto para retirada', in_transit: 'Em entrega', completed: 'Concluído',
};

export function MyOrdersPage(): React.JSX.Element {
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const requestInFlight = useRef(false);

  async function load(showLoading = true): Promise<void> {
    if (requestInFlight.current) return;
    requestInFlight.current = true;
    if (showLoading) setLoading(true);
    setError(null);
    try { setOrders(await listMyOrders()); }
    catch { setError('Não foi possível carregar seus pedidos.'); }
    finally { setLoading(false); requestInFlight.current = false; }
  }
  useEffect(() => { void load(); }, []);
  useControlledPolling(() => load(false), 20_000);

  return <main className="min-h-screen bg-[#fff1d6]"><AppHeader /><div className="mx-auto max-w-5xl px-5 py-8 sm:px-8 lg:px-16">
      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-end"><div><h1 className="font-display text-3xl font-extrabold text-[#7a1e1e] sm:text-4xl">Meus Pedidos</h1><p className="mt-1 text-ilarica-muted">Acompanhe o preparo e saiba quando retirar.</p></div><Button variant="secondary" isLoading={loading} loadingText="Atualizando..." onClick={() => { void load(); }}>Atualizar</Button></div>
      {loading && <Card className="mt-7 p-10 text-center">Carregando pedidos...</Card>}
      {error && <Card className="mt-7 border-[#efb7b7] p-6 text-[#a32020]" role="alert">{error}</Card>}
      {!loading && !error && orders.length === 0 && <Card className="mt-7 border-dashed p-10 text-center"><p className="font-display text-xl font-bold text-[#7a1e1e]">Você ainda não fez nenhum pedido</p><p className="mt-2 text-sm text-ilarica-muted">Escolha uma cantina e encontre algo gostoso para retirar.</p><Link to="/" className="mt-5 inline-flex rounded-full bg-ilarica-orange px-5 py-2.5 text-sm font-bold text-white">Ir para as cantinas</Link></Card>}
      <div className="mt-7 space-y-5">{orders.map((order) => <Card key={order.id} className="border-0 p-6 shadow-none sm:p-7">
        <div className="flex flex-wrap items-start justify-between gap-3"><div><p className="text-xs font-bold uppercase text-ilarica-orange">Pedido #{order.id.slice(0, 8)}</p><h2 className="mt-1 font-display text-xl font-extrabold text-[#7a1e1e]">{order.canteen.name}</h2><p className="text-sm text-ilarica-muted">{order.canteen.location}</p></div><span className="rounded-full bg-[#fff0e8] px-3 py-2 text-xs font-bold text-ilarica-orange">{statusLabels[order.status] ?? order.status}</span></div>
        <ul className="mt-5 space-y-1 text-sm text-ilarica-muted">{order.items.map((item) => <li key={item.id}>{item.quantity}x {item.name}</li>)}</ul>
        <div className="mt-5 border-t border-ilarica-line pt-4 text-sm"><p><strong>Modalidade:</strong> {order.fulfillment_type === 'pickup' ? 'Retirada presencial' : 'Entrega'}</p><p className="mt-1"><strong>Destino:</strong> {order.fulfillment_type === 'pickup' ? order.canteen.location : formatDeliveryDestination(order.destination, order.location_details)}</p></div>
        {order.fulfillment_type === 'pickup' && order.pickup_pin && <div className="mt-5 rounded-2xl bg-[#eff9f1] p-4 text-center text-[#237b39]"><span className="block text-xs font-bold uppercase">PIN de retirada</span><strong className="font-display text-3xl tracking-[0.3em]">{order.pickup_pin}</strong><span className="mt-1 block text-xs">Mostre este código no balcão.</span></div>}
        <div className="mt-5 flex flex-wrap items-center justify-between gap-3 border-t border-ilarica-line pt-4 font-bold"><Link to={`/pedidos/${order.id}`} className="inline-flex min-h-11 items-center text-sm text-ilarica-orange hover:underline">Ver detalhes</Link><span className="text-[#7a1e1e]">{money.format(Number(order.total_amount))}</span></div>
      </Card>)}</div>
    </div>
  </main>;
}
