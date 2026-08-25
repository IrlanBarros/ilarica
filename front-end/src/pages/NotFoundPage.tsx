import { Link } from 'react-router-dom';

import { AppHeader } from '../components/AppHeader';
import { getRoleHome } from '../routes/role-home';
import { useAuthStore } from '../store';

export function NotFoundPage(): React.JSX.Element {
  const user = useAuthStore((state) => state.user);
  const home = user ? getRoleHome(user.role) : '/login';
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink">{user && <AppHeader />}<div className="mx-auto flex max-w-xl flex-col items-center px-6 py-24 text-center"><span className="font-display text-7xl font-extrabold text-ilarica-orange">404</span><h1 className="mt-4 font-display text-3xl font-extrabold text-[#7a1e1e]">Página não encontrada</h1><p className="mt-3 text-ilarica-muted">O endereço pode ter mudado ou não está disponível para sua conta.</p><Link to={home} className="mt-7 inline-flex min-h-11 items-center rounded-full bg-ilarica-orange px-6 font-bold text-white">Voltar ao início</Link></div></main>;
}
