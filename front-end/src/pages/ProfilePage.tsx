import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import { AppHeader } from '../components/AppHeader';
import { Button, Card, ConfirmDialog, Input } from '../components/ui';
import { formatBrazilianPhone } from '../lib/phone';
import { useAuthStore } from '../store';

const roleLabels = { customer: 'Cliente', courier: 'Entregador', canteen_staff: 'Equipe da cantina', admin: 'Administrador' } as const;

export function ProfilePage(): React.JSX.Element {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();
  const [confirmLogout, setConfirmLogout] = useState(false);
  return <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink"><AppHeader /><div className="mx-auto max-w-3xl px-5 py-10 sm:px-8 sm:py-14">
    <div><p className="text-sm font-bold uppercase tracking-[0.18em] text-ilarica-orange">Minha conta</p><h1 className="mt-1 font-display text-4xl font-extrabold text-[#7a1e1e]">Meu perfil</h1><p className="mt-2 text-ilarica-muted">Confira os dados vinculados à sua conta iLarica.</p></div>
    <Card className="mt-8 border-0 p-6 shadow-none sm:p-8"><div className="grid gap-5 sm:grid-cols-2"><Input label="Nome completo" value={user?.name ?? ''} readOnly /><Input label="WhatsApp" prefix="+55" value={formatBrazilianPhone(user?.whatsapp ?? '')} readOnly /><Input label="E-mail" value={user?.email ?? ''} readOnly wrapperClassName="sm:col-span-2" /><Input label="Tipo de conta" value={user ? roleLabels[user.role] : ''} readOnly /><div className="flex items-end"><span className={`mb-1 inline-flex rounded-full px-3 py-2 text-xs font-bold ${user?.is_email_validated ? 'bg-[#eff9f1] text-[#237b39]' : 'bg-[#fff4db] text-[#9a6710]'}`}>{user?.is_email_validated ? 'E-mail validado' : 'Validação pendente'}</span></div></div>
      <p className="mt-6 rounded-xl bg-[#fffaf2] px-4 py-3 text-xs text-ilarica-muted">A edição do perfil ficará disponível quando o backend oferecer um endpoint seguro de atualização da própria conta.</p>
      <div className="mt-7 flex flex-wrap gap-4 border-t border-ilarica-line pt-6"><Link to="/preferencias" className="inline-flex min-h-11 items-center rounded-xl bg-[#fff0e8] px-4 text-sm font-bold text-ilarica-orange">Notificações</Link><Link to="/suporte" className="inline-flex min-h-11 items-center rounded-xl bg-[#fff0e8] px-4 text-sm font-bold text-ilarica-orange">Ajuda e suporte</Link><Button variant="danger" onClick={() => setConfirmLogout(true)}>Sair da conta</Button></div>
    </Card>
    <ConfirmDialog open={confirmLogout} title="Sair da conta?" description="Você precisará informar suas credenciais novamente para acessar o iLarica." confirmLabel="Sair" onCancel={() => setConfirmLogout(false)} onConfirm={() => { logout(); navigate('/login', { replace: true }); }} />
  </div></main>;
}
