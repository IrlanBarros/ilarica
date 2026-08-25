import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import { Link } from 'react-router-dom';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import searchIcon from '../assets/figma/cart/search.svg';
import vendorImage from '../assets/figma/canteen/vendor-hero.png';
import { Button, Card } from '../components/ui';
import { useSellerStore } from '../store';
import type { SellerOrder, SellerOrderStage } from '../types';

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
const tabs: Array<{ id: SellerOrderStage; label: string }> = [
  { id: 'new', label: 'Novos' },
  { id: 'preparing', label: 'Em preparo' },
  { id: 'ready', label: 'Prontos' },
];

function Header(): React.JSX.Element {
  return <header className="border-b border-[#efe6d7] bg-white"><div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-5 px-5 sm:px-8 lg:px-16">
    <div className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span><span className="font-display text-[27px] font-extrabold text-[#7a1e1e]">Ilarica</span><span className="hidden rounded-full bg-[#fff0e8] px-2.5 py-1 text-[10px] font-bold uppercase text-ilarica-orange sm:inline">Campus Centro</span></div>
    <div className="hidden h-11 max-w-[480px] flex-1 items-center gap-3 rounded-full border border-[#f0dfc2] bg-[#fff1d6] px-4 text-sm text-ilarica-muted md:flex"><img src={searchIcon} alt="" className="h-[18px] w-[18px]" />Buscar pedidos ou clientes...</div>
    <div className="flex items-center gap-2"><img src={vendorImage} alt="" className="h-9 w-9 rounded-full object-cover" /><span className="hidden text-sm font-bold sm:inline">Cantina</span><img src={chevronDownIcon} alt="" className="h-3.5 w-3.5" /></div>
  </div></header>;
}

function Sidebar(): React.JSX.Element {
  return <aside className="h-fit rounded-2xl bg-white p-4 lg:sticky lg:top-6 lg:w-[280px] lg:p-5"><h2 className="mb-2 font-display text-lg font-extrabold text-[#7a1e1e]">Gerenciamento</h2><nav className="flex gap-2 overflow-x-auto lg:flex-col" aria-label="Gerenciamento da cantina">
    <Link to="/vendedor/cardapio" className="shrink-0 rounded-lg px-3 py-3 text-sm text-ilarica-muted hover:bg-[#fffaf2] lg:w-full">Meu Cardápio</Link>
    <Link to="/vendedor/pedidos" aria-current="page" className="shrink-0 rounded-lg bg-[#fff0e8] px-3 py-3 text-sm font-bold text-ilarica-orange lg:w-full">Pedidos Recebidos</Link>
    <span className="shrink-0 rounded-lg px-3 py-3 text-sm text-ilarica-muted lg:w-full">Horários</span><span className="shrink-0 rounded-lg px-3 py-3 text-sm text-ilarica-muted lg:w-full">Configurações</span>
  </nav></aside>;
}

function OrderCard({ order }: { order: SellerOrder }): React.JSX.Element {
  const advanceOrder = useSellerStore((state) => state.advanceOrder);
  const itemCount = order.items.reduce((sum, item) => sum + item.quantity, 0);
  const action = order.stage === 'new' ? 'Aceitar pedido' : order.stage === 'preparing' ? 'Marcar como pronto' : 'Aguardando retirada';
  return <Card className="border-[#eadfce] p-5 shadow-none sm:p-6"><div className="flex flex-wrap items-start justify-between gap-3"><div><div className="flex items-center gap-3"><h2 className="font-display text-lg font-extrabold text-[#7a1e1e]">Pedido {order.displayCode}</h2><span className="rounded-full bg-[#fff0e8] px-2.5 py-1 text-xs font-bold text-ilarica-orange">{itemCount} {itemCount === 1 ? 'item' : 'itens'}</span></div><p className="mt-1 text-sm text-ilarica-muted">Recebido às {order.createdAt} · <strong className="text-ilarica-ink">{order.customerName}</strong></p></div><strong className="font-display text-lg text-[#7a1e1e]">{currency.format(Number(order.totalAmount))}</strong></div>
    <div className="mt-5 grid gap-5 border-t border-[#eee5d9] pt-5 md:grid-cols-[minmax(0,1fr)_minmax(220px,0.8fr)_auto] md:items-end"><div><p className="mb-2 text-xs font-bold uppercase tracking-wide text-ilarica-muted">Itens do pedido</p><ul className="space-y-1.5 text-sm">{order.items.map((item) => <li key={item.productId}><strong className="text-ilarica-orange">{item.quantity}x</strong> {item.name}</li>)}</ul></div><div><p className="text-xs font-bold uppercase tracking-wide text-ilarica-muted">{order.fulfillment === 'pickup' ? 'Modalidade' : 'Local de entrega'}</p><p className="mt-2 text-sm font-semibold">{order.destination}</p>{order.notes && <p className="mt-1 text-xs text-ilarica-muted">Obs.: {order.notes}</p>}</div><Button disabled={order.stage === 'ready'} onClick={() => advanceOrder(order.id)} className="h-11 rounded-full bg-ilarica-orange px-6 hover:bg-[#ed5925] disabled:bg-[#d7d1c7]">{action}</Button></div>
  </Card>;
}

export function SellerOrdersPage(): React.JSX.Element {
  const orders = useSellerStore((state) => state.orders);
  const activeStage = useSellerStore((state) => state.orderStage);
  const setOrderStage = useSellerStore((state) => state.setOrderStage);
  const filtered = orders.filter((order) => order.stage === activeStage);
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><Header /><div className="mx-auto grid w-full max-w-[1440px] gap-6 px-5 py-7 sm:px-8 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-10 lg:px-16 lg:py-10"><Sidebar /><section><div><h1 className="font-display text-3xl font-extrabold text-[#7a1e1e] sm:text-4xl">Pedidos Recebidos</h1><p className="mt-1 text-base text-ilarica-muted">Acompanhe os pedidos e mantenha o cliente informado em cada etapa.</p></div>
    <div className="mt-7 flex gap-2 overflow-x-auto rounded-2xl bg-white p-1.5" role="tablist" aria-label="Status dos pedidos">{tabs.map((tab) => { const count = orders.filter((order) => order.stage === tab.id).length; return <button key={tab.id} type="button" role="tab" aria-selected={activeStage === tab.id} onClick={() => setOrderStage(tab.id)} className={`flex min-w-[130px] flex-1 items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-bold transition ${activeStage === tab.id ? 'bg-[#7a1e1e] text-white' : 'text-ilarica-muted hover:bg-[#fffaf2]'}`}>{tab.label}<span className={`rounded-full px-2 py-0.5 text-xs ${activeStage === tab.id ? 'bg-white/20 text-white' : 'bg-[#fff0e8] text-ilarica-orange'}`}>{count}</span></button>; })}</div>
    <div className="mt-5 space-y-4">{filtered.map((order) => <OrderCard key={order.id} order={order} />)}{filtered.length === 0 && <Card className="border-dashed p-10 text-center shadow-none"><p className="font-display text-lg font-bold text-[#7a1e1e]">Nenhum pedido nesta etapa</p><p className="mt-1 text-sm text-ilarica-muted">Os próximos pedidos aparecerão aqui automaticamente.</p></Card>}</div>
  </section></div></main>;
}
