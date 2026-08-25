import { Link } from 'react-router-dom';

import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import { getRoleHome } from '../routes/role-home';
import { useAuthStore } from '../store';

export function AppHeader(): React.JSX.Element {
  const user = useAuthStore((state) => state.user);
  const home = user ? getRoleHome(user.role) : '/';
  const navigation = user?.role === 'canteen_staff'
    ? [{ label: 'Pedidos', to: '/vendedor/pedidos' }, { label: 'Cardápio', to: '/vendedor/cardapio' }, { label: 'Perfil comercial', to: '/vendedor/onboarding' }]
    : user?.role === 'courier'
      ? [{ label: 'Entregas', to: '/entregas' }]
      : user?.role === 'admin'
        ? [{ label: 'Administração', to: '/admin' }]
        : [{ label: 'Pedidos', to: '/pedidos' }, { label: 'Carteira', to: '/carteira' }];
  return <header className="border-b border-[#efe6d7] bg-white"><div className="mx-auto flex h-20 max-w-[1280px] items-center justify-between gap-4 px-5 sm:px-8">
    <Link to={home} aria-label="Ir para a página inicial" className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span><span className="font-display text-[27px] font-extrabold text-[#7a1e1e]">Ilarica</span></Link>
    <nav className="flex items-center gap-2 text-sm font-semibold" aria-label="Conta">{navigation.map((item) => <Link key={item.to} to={item.to} className="hidden min-h-11 items-center rounded-full px-4 text-ilarica-muted hover:bg-[#fff0e8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ilarica-orange sm:flex">{item.label}</Link>)}<Link to="/perfil" className="inline-flex min-h-11 items-center rounded-full bg-[#fff0e8] px-4 text-[#7a1e1e] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ilarica-orange">{user?.name?.split(' ')[0] ?? 'Perfil'}</Link></nav>
  </div></header>;
}
