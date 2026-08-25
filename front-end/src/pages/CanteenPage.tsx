import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

import chevronLeftIcon from '../assets/figma/canteen/chevron-left.svg';
import chevronRightIcon from '../assets/figma/canteen/chevron-right.svg';
import plusIcon from '../assets/figma/canteen/plus.svg';
import vendorHeroImage from '../assets/figma/canteen/vendor-hero.png';
import { getCanteen } from '../services/canteen.service';
import { listProducts } from '../services/product.service';
import { useCartStore } from '../store';
import type { Canteen, Product } from '../types';

const categoryLabels: Record<Product['category'], string> = {
  salgados: 'Salgados',
  bebidas: 'Bebidas',
  refeicoes: 'Refeições',
  doces: 'Doces',
  outros: 'Outros',
};

const currencyFormatter = new Intl.NumberFormat('pt-BR', {
  style: 'currency',
  currency: 'BRL',
});

function formatMoney(value: string): string {
  const amount = Number.parseFloat(value);
  return currencyFormatter.format(Number.isFinite(amount) ? amount : 0);
}

function PageLoading(): React.JSX.Element {
  return (
    <div aria-label="Carregando cardápio" className="min-h-screen animate-pulse bg-ilarica-cream">
      <div className="h-[174px] bg-[#d7d1c8]" />
      <div className="mx-auto max-w-5xl px-6 py-5">
        <div className="h-6 w-40 rounded bg-[#ebe7de]" />
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {[0, 1, 2].map((item) => (
            <div key={item} className="h-[106px] rounded-2xl border border-ilarica-line bg-white" />
          ))}
        </div>
      </div>
    </div>
  );
}

export function CanteenPage(): React.JSX.Element {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const items = useCartStore((state) => state.items);
  const cartCanteenId = useCartStore((state) => state.canteenId);
  const cartTotal = useCartStore((state) => state.total);
  const addItem = useCartStore((state) => state.addItem);
  const [canteen, setCanteen] = useState<Canteen | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [unavailableReason, setUnavailableReason] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<Product['category'] | 'todos'>('todos');
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [selectedQuantity, setSelectedQuantity] = useState(1);

  const loadCanteen = useCallback(async (): Promise<void> => {
    if (!id) {
      setError('Cantina inválida.');
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const [canteenData, productData] = await Promise.all([getCanteen(id), listProducts()]);
      setCanteen(canteenData);
      setProducts(
        productData.filter((product) => product.canteen_id === id && product.is_active),
      );
    } catch {
      setError('Não foi possível carregar esta cantina agora.');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    void loadCanteen();
  }, [loadCanteen]);

  const currentCartItems = useMemo(
    () => (cartCanteenId === id ? items : []),
    [cartCanteenId, id, items],
  );
  const itemCount = currentCartItems.reduce((total, item) => total + item.quantity, 0);
  const availableCategories = useMemo(
    () => Array.from(new Set(products.map((product) => product.category))),
    [products],
  );
  const visibleProducts = useMemo(
    () => selectedCategory === 'todos' ? products : products.filter((product) => product.category === selectedCategory),
    [products, selectedCategory],
  );

  function handleAddItem(product: Product, quantity = 1): void {
    setFeedback(null);
    try {
      addItem(product, quantity);
      setFeedback(`${quantity}x ${product.name} adicionado ao carrinho.`);
      setSelectedProduct(null);
      setSelectedQuantity(1);
    } catch {
      setFeedback('Seu carrinho contém itens de outra cantina. Esvazie-o antes de continuar.');
      setUnavailableReason('Para evitar pedidos divididos, o carrinho aceita produtos de apenas uma cantina por vez. Esvazie o carrinho atual para trocar de cantina.');
    }
  }

  if (isLoading) return <PageLoading />;

  if (error || !canteen) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-ilarica-cream px-6 text-center text-ilarica-ink">
        <div className="max-w-sm rounded-2xl border border-[#ffd1c1] bg-white p-7">
          <h1 className="font-display text-xl font-extrabold">Cardápio indisponível</h1>
          <p role="alert" className="mt-2 text-sm text-ilarica-muted">
            {error || 'A cantina solicitada não foi encontrada.'}
          </p>
          <div className="mt-5 flex justify-center gap-3">
            <button type="button" onClick={() => navigate(-1)} className="rounded-full border border-ilarica-line px-4 py-2 text-sm font-bold">
              Voltar
            </button>
            <button type="button" onClick={() => void loadCanteen()} className="rounded-full bg-ilarica-orange px-4 py-2 text-sm font-bold text-white">
              Tentar novamente
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-ilarica-cream pb-24 text-ilarica-ink">
      <div className="mx-auto w-full max-w-5xl">
        <header className="relative flex h-[174px] flex-col justify-between overflow-hidden px-5 py-5 text-white sm:rounded-b-3xl">
          <img src={vendorHeroImage} alt="" className="absolute inset-0 h-full w-full object-cover" />
          <div className="absolute inset-0 bg-black/40" />
          <button
            type="button"
            onClick={() => navigate(-1)}
            aria-label="Voltar ao mural"
            className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-black/15 transition hover:bg-black/30 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white"
          >
            <img src={chevronLeftIcon} alt="" className="h-6 w-6" />
          </button>

          <div className="relative z-10">
            <h1 className="font-display text-2xl font-extrabold leading-tight">{canteen.name}</h1>
            <p className="mt-0.5 text-xs leading-[1.45] text-white/90">
              {canteen.location} • {canteen.is_open ? 'Aberto agora' : 'Fechado no momento'}
            </p>
          </div>
        </header>

        <section className="px-6 pb-7 pt-5" aria-labelledby="menu-heading">
          <h2 id="menu-heading" className="font-display text-lg font-extrabold">
            Opções de Hoje
          </h2>

          {availableCategories.length > 1 && <nav aria-label="Filtrar cardápio por categoria" className="mt-4 flex gap-2 overflow-x-auto pb-1"><button type="button" aria-pressed={selectedCategory === 'todos'} onClick={() => setSelectedCategory('todos')} className={`min-h-11 shrink-0 rounded-full px-4 text-sm font-bold transition ${selectedCategory === 'todos' ? 'bg-ilarica-orange text-white' : 'border border-ilarica-line bg-white text-ilarica-muted'}`}>Todos</button>{availableCategories.map((category) => <button key={category} type="button" aria-pressed={selectedCategory === category} onClick={() => setSelectedCategory(category)} className={`min-h-11 shrink-0 rounded-full px-4 text-sm font-bold transition ${selectedCategory === category ? 'bg-ilarica-orange text-white' : 'border border-ilarica-line bg-white text-ilarica-muted'}`}>{categoryLabels[category]}</button>)}</nav>}

          {feedback && (
            <p
              role="status"
              className={`mt-3 rounded-xl px-4 py-3 text-xs font-semibold ${
                feedback.includes('outra cantina')
                  ? 'border border-[#ffd1c1] bg-[#fff5f1] text-[#9f321b]'
                  : 'border border-[#d4ead7] bg-[#f1f8f2] text-[#287a38]'
              }`}
            >
              {feedback}
            </p>
          )}

          {visibleProducts.length === 0 ? (
            <div className="mt-3 rounded-2xl border border-dashed border-[#dcd8ce] bg-white p-8 text-center">
              <p className="font-bold">Nenhuma opção disponível hoje</p>
              <p className="mt-1 text-sm text-ilarica-muted">Consulte novamente mais tarde.</p>
              <Link to="/" className="mt-5 inline-flex rounded-full bg-ilarica-orange px-5 py-2.5 text-sm font-bold text-white">Ver outras cantinas</Link>
            </div>
          ) : (
            <div className="mt-2 grid gap-3 md:grid-cols-2">
              {visibleProducts.map((product) => (
                <article
                  key={product.id}
                  className="flex min-h-[106px] cursor-pointer items-center gap-3 rounded-2xl border border-ilarica-line bg-white p-3.5 transition hover:border-ilarica-orange focus-within:border-ilarica-orange"
                  onClick={() => { setSelectedProduct(product); setSelectedQuantity(1); }}
                >
                  <div className="min-w-0 flex-1">
                    <span className="mb-1 inline-flex rounded-full bg-[#fff0e8] px-2 py-0.5 text-[10px] font-bold uppercase text-ilarica-orange">{categoryLabels[product.category]}</span>
                    <h3 className="font-display text-[15px] font-extrabold leading-tight">{product.name}</h3>
                    {product.description && (
                      <p className="mt-1 line-clamp-2 text-xs leading-[1.35] text-ilarica-muted">
                        {product.description}
                      </p>
                    )}
                    <p className="mt-1 font-bold text-[15px] text-ilarica-orange">{formatMoney(product.price)}</p>
                    <p className="mt-1 text-[11px] font-semibold text-ilarica-muted">{product.stock_quantity} unidades disponíveis</p>
                  </div>
                  <button
                    type="button"
                    onClick={(event) => { event.stopPropagation(); setSelectedProduct(product); setSelectedQuantity(1); }}
                    disabled={!canteen.is_open || product.stock_quantity === 0}
                    aria-label={`Ver detalhes de ${product.name}`}
                    className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-ilarica-orange transition hover:bg-[#ed5925] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ilarica-orange disabled:cursor-not-allowed disabled:bg-[#c9c5bc]"
                  >
                    <img src={plusIcon} alt="" className="h-4 w-4" />
                  </button>
                </article>
              ))}
            </div>
          )}
          {!canteen.is_open && <button type="button" onClick={() => setUnavailableReason('A cantina pausou temporariamente o recebimento de pedidos. Seus itens atuais não serão cobrados e você pode consultar outras cantinas.')} className="mt-4 min-h-11 font-bold text-ilarica-orange underline">Por que não posso adicionar itens?</button>}
        </section>
      </div>

      {itemCount > 0 && (
        <aside className="fixed inset-x-0 bottom-0 z-20 border-t border-ilarica-line bg-white" aria-label="Resumo do carrinho">
          <div className="mx-auto flex min-h-[68px] max-w-5xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
            <div className="min-w-0">
              <p className="text-sm font-bold">
                {itemCount} {itemCount === 1 ? 'item selecionado' : 'itens selecionados'}
              </p>
              <p className="mt-0.5 text-xs text-ilarica-muted">{currencyFormatter.format(cartTotal)} subtotal</p>
            </div>
            <Link
              to="/carrinho"
              className="flex shrink-0 items-center gap-1 rounded-full bg-ilarica-orange px-4 py-2.5 text-[13px] font-bold text-white transition hover:bg-[#ed5925] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ilarica-orange"
            >
              Ver Carrinho
              <img src={chevronRightIcon} alt="" className="h-3.5 w-3.5" />
            </Link>
          </div>
        </aside>
      )}
      {unavailableReason && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setUnavailableReason(null); }}><section role="alertdialog" aria-modal="true" aria-labelledby="unavailable-title" className="w-full max-w-md rounded-2xl bg-white p-6"><h2 id="unavailable-title" className="font-display text-xl font-extrabold text-[#7a1e1e]">Item indisponível</h2><p className="mt-2 text-sm leading-relaxed text-ilarica-muted">{unavailableReason}</p><div className="mt-6 flex flex-wrap justify-end gap-3"><Link to="/" className="inline-flex min-h-11 items-center rounded-xl bg-[#fff0e8] px-4 text-sm font-bold text-ilarica-orange">Ver outras cantinas</Link><button type="button" onClick={() => setUnavailableReason(null)} className="min-h-11 rounded-xl bg-ilarica-orange px-5 text-sm font-bold text-white">Entendi</button></div></section></div>}
      {selectedProduct && <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 px-4" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) setSelectedProduct(null); }}><section role="dialog" aria-modal="true" aria-labelledby="product-detail-title" className="w-full max-w-lg overflow-hidden rounded-3xl bg-white"><img src={selectedProduct.image_url || vendorHeroImage} alt="" className="h-48 w-full object-cover" /><div className="p-6"><div className="flex items-start justify-between gap-4"><div><span className="rounded-full bg-[#fff0e8] px-2.5 py-1 text-[10px] font-bold uppercase text-ilarica-orange">{categoryLabels[selectedProduct.category]}</span><h2 id="product-detail-title" className="mt-2 font-display text-2xl font-extrabold text-[#7a1e1e]">{selectedProduct.name}</h2></div><button type="button" aria-label="Fechar detalhes" onClick={() => setSelectedProduct(null)} className="flex h-11 w-11 items-center justify-center rounded-full bg-[#fff0e8] text-xl font-bold text-ilarica-orange">×</button></div>{selectedProduct.description && <p className="mt-3 text-sm leading-relaxed text-ilarica-muted">{selectedProduct.description}</p>}<div className="mt-5 flex items-center justify-between"><div><strong className="font-display text-2xl text-ilarica-orange">{formatMoney(selectedProduct.price)}</strong><p className="text-xs font-semibold text-ilarica-muted">Quantidade disponível: {selectedProduct.stock_quantity}</p></div><div className="flex items-center rounded-xl bg-[#fff1d6] p-1"><button type="button" aria-label="Diminuir quantidade" disabled={selectedQuantity === 1} onClick={() => setSelectedQuantity((value) => Math.max(1, value - 1))} className="h-11 w-11 rounded-lg font-bold text-ilarica-orange disabled:opacity-40">−</button><span aria-label="Quantidade selecionada" className="min-w-10 text-center font-bold">{selectedQuantity}</span><button type="button" aria-label="Aumentar quantidade" disabled={selectedQuantity >= selectedProduct.stock_quantity} onClick={() => setSelectedQuantity((value) => Math.min(selectedProduct.stock_quantity, value + 1))} className="h-11 w-11 rounded-lg font-bold text-ilarica-orange disabled:opacity-40">+</button></div></div><button type="button" disabled={!canteen.is_open || selectedProduct.stock_quantity === 0} onClick={() => handleAddItem(selectedProduct, selectedQuantity)} className="mt-6 min-h-12 w-full rounded-full bg-ilarica-orange px-6 font-bold text-white disabled:cursor-not-allowed disabled:bg-[#c9c5bc]">{selectedProduct.stock_quantity === 0 ? 'Produto esgotado' : `Adicionar ${selectedQuantity} ao carrinho`}</button></div></section></div>}
    </main>
  );
}
