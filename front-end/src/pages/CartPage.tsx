import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import itemOneImage from '../assets/figma/cart/item-1.png';
import itemTwoImage from '../assets/figma/cart/item-2.png';
import profileImage from '../assets/figma/cart/profile.png';
import searchIcon from '../assets/figma/cart/search.svg';
import shoppingCartIcon from '../assets/figma/cart/shopping-cart.svg';
import { useAuthStore, useCartStore } from '../store';

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

const itemImages = [itemOneImage, itemTwoImage];
const tipOptions = [1, 2, 3] as const;

export function CartPage(): React.JSX.Element {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const items = useCartStore((state) => state.items);
  const subtotal = useCartStore((state) => state.total);
  const updateQuantity = useCartStore((state) => state.updateQuantity);
  const removeItem = useCartStore((state) => state.removeItem);
  const clearCart = useCartStore((state) => state.clearCart);
  const [isPickup, setIsPickup] = useState(true);
  const [tip, setTip] = useState<number>(1);
  const [customTip, setCustomTip] = useState('');
  const [feedback, setFeedback] = useState<string | null>(null);

  const itemCount = items.reduce((total, item) => total + item.quantity, 0);
  const selectedTip = useMemo(() => {
    if (tip >= 0) return tip;
    const parsed = Number.parseFloat(customTip.replace(',', '.'));
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : 0;
  }, [customTip, tip]);
  const deliveryFee = isPickup ? 0 : 2;
  const total = subtotal + deliveryFee + selectedTip;

  function decreaseItem(productId: string, quantity: number): void {
    if (quantity === 1) {
      removeItem(productId);
      setFeedback('Item removido do carrinho.');
      return;
    }
    updateQuantity(productId, quantity - 1);
    setFeedback('Quantidade atualizada.');
  }

  function increaseItem(productId: string, quantity: number): void {
    updateQuantity(productId, quantity + 1);
    setFeedback('Quantidade atualizada.');
  }

  function handleClearCart(): void {
    clearCart();
    setFeedback('Carrinho esvaziado.');
  }

  function prepareNextStep(): void {
    navigate('/checkout');
  }

  if (items.length === 0) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#fff1d6] px-6 text-center text-ilarica-ink">
        <div className="w-full max-w-md rounded-3xl bg-white p-9 shadow-[0_16px_50px_rgba(122,30,30,0.07)]">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-[#fff0e8]">
            <img src={shoppingCartIcon} alt="" className="h-7 w-7" />
          </div>
          <h1 className="mt-5 font-display text-2xl font-extrabold text-[#7a1e1e]">Seu carrinho está vazio</h1>
          <p className="mt-2 text-sm leading-relaxed text-ilarica-muted">
            Explore o Mural e escolha uma opção deliciosa para começar seu pedido.
          </p>
          {feedback && <p role="status" className="mt-3 text-xs font-semibold text-[#287a38]">{feedback}</p>}
          <Link to="/" className="mt-6 inline-flex rounded-full bg-ilarica-orange px-6 py-3 text-sm font-bold text-white">
            Voltar ao Mural
          </Link>
        </div>
      </main>
    );
  }

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
            <div className="flex items-center gap-2 rounded-full bg-[#fff0e8] px-3 py-2.5 sm:px-4">
              <img src={shoppingCartIcon} alt="" className="h-[18px] w-[18px]" />
              <span className="text-sm font-bold text-ilarica-orange">{itemCount} {itemCount === 1 ? 'item' : 'itens'}</span>
            </div>
            <div className="hidden items-center gap-2.5 lg:flex">
              <img src={profileImage} alt="" className="h-9 w-9 rounded-full object-cover" />
              <span className="text-sm font-semibold">{user?.name || 'Perfil'}</span>
              <img src={chevronDownIcon} alt="" className="h-3.5 w-3.5" />
            </div>
          </div>
        </div>
      </header>

      <div className="mx-auto grid w-full max-w-[1440px] gap-6 px-5 py-7 sm:px-8 lg:grid-cols-[minmax(0,1fr)_420px] lg:gap-10 lg:px-16 lg:py-10">
        <section className="rounded-3xl bg-white p-5 sm:p-8" aria-labelledby="cart-heading">
          <div className="flex items-center justify-between gap-4">
            <h1 id="cart-heading" className="font-display text-2xl font-extrabold text-[#7a1e1e] sm:text-[28px]">Seu Carrinho</h1>
            <button type="button" onClick={handleClearCart} className="text-xs font-bold text-ilarica-orange hover:underline">
              Limpar carrinho
            </button>
          </div>

          {feedback && (
            <p role="status" className="mt-4 rounded-xl border border-[#d4ead7] bg-[#f1f8f2] px-4 py-3 text-xs font-semibold text-[#287a38]">
              {feedback}
            </p>
          )}

          <div className="mt-5 divide-y divide-ilarica-line">
            {items.map((item, index) => {
              const lineTotal = Number.parseFloat(item.product.price) * item.quantity;
              return (
                <article key={item.product.id} className="grid grid-cols-[64px_minmax(0,1fr)] items-center gap-3 py-4 first:pt-0 sm:grid-cols-[80px_minmax(0,1fr)_auto_100px] sm:gap-4">
                  <img src={itemImages[index % itemImages.length]} alt="" className="h-16 w-16 rounded-xl object-cover sm:h-20 sm:w-20" />
                  <div className="min-w-0">
                    <h2 className="font-display text-sm font-bold sm:text-base">{item.product.name}</h2>
                    <p className="mt-1 text-xs text-ilarica-muted">Cantina selecionada</p>
                    <button type="button" onClick={() => { removeItem(item.product.id); setFeedback('Item removido do carrinho.'); }} className="mt-1 text-[11px] font-semibold text-[#9f321b] hover:underline sm:hidden">
                      Remover
                    </button>
                  </div>
                  <div className="col-start-2 flex w-fit items-center gap-3 rounded-xl bg-[#fff1d6] p-1 sm:col-start-auto">
                    <button type="button" onClick={() => decreaseItem(item.product.id, item.quantity)} aria-label={item.quantity === 1 ? `Remover ${item.product.name}` : `Diminuir ${item.product.name}`} className="flex h-7 w-7 items-center justify-center rounded-lg bg-white font-bold text-ilarica-orange">−</button>
                    <span aria-label={`Quantidade de ${item.product.name}`} className="min-w-3 text-center font-bold">{item.quantity}</span>
                    <button type="button" onClick={() => increaseItem(item.product.id, item.quantity)} aria-label={`Aumentar ${item.product.name}`} className="flex h-7 w-7 items-center justify-center rounded-lg bg-white font-bold text-ilarica-orange">+</button>
                  </div>
                  <div className="col-start-2 flex items-center justify-between sm:col-start-auto sm:block">
                    <button type="button" onClick={() => { removeItem(item.product.id); setFeedback('Item removido do carrinho.'); }} className="hidden text-[11px] font-semibold text-[#9f321b] hover:underline sm:block">Remover</button>
                    <p className="font-bold text-[#7a1e1e] sm:mt-1 sm:text-right">{currencyFormatter.format(lineTotal)}</p>
                  </div>
                </article>
              );
            })}
          </div>

          <div className="mt-2 flex items-center justify-between gap-5 rounded-2xl bg-[#fff1d6] p-4 sm:p-5">
            <div>
              <h2 className="font-display text-sm font-bold text-[#7a1e1e] sm:text-base">Retirar Pessoalmente no Bloco</h2>
              <p className="mt-1 text-xs text-ilarica-muted">Retire na cantina para zerar a taxa de entrega rápida de R$ 2,00</p>
            </div>
            <button type="button" role="switch" aria-checked={isPickup} aria-label="Retirar pessoalmente" onClick={() => setIsPickup((value) => !value)} className={`relative h-7 w-14 shrink-0 rounded-full transition ${isPickup ? 'bg-ilarica-orange' : 'bg-[#c9c5bc]'}`}>
              <span className={`absolute top-1 h-5 w-5 rounded-full bg-white shadow transition ${isPickup ? 'left-8' : 'left-1'}`} />
            </button>
          </div>

          <div className="mt-5">
            <h2 className="font-display text-base font-bold text-[#7a1e1e] sm:text-lg">Apoie seu Colega Entregador (Gorjeta Solidária)</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {tipOptions.map((value) => (
                <button key={value} type="button" aria-pressed={tip === value} onClick={() => setTip(value)} className={`rounded-xl border px-4 py-2.5 text-sm ${tip === value ? 'border-ilarica-orange bg-[#fff0e8] font-bold text-ilarica-orange' : 'border-ilarica-line bg-white text-ilarica-muted'}`}>
                  {currencyFormatter.format(value)}
                </button>
              ))}
              <button type="button" aria-pressed={tip === -1} onClick={() => setTip(-1)} className={`rounded-xl border px-4 py-2.5 text-sm ${tip === -1 ? 'border-ilarica-orange bg-[#fff0e8] font-bold text-ilarica-orange' : 'border-ilarica-line bg-white text-ilarica-muted'}`}>
                Outro Valor
              </button>
              {tip === -1 && (
                <label className="flex items-center gap-2 rounded-xl border border-ilarica-line bg-white px-3 text-sm">
                  R$
                  <input aria-label="Outro valor de gorjeta" inputMode="decimal" value={customTip} onChange={(event) => setCustomTip(event.target.value)} className="w-20 bg-transparent py-2.5 outline-none" placeholder="0,00" />
                </label>
              )}
            </div>
          </div>
        </section>

        <aside className="h-fit rounded-3xl bg-white p-6 sm:p-8" aria-labelledby="summary-heading">
          <h2 id="summary-heading" className="font-display text-xl font-extrabold text-[#7a1e1e]">Resumo da Compra</h2>
          <dl className="mt-6 space-y-3 text-sm">
            <div className="flex justify-between gap-4"><dt className="text-ilarica-muted">Subtotal Itens</dt><dd>{currencyFormatter.format(subtotal)}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-ilarica-muted">Taxa de Entrega</dt><dd>{isPickup ? 'Grátis (Retirada)' : currencyFormatter.format(deliveryFee)}</dd></div>
            <div className="flex justify-between gap-4"><dt className="text-ilarica-muted">Gorjeta Solidária</dt><dd>{currencyFormatter.format(selectedTip)}</dd></div>
          </dl>
          <div className="mt-4 flex items-center justify-between border-t border-ilarica-line pt-4 font-display font-extrabold text-[#7a1e1e]">
            <span className="text-lg">Total Geral</span>
            <span className="text-[22px]">{currencyFormatter.format(total)}</span>
          </div>
          <button type="button" onClick={prepareNextStep} className="mt-6 w-full rounded-full bg-ilarica-orange px-6 py-4 text-base font-bold text-white transition hover:bg-[#ed5925]">
            Finalizar Pedido
          </button>
          <p className="mt-3 text-center text-[11px] leading-relaxed text-ilarica-muted">Nenhum pagamento será iniciado nesta etapa.</p>
        </aside>
      </div>
    </main>
  );
}
