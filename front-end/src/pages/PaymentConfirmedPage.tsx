import { useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';

import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import profileImage from '../assets/figma/cart/profile.png';
import searchIcon from '../assets/figma/cart/search.svg';
import shoppingCartIcon from '../assets/figma/cart/shopping-cart.svg';
import { getPaymentTransaction } from '../services';
import { useAuthStore, useCartStore } from '../store';
import type { PaymentTransaction } from '../types';

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

export function PaymentConfirmedPage(): React.JSX.Element {
  const { orderId } = useParams();
  const [searchParams] = useSearchParams();
  const user = useAuthStore((state) => state.user);
  const itemCount = useCartStore((state) => state.items.reduce((total, item) => total + item.quantity, 0));
  const [transaction, setTransaction] = useState<PaymentTransaction | null>(null);
  const [error, setError] = useState('');
  const transactionId = searchParams.get('transaction');

  useEffect(() => {
    if (!transactionId) {
      setError('Não foi possível validar este pagamento.');
      return;
    }
    void getPaymentTransaction(transactionId)
      .then((response) => {
        if (response.status !== 'succeeded' || response.order_id !== orderId) {
          setError('O pagamento ainda não foi confirmado pelo servidor.');
          return;
        }
        setTransaction(response);
      })
      .catch(() => setError('Não foi possível validar este pagamento.'));
  }, [orderId, transactionId]);

  const methodLabel = transaction?.payment_method === 'wallet' ? 'Carteira Digital' : 'Pix';

  return (
    <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink">
      <header className="border-b border-ilarica-line bg-white">
        <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-6 px-5 sm:px-8 lg:px-16">
          <Link to="/" className="flex shrink-0 items-center gap-3" aria-label="Ir para o Mural">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange">
              <img src={forkKnifeIcon} alt="" className="h-6 w-6" />
            </span>
            <span className="font-display text-xl font-extrabold text-[#7a1e1e] sm:text-[28px]">Ilarica</span>
          </Link>
          <Link to="/" className="hidden h-11 max-w-[480px] flex-1 items-center gap-3 rounded-full border border-ilarica-line bg-[#fff1d6] px-4 text-[15px] text-ilarica-muted md:flex">
            <img src={searchIcon} alt="" className="h-[18px] w-[18px]" />
            Buscar lanches, doces ou vendedores...
          </Link>
          <div className="flex shrink-0 items-center gap-3 lg:gap-6">
            <Link to="/carrinho" className="flex items-center gap-2 rounded-full bg-[#fff0e8] px-3 py-2.5 sm:px-4">
              <img src={shoppingCartIcon} alt="" className="h-[18px] w-[18px]" />
              <span className="text-sm font-bold text-ilarica-orange">{itemCount} {itemCount === 1 ? 'item' : 'itens'}</span>
            </Link>
            <Link to="/perfil" aria-label="Abrir meu perfil" className="flex min-h-11 items-center gap-2.5 rounded-full px-2 transition hover:bg-[#fff0e8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ilarica-orange">
              <img src={profileImage} alt="" className="h-9 w-9 rounded-full object-cover" />
              <span className="hidden text-sm font-semibold lg:inline">{user?.name || 'Perfil'}</span>
              <img src={chevronDownIcon} alt="" className="hidden h-3.5 w-3.5 lg:block" />
            </Link>
          </div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1440px] items-start justify-center px-5 py-10 sm:px-8 sm:py-16 lg:px-16">
        <section className="w-full max-w-[640px] rounded-3xl bg-white px-6 py-9 text-center shadow-[0_18px_50px_rgba(122,30,30,0.08)] sm:px-12 sm:py-12" aria-labelledby="payment-confirmed-heading">
          {!transaction && !error && <p role="status">Validando pagamento...</p>}
          {error && (
            <>
              <span className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-[#fff0e8] text-[38px] font-bold text-ilarica-orange" aria-hidden="true">!</span>
              <h1 id="payment-confirmed-heading" className="mt-6 font-display text-3xl font-extrabold text-[#7a1e1e]">Pagamento não validado</h1>
              <p role="alert" className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-[#a22727]">{error}</p>
              <Link to="/checkout" className="mt-8 inline-flex rounded-full bg-ilarica-orange px-7 py-3.5 text-sm font-bold text-white">Voltar ao Checkout</Link>
            </>
          )}
          {transaction && (
            <>
              <span className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-[#e9f8ee] text-[38px] font-bold text-[#239d52]" aria-hidden="true">✓</span>
              <h1 id="payment-confirmed-heading" className="mt-6 font-display text-3xl font-extrabold text-[#7a1e1e]">Pagamento Confirmado!</h1>
              <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-ilarica-muted">Seu pagamento foi aprovado e a cantina já pode preparar o pedido.</p>

              <div className="mx-auto mt-8 max-w-md rounded-2xl bg-[#fff1d6] p-5 text-left">
              <div className="flex items-center justify-between gap-4 border-b border-[#ead9bd] pb-3 text-sm">
                <span className="text-ilarica-muted">Valor pago</span>
                <strong className="text-lg text-[#7a1e1e]">{currencyFormatter.format(Number(transaction.amount))}</strong>
              </div>
                <div className="flex items-center justify-between gap-4 py-3 text-sm">
                  <span className="text-ilarica-muted">Forma de pagamento</span>
                  <strong>{methodLabel}</strong>
                </div>
                {orderId && (
                  <div className="flex flex-col gap-1 border-t border-[#ead9bd] pt-3 text-sm sm:flex-row sm:items-center sm:justify-between sm:gap-4">
                    <span className="text-ilarica-muted">Número do pedido</span>
                    <strong className="break-all text-xs">{orderId}</strong>
                  </div>
                )}
              </div>

              <div className="mt-8 rounded-2xl border border-[#d5eadb] bg-[#f4fbf6] px-5 py-4 text-sm text-[#287a38]">
                Acompanhe o preparo e a entrega pela área de pedidos.
              </div>

              <div className="mt-8 flex flex-col justify-center gap-3 sm:flex-row">
                <Link to="/pedidos" className="rounded-full bg-ilarica-orange px-7 py-3.5 text-sm font-bold text-white transition hover:bg-[#ed5925]">Acompanhar Pedido</Link>
                <Link to="/" className="rounded-full border border-ilarica-line px-7 py-3.5 text-sm font-bold text-[#7a1e1e] transition hover:bg-[#fffaf2]">Voltar ao Mural</Link>
              </div>
            </>
          )}
        </section>
      </div>
    </main>
  );
}
