import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import profileImage from '../assets/figma/cart/profile.png';
import searchIcon from '../assets/figma/cart/search.svg';
import shoppingCartIcon from '../assets/figma/cart/shopping-cart.svg';
import { ApiClientError } from '../api/http-error';
import { getPaymentTransaction } from '../services';
import { useAuthStore, useCartStore, usePaymentStore } from '../store';
import type { PaymentTransaction } from '../types';

const currencyFormatter = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

function remainingTime(expiresAt: string | null): string {
  if (!expiresAt) return '--:--';
  const seconds = Math.max(0, Math.floor((new Date(expiresAt).getTime() - Date.now()) / 1000));
  return `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
}

export function PixPaymentPage(): React.JSX.Element {
  const { transactionId } = useParams();
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const itemCount = useCartStore((state) => state.items.reduce((total, item) => total + item.quantity, 0));
  const clearCart = useCartStore((state) => state.clearCart);
  const clearPayment = usePaymentStore((state) => state.clear);
  const [transaction, setTransaction] = useState<PaymentTransaction | null>(null);
  const [clock, setClock] = useState('--:--');
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTransaction = useCallback(async () => {
    if (!transactionId) return;
    try {
      const response = await getPaymentTransaction(transactionId);
      setTransaction(response);
      setError(null);
      if (response.status === 'succeeded') {
        clearCart();
        clearPayment();
        navigate(`/pedidos/${response.order_id}/pagamento-confirmado?transaction=${response.id}`, {
          replace: true,
          state: { amount: Number(response.amount), method: 'pix', paymentStatus: 'confirmed' },
        });
      } else if (response.status === 'expired') {
        clearPayment();
        setError('Este Pix expirou. Volte ao Checkout para gerar um novo pedido e pagamento.');
      } else if (response.status === 'failed') {
        clearPayment();
        setError(response.failure_reason || 'O pagamento foi recusado.');
      }
    } catch (requestError) {
      if (requestError instanceof ApiClientError && requestError.status === 401) {
        setError('Sua sessão expirou. Entre novamente para acompanhar o pagamento.');
      } else {
        setError('Não foi possível consultar o pagamento. Tentaremos novamente automaticamente.');
      }
    }
  }, [clearCart, clearPayment, navigate, transactionId]);

  useEffect(() => {
    void loadTransaction();
    const polling = window.setInterval(() => void loadTransaction(), 3000);
    return () => window.clearInterval(polling);
  }, [loadTransaction]);

  useEffect(() => {
    setClock(remainingTime(transaction?.expires_at || null));
    const timer = window.setInterval(() => setClock(remainingTime(transaction?.expires_at || null)), 1000);
    return () => window.clearInterval(timer);
  }, [transaction?.expires_at]);

  const isTerminal = useMemo(
    () => transaction?.status === 'expired' || transaction?.status === 'failed',
    [transaction?.status],
  );

  async function copyPix(): Promise<void> {
    if (!transaction?.pix_copy_paste) return;
    await navigator.clipboard.writeText(transaction.pix_copy_paste);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 2000);
  }

  return (
    <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink">
      <header className="border-b border-ilarica-line bg-white">
        <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-6 px-5 sm:px-8 lg:px-16">
          <Link to="/" className="flex shrink-0 items-center gap-3" aria-label="Ir para o Mural"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span><span className="font-display text-xl font-extrabold text-[#7a1e1e] sm:text-[28px]">Ilarica</span></Link>
          <Link to="/" className="hidden h-11 max-w-[480px] flex-1 items-center gap-3 rounded-full border border-ilarica-line bg-[#fff1d6] px-4 text-[15px] text-ilarica-muted md:flex"><img src={searchIcon} alt="" className="h-[18px] w-[18px]" />Buscar lanches, doces ou vendedores...</Link>
          <div className="flex shrink-0 items-center gap-3 lg:gap-6"><span className="flex items-center gap-2 rounded-full bg-[#fff0e8] px-3 py-2.5 sm:px-4"><img src={shoppingCartIcon} alt="" className="h-[18px] w-[18px]" /><span className="text-sm font-bold text-ilarica-orange">{itemCount} {itemCount === 1 ? 'item' : 'itens'}</span></span><div className="hidden items-center gap-2.5 lg:flex"><img src={profileImage} alt="" className="h-9 w-9 rounded-full object-cover" /><span className="text-sm font-semibold">{user?.name || 'Perfil'}</span><img src={chevronDownIcon} alt="" className="h-3.5 w-3.5" /></div></div>
        </div>
      </header>

      <div className="mx-auto flex w-full max-w-[1440px] justify-center px-5 py-10 sm:px-8 sm:py-16">
        <section className="w-full max-w-[640px] rounded-3xl bg-white px-6 py-9 text-center shadow-[0_18px_50px_rgba(122,30,30,0.08)] sm:px-12 sm:py-12" aria-labelledby="pix-heading">
          <h1 id="pix-heading" className="font-display text-3xl font-extrabold text-[#7a1e1e]">Aguardando Pagamento</h1>
          <p className="mt-2 text-sm text-ilarica-muted">Pague via Pix para confirmar seu pedido.</p>
          {transaction && <><p className="mt-8 text-xs uppercase text-ilarica-muted">Valor total</p><p className="font-display text-4xl font-extrabold text-ilarica-orange">{currencyFormatter.format(Number(transaction.amount))}</p></>}
          {!isTerminal && <p className="mx-auto mt-2 w-fit rounded-full bg-[#fff1d6] px-3 py-1.5 text-xs font-bold text-[#7a1e1e]">Expira em {clock}</p>}

          {transaction?.pix_qr_code && !isTerminal && <img src={transaction.pix_qr_code} alt="QR Code Pix" className="mx-auto mt-7 h-56 w-56 rounded-2xl border-[12px] border-[#fff1d6] bg-white object-contain" />}
          {transaction?.pix_copy_paste && !isTerminal && <div className="mx-auto mt-7 max-w-lg text-left"><label htmlFor="pix-code" className="text-sm font-bold text-ilarica-muted">Pix Copia e Cola</label><div className="mt-2 flex gap-2"><input id="pix-code" readOnly value={transaction.pix_copy_paste} className="min-w-0 flex-1 rounded-xl bg-[#fff1d6] px-4 py-3 text-sm text-ilarica-muted" /><button type="button" onClick={() => void copyPix()} className="rounded-xl bg-ilarica-orange px-5 py-3 text-sm font-bold text-white">{copied ? 'Copiado!' : 'Copiar'}</button></div></div>}

          {error ? <p role="alert" className="mt-6 rounded-xl border border-[#ffc9c2] bg-[#fff1f0] px-4 py-3 text-sm font-semibold text-[#a3261b]">{error}</p> : <p role="status" className="mt-7 text-sm font-bold text-[#7a1e1e]">Aguardando confirmação segura do pagamento...</p>}
          <div className="mt-8 border-t border-ilarica-line pt-6"><Link to="/checkout" className="text-sm font-bold text-ilarica-muted underline">Voltar para o Checkout</Link></div>
        </section>
      </div>
    </main>
  );
}
