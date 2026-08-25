import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

import browniesImage from '../assets/figma/mural/brownies.png';
import cakeSliceIcon from '../assets/figma/mural/cake-slice.svg';
import fileTextIcon from '../assets/figma/mural/file-text.svg';
import hamburgerIcon from '../assets/figma/mural/hamburger.svg';
import houseIcon from '../assets/figma/mural/house.svg';
import marmitaImage from '../assets/figma/mural/marmita.png';
import pastelImage from '../assets/figma/mural/pastel.png';
import pieChartIcon from '../assets/figma/mural/pie-chart.svg';
import salgadosImage from '../assets/figma/mural/salgados.png';
import searchIcon from '../assets/figma/mural/search.svg';
import shoppingBagIcon from '../assets/figma/mural/shopping-bag.svg';
import shoppingBasketIcon from '../assets/figma/mural/shopping-basket.svg';
import userIcon from '../assets/figma/mural/user.svg';
import walletIcon from '../assets/figma/mural/wallet.svg';
import { formatNextOpening } from '../lib/canteen-hours';
import { listCanteens } from '../services/canteen.service';
import { listProducts } from '../services/product.service';
import { useAuthStore, useCartStore } from '../store';
import type { Canteen, Product } from '../types';

const categories = [
  { label: 'Lanches', icon: hamburgerIcon },
  { label: 'Bebidas', icon: shoppingBasketIcon },
  { label: 'Doces', icon: cakeSliceIcon },
  { label: 'Salgados', icon: pieChartIcon },
] as const;

const navigation = [
  { label: 'Mural', to: '/', icon: houseIcon },
  { label: 'Pedidos', to: '/pedidos', icon: fileTextIcon },
  { label: 'Carteira', to: '/carteira', icon: walletIcon },
  { label: 'Perfil', to: '/perfil', icon: userIcon },
] as const;

const fallbackImages = [browniesImage, salgadosImage, marmitaImage, pastelImage];

interface CanteenView extends Canteen {
  safeName: string;
  safeLocation: string;
  image: string;
  searchableText: string;
}

function buildCanteenViews(canteens: Canteen[], products: Product[]): CanteenView[] {
  return canteens.map((canteen, index) => {
    const canteenProducts = products.filter(
      (product) => product.canteen_id === canteen.id && product.is_active,
    );
    const safeName = canteen.name.trim() || 'Vendedor indisponível';
    const safeLocation = canteen.location.trim() || 'Local não informado';
    const productNames = canteenProducts.map((product) => product.name).filter(Boolean);

    return {
      ...canteen,
      safeName,
      safeLocation,
      image: fallbackImages[index % fallbackImages.length],
      searchableText: [safeName, safeLocation, ...productNames]
        .join(' ')
        .toLocaleLowerCase('pt-BR'),
    };
  });
}

function LoadingCards(): React.JSX.Element {
  return (
    <div aria-label="Carregando vendedores" className="grid gap-3 md:grid-cols-2">
      {[0, 1, 2].map((item) => (
        <div key={item} className="flex animate-pulse gap-3 rounded-2xl border border-ilarica-line bg-white p-3">
          <div className="h-20 w-20 shrink-0 rounded-xl bg-[#f1eee6]" />
          <div className="flex flex-1 flex-col justify-center gap-2">
            <div className="h-4 w-2/3 rounded bg-[#f1eee6]" />
            <div className="h-3 w-full rounded bg-[#f5f2eb]" />
            <div className="h-5 w-16 rounded-full bg-[#edf5ee]" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function HomePage(): React.JSX.Element {
  const user = useAuthStore((state) => state.user);
  const cartItems = useCartStore((state) => state.items);
  const [canteens, setCanteens] = useState<Canteen[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [query, setQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('Lanches');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadMural = useCallback(async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      const [canteenData, productData] = await Promise.all([listCanteens(), listProducts()]);
      setCanteens(canteenData);
      setProducts(productData);
    } catch {
      setError('Não foi possível carregar os vendedores agora.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadMural();
  }, [loadMural]);

  const canteenViews = useMemo(() => buildCanteenViews(canteens, products), [canteens, products]);
  const visibleCanteens = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase('pt-BR');
    if (!normalizedQuery) return canteenViews;
    return canteenViews.filter((canteen) => canteen.searchableText.includes(normalizedQuery));
  }, [canteenViews, query]);

  const firstName = user?.name.trim().split(/\s+/)[0] || 'visitante';
  const cartCount = cartItems.reduce((total, item) => total + item.quantity, 0);

  return (
    <div className="min-h-screen bg-ilarica-cream text-ilarica-ink">
      <div className="mx-auto w-full max-w-5xl px-5 pb-24 pt-8 sm:px-7 lg:px-8">
        <header className="flex items-center justify-between">
          <div>
            <p className="text-sm text-ilarica-muted">E aí, com fome?</p>
            <h1 className="mt-0.5 font-display text-[22px] font-extrabold leading-tight">
              Olá, {firstName}! <span aria-hidden="true">👋</span>
            </h1>
          </div>

          <Link
            to="/carrinho"
            aria-label={`Carrinho com ${cartCount} ${cartCount === 1 ? 'item' : 'itens'}`}
            className="relative flex h-11 w-11 items-center justify-center rounded-[14px] bg-[#fff0e8] transition hover:bg-[#ffe5d8] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ilarica-orange"
          >
            <img src={shoppingBagIcon} alt="" className="h-[22px] w-[22px]" />
            {cartCount > 0 && (
              <span className="absolute -right-1 -top-1 flex min-h-4 min-w-4 items-center justify-center rounded-full bg-[#ef4444] px-1 text-[9px] font-bold text-white">
                {cartCount > 99 ? '99+' : cartCount}
              </span>
            )}
          </Link>
        </header>

        <label className="mt-6 flex h-11 items-center gap-3 rounded-[14px] border border-ilarica-line bg-white px-4 focus-within:border-ilarica-orange focus-within:ring-2 focus-within:ring-orange-100">
          <img src={searchIcon} alt="" className="h-[18px] w-[18px] shrink-0" />
          <span className="sr-only">Buscar vendedores ou comidas</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Buscar vendedores ou comidas..."
            className="min-w-0 flex-1 bg-transparent text-sm outline-none placeholder:text-[#a3a095]"
          />
        </label>

        <div className="-mx-5 mt-4 overflow-x-auto px-5 [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
          <div className="flex w-max gap-2" aria-label="Categorias">
            {categories.map((category) => {
              const isSelected = selectedCategory === category.label;
              return (
                <button
                  key={category.label}
                  type="button"
                  aria-pressed={isSelected}
                  onClick={() => setSelectedCategory(category.label)}
                  className={`flex h-9 items-center gap-2 rounded-full border px-4 text-xs font-semibold transition ${
                    isSelected
                      ? 'border-ilarica-orange bg-[#fff0e8] text-ilarica-orange'
                      : 'border-ilarica-line bg-white text-ilarica-muted hover:border-[#dcd8ce]'
                  }`}
                >
                  <img src={category.icon} alt="" className="h-4 w-4" />
                  {category.label}
                </button>
              );
            })}
          </div>
        </div>

        <section className="mt-6" aria-labelledby="available-heading">
          <h2 id="available-heading" className="font-display text-lg font-bold">
            Disponíveis para Entrega Hoje
          </h2>

          <div className="mt-3">
            {isLoading ? (
              <LoadingCards />
            ) : error ? (
              <div role="alert" className="rounded-2xl border border-[#ffd1c1] bg-[#fff5f1] p-5 text-sm">
                <p className="font-semibold text-[#9f321b]">{error}</p>
                <button
                  type="button"
                  onClick={() => void loadMural()}
                  className="mt-3 rounded-full bg-ilarica-orange px-4 py-2 font-semibold text-white"
                >
                  Tentar novamente
                </button>
              </div>
            ) : visibleCanteens.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[#dcd8ce] bg-white p-7 text-center">
                <p className="font-semibold">
                  {query ? 'Nenhum vendedor encontrado' : 'Nenhum vendedor disponível agora'}
                </p>
                <p className="mt-1 text-sm text-ilarica-muted">
                  {query ? 'Tente buscar por outro nome ou comida.' : 'Volte em breve para conferir as novidades.'}
                </p>
              </div>
            ) : (
              <div className="grid gap-3 md:grid-cols-2">
                {visibleCanteens.map((canteen) => (
                  <Link
                    key={canteen.id}
                    to={`/cantina/${canteen.id}`}
                    className="group flex min-w-0 gap-3 rounded-2xl border border-ilarica-line bg-white p-3 transition hover:-translate-y-0.5 hover:border-[#ded9ce] hover:shadow-[0_8px_25px_rgba(83,71,53,0.08)] focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ilarica-orange"
                  >
                    <img src={canteen.image} alt="" className="h-20 w-20 shrink-0 rounded-xl object-cover" />
                    <div className="min-w-0 flex-1 py-0.5">
                      <h3 className="truncate text-[15px] font-bold group-hover:text-ilarica-orange">
                        {canteen.safeName}
                      </h3>
                      <p className="mt-1 line-clamp-2 text-xs leading-[1.45] text-ilarica-muted">
                        {canteen.safeLocation}
                      </p>
                      <span
                        className={`mt-2 inline-flex rounded-full px-2.5 py-1 text-[10px] font-bold ${
                          (canteen.is_accepting_orders ?? canteen.is_open)
                            ? 'bg-[#edf7ee] text-[#287a38]'
                            : 'bg-[#f1f0ed] text-[#77746d]'
                        }`}
                      >
                        {(canteen.is_accepting_orders ?? canteen.is_open) ? 'Aberto agora' : 'Fechado'}
                      </span>
                      {!(canteen.is_accepting_orders ?? canteen.is_open) && formatNextOpening(canteen.next_opening_at) && (
                        <p className="mt-1 text-[10px] font-semibold text-ilarica-orange">
                          {formatNextOpening(canteen.next_opening_at)}
                        </p>
                      )}
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </section>
      </div>

      <nav className="fixed inset-x-0 bottom-0 z-20 border-t border-ilarica-line bg-white/95 backdrop-blur" aria-label="Navegação principal">
        <div className="mx-auto grid h-[72px] max-w-md grid-cols-4 px-3">
          {navigation.map((item) => {
            const isCurrent = item.to === '/';
            return (
              <Link
                key={item.label}
                to={item.to}
                aria-current={isCurrent ? 'page' : undefined}
                className={`flex flex-col items-center justify-center gap-1 text-[10px] font-semibold ${
                  isCurrent ? 'text-ilarica-orange' : 'text-[#a3a095]'
                }`}
              >
                <img src={item.icon} alt="" className="h-[22px] w-[22px]" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
