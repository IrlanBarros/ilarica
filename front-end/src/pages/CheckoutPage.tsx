import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import profileImage from '../assets/figma/cart/profile.png';
import searchIcon from '../assets/figma/cart/search.svg';
import shoppingCartIcon from '../assets/figma/cart/shopping-cart.svg';
import { ApiClientError } from '../api/http-error';
import { buildOrderPayload } from '../lib/build-order-payload';
import { createOrder, createPaymentTransaction, getMyWallet, listDropOffZones } from '../services';
import { useAuthStore, useCartStore, usePaymentStore } from '../store';
import type { DropOffZone, PaymentMethod, Wallet } from '../types';

const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

type FulfillmentMethod = 'pickup' | 'delivery';

function checkoutErrorMessage(error: unknown): string {
  if (!(error instanceof ApiClientError)) {
    return 'Não foi possível confirmar o pedido. Tente novamente.';
  }
  if (error.status === 401) return 'Sua sessão expirou. Entre novamente para confirmar o pedido.';
  if (error.status === 403) return 'Sua conta não tem permissão para criar este pedido.';
  if (error.status === 404) return 'Um produto, cantina ou ponto selecionado não está mais disponível.';
  if (error.status === 402) return error.message || 'Pagamento recusado ou saldo insuficiente.';
  if (error.status === 409) return error.message || 'O pedido já foi pago ou existe outro pagamento em andamento.';
  if (error.status === 400 || error.status === 422) return 'Os dados do pedido são inválidos. Revise o carrinho e o ponto selecionado.';
  return 'O serviço está indisponível no momento. Tente novamente em instantes.';
}

export function CheckoutPage(): React.JSX.Element {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const items = useCartStore((state) => state.items);
  const canteenId = useCartStore((state) => state.canteenId);
  const subtotal = useCartStore((state) => state.total);
  const clearCart = useCartStore((state) => state.clearCart);
  const pendingPayment = usePaymentStore((state) => state.pending);
  const startPayment = usePaymentStore((state) => state.start);
  const setPaymentTransaction = usePaymentStore((state) => state.setTransaction);
  const clearPayment = usePaymentStore((state) => state.clear);
  const [zones, setZones] = useState<DropOffZone[]>([]);
  const [selectedZoneId, setSelectedZoneId] = useState('');
  const [fulfillmentMethod, setFulfillmentMethod] = useState<FulfillmentMethod>('delivery');
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>(pendingPayment?.method || 'pix');
  const [wallet, setWallet] = useState<Wallet | null>(null);
  const [reference, setReference] = useState('');
  const [isLoadingZones, setIsLoadingZones] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const itemCount = items.reduce((total, item) => total + item.quantity, 0);
  const activeZones = useMemo(
    () => zones.filter((zone) => zone.is_active && zone.current_load < zone.capacity_total),
    [zones],
  );

  useEffect(() => {
    let isMounted = true;
    setIsLoadingZones(true);
    listDropOffZones()
      .then((response) => {
        if (!isMounted) return;
        const available = response.filter((zone) => zone.is_active && zone.current_load < zone.capacity_total);
        setZones(response);
        setSelectedZoneId((current) => current || available[0]?.id || '');
        setError(null);
      })
      .catch(() => {
        if (isMounted) setError('Não foi possível carregar os pontos disponíveis. Tente novamente.');
      })
      .finally(() => {
        if (isMounted) setIsLoadingZones(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  useEffect(() => {
    if (paymentMethod !== 'wallet') return;
    getMyWallet()
      .then(setWallet)
      .catch(() => setWallet(null));
  }, [paymentMethod]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);

    if (!user || !selectedZoneId) {
      setError('Selecione um ponto válido antes de confirmar o pedido.');
      return;
    }

    try {
      setIsSubmitting(true);
      let orderId = pendingPayment?.orderId;
      const idempotencyKey = pendingPayment?.idempotencyKey || crypto.randomUUID();

      if (!orderId) {
        const payload = buildOrderPayload({
          customerId: user.id,
          canteenId,
          dropOffZoneId: selectedZoneId,
          items,
        });
        const order = await createOrder(payload);
        orderId = order.id;
      }

      startPayment({ orderId, transactionId: pendingPayment?.transactionId || null, idempotencyKey, method: paymentMethod });
      const transaction = await createPaymentTransaction(
        { order_id: orderId, payment_method: paymentMethod },
        idempotencyKey,
      );
      setPaymentTransaction(transaction.id);

      if (transaction.status === 'succeeded') {
        clearCart();
        clearPayment();
        navigate(`/pedidos/${orderId}/pagamento-confirmado?transaction=${transaction.id}`, {
          replace: true,
          state: { amount: Number(transaction.amount), method: transaction.payment_method, paymentStatus: 'confirmed' },
        });
        return;
      }
      if (transaction.payment_method === 'pix' && transaction.status === 'pending') {
        navigate(`/pagamentos/${transaction.id}/pix`);
        return;
      }
      throw new ApiClientError(transaction.failure_reason || 'Pagamento recusado.', 402, transaction.failure_reason);
    } catch (submissionError) {
      if (submissionError instanceof ApiClientError && submissionError.status === 402) clearPayment();
      setError(checkoutErrorMessage(submissionError));
    } finally {
      setIsSubmitting(false);
    }
  }

  if (items.length === 0) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#fff1d6] px-5 text-center">
        <section className="w-full max-w-md rounded-3xl bg-white p-8">
          <h1 className="font-display text-2xl font-extrabold text-[#7a1e1e]">Não há pedido para confirmar</h1>
          <p className="mt-2 text-sm text-ilarica-muted">Adicione produtos ao carrinho antes de continuar.</p>
          <Link to="/" className="mt-6 inline-flex rounded-full bg-ilarica-orange px-6 py-3 text-sm font-bold text-white">Voltar ao Mural</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink">
      <header className="border-b border-ilarica-line bg-white">
        <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-6 px-5 sm:px-8 lg:px-16">
          <Link to="/" className="flex shrink-0 items-center gap-3" aria-label="Ir para o Mural">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span>
            <span className="font-display text-xl font-extrabold text-[#7a1e1e] sm:text-[28px]">Ilarica</span>
          </Link>
          <Link to="/" className="hidden h-11 max-w-[480px] flex-1 items-center gap-3 rounded-full border border-ilarica-line bg-[#fff1d6] px-4 text-[15px] text-ilarica-muted md:flex">
            <img src={searchIcon} alt="" className="h-[18px] w-[18px]" />Buscar lanches, doces ou vendedores...
          </Link>
          <div className="flex shrink-0 items-center gap-3 lg:gap-6">
            <Link to="/carrinho" className="flex items-center gap-2 rounded-full bg-[#fff0e8] px-3 py-2.5 sm:px-4">
              <img src={shoppingCartIcon} alt="" className="h-[18px] w-[18px]" /><span className="text-sm font-bold text-ilarica-orange">{itemCount} {itemCount === 1 ? 'item' : 'itens'}</span>
            </Link>
            <div className="hidden items-center gap-2.5 lg:flex"><img src={profileImage} alt="" className="h-9 w-9 rounded-full object-cover" /><span className="text-sm font-semibold">{user?.name || 'Perfil'}</span><img src={chevronDownIcon} alt="" className="h-3.5 w-3.5" /></div>
          </div>
        </div>
      </header>

      <form onSubmit={handleSubmit} className="mx-auto grid w-full max-w-[1440px] gap-6 px-5 py-7 sm:px-8 lg:grid-cols-[minmax(0,1fr)_420px] lg:gap-10 lg:px-16 lg:py-10">
        <section className="rounded-3xl bg-white p-5 sm:p-8" aria-labelledby="checkout-heading">
          <h1 id="checkout-heading" className="font-display text-2xl font-extrabold text-[#7a1e1e] sm:text-[28px]">Finalizar Pedido</h1>
          <fieldset className="mt-7">
            <legend className="font-display text-lg font-bold text-[#7a1e1e]">Como você quer receber?</legend>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <button type="button" aria-pressed={fulfillmentMethod === 'pickup'} onClick={() => setFulfillmentMethod('pickup')} className={`rounded-2xl border p-4 text-left transition ${fulfillmentMethod === 'pickup' ? 'border-2 border-ilarica-orange bg-[#fff0e8]' : 'border-ilarica-line bg-white'}`}>
                <strong className={fulfillmentMethod === 'pickup' ? 'text-ilarica-orange' : 'text-ilarica-ink'}>Retirada presencial</strong><span className="mt-1 block text-xs text-ilarica-muted">Retire em um ponto disponível no campus.</span>
              </button>
              <button type="button" aria-pressed={fulfillmentMethod === 'delivery'} onClick={() => setFulfillmentMethod('delivery')} className={`rounded-2xl border p-4 text-left transition ${fulfillmentMethod === 'delivery' ? 'border-2 border-ilarica-orange bg-[#fff0e8]' : 'border-ilarica-line bg-white'}`}>
                <strong className={fulfillmentMethod === 'delivery' ? 'text-ilarica-orange' : 'text-ilarica-ink'}>Entrega no campus</strong><span className="mt-1 block text-xs text-ilarica-muted">Escolha uma zona de entrega válida.</span>
              </button>
            </div>
          </fieldset>

          <div className="mt-7">
            <label htmlFor="drop-off-zone" className="font-display text-lg font-bold text-[#7a1e1e]">{fulfillmentMethod === 'pickup' ? 'Ponto de Retirada' : 'Ponto de Entrega no Campus'}</label>
            <select id="drop-off-zone" value={selectedZoneId} onChange={(event) => setSelectedZoneId(event.target.value)} disabled={isLoadingZones || activeZones.length === 0} className="mt-3 h-12 w-full rounded-xl border border-transparent bg-[#fff1d6] px-4 outline-none focus:border-ilarica-orange disabled:cursor-not-allowed disabled:opacity-60">
              <option value="">{isLoadingZones ? 'Carregando pontos...' : 'Selecione um ponto'}</option>
              {activeZones.map((zone) => <option key={zone.id} value={zone.id}>{zone.name}</option>)}
            </select>
            {!isLoadingZones && activeZones.length === 0 && <p className="mt-2 text-xs font-semibold text-[#9f321b]">Nenhum ponto está disponível no momento.</p>}
          </div>

          <div className="mt-6">
            <label htmlFor="reference" className="text-sm font-bold text-ilarica-muted">Sala / Laboratório / Referência <span className="font-normal">(opcional, somente para sua revisão)</span></label>
            <textarea id="reference" value={reference} onChange={(event) => setReference(event.target.value)} maxLength={180} placeholder="Ex: Laboratório de Redes, Sala 204" className="mt-2 min-h-20 w-full resize-none rounded-xl border border-transparent bg-[#fff1d6] px-4 py-3 text-sm outline-none focus:border-ilarica-orange" />
            <p className="mt-2 text-xs text-ilarica-muted">A observação não será enviada enquanto o backend não possuir esse campo no contrato.</p>
          </div>

          <fieldset className="mt-7">
            <legend className="font-display text-lg font-bold text-[#7a1e1e]">Método de Pagamento</legend>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <button type="button" aria-pressed={paymentMethod === 'pix'} onClick={() => setPaymentMethod('pix')} className={`rounded-2xl border p-4 text-left font-bold transition ${paymentMethod === 'pix' ? 'border-2 border-ilarica-orange bg-[#fff0e8] text-ilarica-orange' : 'border-ilarica-line text-ilarica-muted'}`}>Pagar via Pix</button>
              <button type="button" aria-pressed={paymentMethod === 'wallet'} onClick={() => setPaymentMethod('wallet')} className={`rounded-2xl border p-4 text-left transition ${paymentMethod === 'wallet' ? 'border-2 border-ilarica-orange bg-[#fff0e8] text-ilarica-orange' : 'border-ilarica-line text-ilarica-muted'}`}>
                <strong>Carteira Digital</strong>
                {paymentMethod === 'wallet' && <span className="mt-1 block text-xs">Saldo: {wallet ? currencyFormatter.format(Number(wallet.balance)) : 'indisponível'}</span>}
              </button>
            </div>
          </fieldset>
        </section>

        <aside className="h-fit rounded-3xl bg-white p-6 sm:p-8" aria-labelledby="confirmation-heading">
          <h2 id="confirmation-heading" className="font-display text-xl font-extrabold text-[#7a1e1e]">Confirmar Pedido</h2>
          <p className="mt-6 text-sm font-bold">Cantina ({itemCount} {itemCount === 1 ? 'item' : 'itens'})</p>
          <ul className="mt-2 space-y-1.5 text-sm text-ilarica-muted">
            {items.map((item) => <li key={item.product.id}>{item.quantity}x {item.product.name}</li>)}
          </ul>
          <dl className="mt-6 border-t border-ilarica-line pt-5 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-ilarica-muted">Subtotal</dt><dd>{currencyFormatter.format(subtotal)}</dd></div>
          </dl>
          <div className="mt-4 flex items-center justify-between border-t border-ilarica-line pt-4 font-display font-extrabold text-[#7a1e1e]"><span className="text-lg">Total do Pedido</span><span className="text-[22px]">{currencyFormatter.format(subtotal)}</span></div>
          {error && <p role="alert" className="mt-5 rounded-xl border border-[#ffc9c2] bg-[#fff1f0] px-4 py-3 text-sm font-semibold text-[#a3261b]">{error}</p>}
          <button type="submit" disabled={isSubmitting || isLoadingZones || !selectedZoneId} className="mt-6 w-full rounded-full bg-ilarica-orange px-6 py-4 text-base font-bold text-white transition hover:bg-[#ed5925] disabled:cursor-not-allowed disabled:opacity-60">
            {isSubmitting ? 'Processando com segurança...' : 'Confirmar e Pagar'}
          </button>
          <Link to="/carrinho" className="mt-4 block text-center text-sm font-bold text-[#7a1e1e] hover:underline">Voltar ao carrinho</Link>
        </aside>
      </form>
    </main>
  );
}
