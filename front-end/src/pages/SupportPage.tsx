import { useState } from 'react';
import { Link } from 'react-router-dom';

import { AppHeader } from '../components/AppHeader';
import { Card, Input } from '../components/ui';

export function SupportPage(): React.JSX.Element {
  const [orderId, setOrderId] = useState('');
  const supportEmail = import.meta.env.VITE_SUPPORT_EMAIL || 'suporte@ilarica.com.br';
  return <main className="min-h-screen bg-[#fff1d6]"><AppHeader /><div className="mx-auto max-w-3xl px-5 py-10 sm:px-8"><h1 className="font-display text-3xl font-extrabold text-[#7a1e1e]">Ajuda e suporte</h1><p className="mt-2 text-ilarica-muted">Encontre o canal correto para resolver seu problema.</p><div className="mt-7 grid gap-5 sm:grid-cols-2"><Card className="border-0 p-6 shadow-none"><h2 className="font-display text-xl font-bold text-[#7a1e1e]">Problema com pedido</h2><Input label="Número do pedido (opcional)" className="mt-3" value={orderId} onChange={(event) => setOrderId(event.target.value.slice(0, 36))} placeholder="Ex.: 4081" /><a href={`mailto:${supportEmail}?subject=${encodeURIComponent(`Suporte pedido ${orderId || 'não informado'}`)}`} className="mt-5 inline-flex min-h-11 items-center rounded-full bg-ilarica-orange px-5 text-sm font-bold text-white">Enviar e-mail ao suporte</a></Card><Card className="border-0 p-6 shadow-none"><h2 className="font-display text-xl font-bold text-[#7a1e1e]">Segurança da conta</h2><p className="mt-3 text-sm text-ilarica-muted">Para recuperar o acesso, utilize o fluxo protegido de redefinição.</p><Link to="/esqueci-senha" className="mt-5 inline-flex min-h-11 items-center rounded-full border border-ilarica-orange px-5 text-sm font-bold text-ilarica-orange">Recuperar senha</Link></Card></div><Card className="mt-5 border-0 p-6 shadow-none"><h2 className="font-display text-xl font-bold text-[#7a1e1e]">Privacidade e regras</h2><div className="mt-4 flex flex-wrap gap-4"><Link to="/privacidade" className="font-bold text-ilarica-orange underline">Política de Privacidade</Link><Link to="/termos" className="font-bold text-ilarica-orange underline">Termos de Uso</Link></div></Card></div></main>;
}
