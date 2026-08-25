interface RoleLandingPageProps {
  title: string;
  description: string;
}

export function RoleLandingPage({ title, description }: RoleLandingPageProps): React.JSX.Element {
  const [notice, setNotice] = useState(false);
  return (
    <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><AppHeader /><div className="mx-auto max-w-4xl px-5 py-12 sm:px-8 sm:py-16"><Card className="overflow-hidden border-0 shadow-none"><div className="bg-[#7a1e1e] px-7 py-9 text-white sm:px-10"><p className="text-xs font-bold uppercase tracking-[0.2em] text-[#ffb18f]">Piloto controlado</p><h1 className="mt-2 font-display text-4xl font-extrabold">{title}</h1><p className="mt-3 max-w-xl text-white/75">{description}</p></div><div className="p-7 sm:p-10"><div className="rounded-2xl bg-[#fffaf2] p-5"><h2 className="font-display text-xl font-bold text-[#7a1e1e]">Esta área está sendo preparada</h2><p className="mt-2 text-sm leading-relaxed text-ilarica-muted">O piloto atual está concentrado no ciclo de retirada presencial. Você poderá acessar esta operação assim que a próxima etapa for liberada.</p></div>{notice && <p role="status" className="mt-5 rounded-xl border border-[#f1d9b4] bg-[#fff8e8] px-4 py-3 text-sm font-semibold text-[#7a1e1e]">Funcionalidade em desenvolvimento</p>}<div className="mt-6 flex flex-wrap gap-3"><Button className="bg-ilarica-orange hover:bg-[#ed5925]" onClick={() => setNotice(true)}>Avisar quando disponível</Button><Link to="/perfil" className="inline-flex h-10 items-center rounded-xl bg-slate-200 px-4 text-sm font-semibold text-slate-900 hover:bg-slate-300">Ir para meu perfil</Link></div></div></Card></div></main>
  );
}
import { useState } from 'react';
import { Link } from 'react-router-dom';

import { AppHeader } from '../components/AppHeader';
import { Button, Card } from '../components/ui';
