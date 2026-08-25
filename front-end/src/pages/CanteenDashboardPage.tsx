import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

import chevronDownIcon from '../assets/figma/cart/chevron-down.svg';
import forkKnifeIcon from '../assets/figma/cart/fork-knife.svg';
import searchIcon from '../assets/figma/cart/search.svg';
import shoppingCartIcon from '../assets/figma/cart/shopping-cart.svg';
import vendorImage from '../assets/figma/canteen/vendor-hero.png';
import { Button, Card, ConfirmDialog, Input } from '../components/ui';
import { useSellerStore } from '../store';
import type { BusinessHoursEntry, ProductCategory, SellerMenuItem } from '../types';

const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });

const sections = [
  { to: '/vendedor/cardapio', label: 'Meu Cardápio' },
  { to: '/vendedor/pedidos', label: 'Pedidos Recebidos' },
  { to: '/vendedor/horarios', label: 'Horários' },
  { to: '/vendedor/configuracoes', label: 'Configurações' },
];

function AvailabilitySwitch({ checked, label, onChange }: { checked: boolean; label: string; onChange: () => void }): React.JSX.Element {
  return (
    <button type="button" role="switch" aria-checked={checked} aria-label={label} onClick={onChange} className={`relative h-11 w-14 shrink-0 rounded-full transition ${checked ? 'bg-[#26a146]' : 'bg-[#929ca6]'}`}>
      <span className={`absolute top-2 h-7 w-7 rounded-full bg-white shadow-sm transition ${checked ? 'left-6' : 'left-1'}`} />
    </button>
  );
}

function SellerHeader(): React.JSX.Element {
  return (
    <header className="border-b border-[#efe6d7] bg-white">
      <div className="mx-auto flex h-20 max-w-[1440px] items-center justify-between gap-5 px-5 sm:px-8 lg:px-16">
        <Link to="/vendedor/pedidos" aria-label="Ir para o painel inicial do vendedor" className="flex shrink-0 items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-ilarica-orange"><img src={forkKnifeIcon} alt="" className="h-6 w-6" /></span>
          <span className="font-display text-[27px] font-extrabold text-[#7a1e1e]">Ilarica</span>
          <span className="hidden rounded-full bg-[#fff0e8] px-2.5 py-1 text-[10px] font-bold uppercase text-ilarica-orange sm:inline">Campus Centro</span>
        </Link>
        <div className="hidden h-11 max-w-[480px] flex-1 items-center gap-3 rounded-full border border-[#f0dfc2] bg-[#fff1d6] px-4 text-sm text-ilarica-muted md:flex"><img src={searchIcon} alt="" className="h-[18px] w-[18px]" />Buscar lanches, doces ou vendedores...</div>
        <div className="flex shrink-0 items-center gap-4">
          <span className="hidden items-center gap-2 rounded-full bg-[#fff0e8] px-4 py-2.5 text-sm font-bold text-ilarica-orange sm:flex"><img src={shoppingCartIcon} alt="" className="h-[18px] w-[18px]" />0 itens</span>
          <Link to="/perfil" aria-label="Abrir meu perfil" className="flex min-h-11 items-center gap-2 rounded-full px-2 transition hover:bg-[#fff0e8] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ilarica-orange"><img src={vendorImage} alt="" className="h-9 w-9 rounded-full object-cover" /><span className="hidden text-sm font-bold sm:inline">Cantina</span><img src={chevronDownIcon} alt="" className="h-3.5 w-3.5" /></Link>
        </div>
      </div>
    </header>
  );
}

function SellerSidebar(): React.JSX.Element {
  return (
    <aside className="h-fit rounded-2xl bg-white p-4 lg:sticky lg:top-6 lg:w-[280px] lg:p-5">
      <h2 className="mb-2 font-display text-lg font-extrabold text-[#7a1e1e]">Gerenciamento</h2>
      <nav className="flex gap-2 overflow-x-auto lg:flex-col" aria-label="Gerenciamento da cantina">
        {sections.map((section) => <Link key={section.to} to={section.to} aria-current={section.to === '/vendedor/cardapio' ? 'page' : undefined} className={`shrink-0 rounded-lg px-3 py-3 text-left text-sm transition lg:w-full ${section.to === '/vendedor/cardapio' ? 'bg-[#fff0e8] font-bold text-ilarica-orange' : 'text-ilarica-muted hover:bg-[#fffaf2]'}`}>{section.label}</Link>)}
      </nav>
    </aside>
  );
}

function MenuItemCard({ item, onEdit, onNotice }: { item: SellerMenuItem; onEdit: (item: SellerMenuItem) => void; onNotice: (message: string) => void }): React.JSX.Element {
  const toggle = useSellerStore((state) => state.toggleItemAvailability);
  const remove = useSellerStore((state) => state.removeItem);
  const [pendingAction, setPendingAction] = useState<'toggle' | 'delete' | null>(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  async function toggleAvailability(): Promise<void> {
    setPendingAction('toggle');
    try { await toggle(item.id); onNotice(`Produto ${item.isAvailable ? 'desativado' : 'ativado'} com sucesso.`); }
    catch { onNotice('Não foi possível alterar a disponibilidade do produto.'); }
    finally { setPendingAction(null); }
  }
  async function deleteItem(): Promise<void> {
    setPendingAction('delete');
    try { await remove(item.id); setConfirmDelete(false); onNotice('Produto excluído com sucesso.'); }
    catch { onNotice('Não foi possível excluir o produto.'); }
    finally { setPendingAction(null); }
  }
  return (
    <><Card className="grid gap-4 border-[#eadfce] p-4 shadow-none sm:grid-cols-[100px_minmax(0,1fr)] lg:grid-cols-[100px_minmax(0,1fr)_auto] lg:items-center">
      <img src={item.imageUrl || vendorImage} alt="" className="h-[100px] w-[100px] rounded-xl object-cover" />
      <div className="min-w-0"><div className="flex flex-wrap items-center gap-2"><h3 className="font-display text-lg font-extrabold text-[#7a1e1e]">{item.name}</h3><span className="rounded-full bg-[#fff0e8] px-2.5 py-1 text-[10px] font-bold uppercase text-ilarica-orange">{item.category}</span></div><p className="mt-1 max-w-xl text-sm leading-snug text-ilarica-muted">{item.description}</p><p className="mt-1 font-display text-base font-extrabold text-ilarica-orange">{currency.format(Number(item.price))}</p><p className="mt-1 text-xs font-semibold text-ilarica-muted">{item.stockQuantity} unidades disponíveis</p></div>
      <div className="col-span-full flex flex-wrap items-center justify-end gap-3 lg:col-span-1 lg:flex-nowrap">
        <span className={`text-xs ${item.isAvailable ? 'text-[#269b45]' : 'text-ilarica-muted'}`}>{item.isAvailable ? 'Disponível' : 'Indisponível'}</span>
        {pendingAction === 'toggle' ? <span className="h-5 w-5 animate-spin rounded-full border-2 border-[#26a146] border-t-transparent" aria-label="Atualizando disponibilidade" /> : <AvailabilitySwitch checked={item.isAvailable} label={`Alterar disponibilidade de ${item.name}`} onChange={() => { void toggleAvailability(); }} />}
        <Button variant="secondary" size="sm" disabled={pendingAction !== null} className="ml-2 rounded-lg bg-[#fff1d6] text-ilarica-muted hover:bg-[#f8e4bd]" onClick={() => onEdit(item)}>Editar</Button>
        <Button variant="danger" size="sm" disabled={pendingAction !== null} className="rounded-lg bg-[#ffe7e7] text-[#e22626] hover:bg-[#ffd5d5]" onClick={() => setConfirmDelete(true)}>Excluir</Button>
      </div>
    </Card><ConfirmDialog open={confirmDelete} title="Excluir produto?" description={`“${item.name}” será removido do cardápio. Esta ação não pode ser desfeita.`} confirmLabel="Excluir produto" isLoading={pendingAction === 'delete'} onCancel={() => setConfirmDelete(false)} onConfirm={() => { void deleteItem(); }} /></>
  );
}

function BusinessHoursPanel({ onSaved }: { onSaved: (success: boolean) => void }): React.JSX.Element {
  const hours = useSellerStore((state) => state.businessHours);
  const toggleDay = useSellerStore((state) => state.toggleBusinessDay);
  const updateHour = useSellerStore((state) => state.updateBusinessHour);
  const saveBusinessHours = useSellerStore((state) => state.saveBusinessHours);
  const [saving, setSaving] = useState(false);
  async function save(): Promise<void> {
    setSaving(true);
    try { await saveBusinessHours(); onSaved(true); }
    catch { onSaved(false); }
    finally { setSaving(false); }
  }
  return (
    <Card className="mt-8 border-0 p-6 shadow-none sm:p-8">
      <div className="flex flex-wrap items-center justify-between gap-4"><h2 className="font-display text-xl font-extrabold text-[#7a1e1e]">Horário de Funcionamento</h2><Button variant="ghost" isLoading={saving} loadingText="Salvando..." className="h-9 rounded-xl border border-ilarica-orange px-4 text-sm text-ilarica-orange hover:bg-[#fff0e8]" onClick={() => { void save(); }}>Salvar Alterações</Button></div>
      <div className="mt-6 divide-y divide-[#eee5d9]">
        {hours.map((entry: BusinessHoursEntry) => <div key={entry.id} className="grid items-center gap-3 py-5 sm:grid-cols-[minmax(140px,1fr)_120px_28px_120px_minmax(130px,1fr)]">
          <strong className="text-sm">{entry.label}</strong>
          <Input aria-label={`Abertura ${entry.label}`} value={entry.opensAt} disabled={!entry.isOpen} onChange={(event) => updateHour(entry.id, 'opensAt', event.target.value)} className="h-9 border-0 bg-[#fff1d6] px-4 focus:ring-ilarica-orange" />
          <span className="text-center text-xs text-ilarica-muted">até</span>
          <Input aria-label={`Fechamento ${entry.label}`} value={entry.closesAt} disabled={!entry.isOpen} onChange={(event) => updateHour(entry.id, 'closesAt', event.target.value)} className="h-9 border-0 bg-[#fff1d6] px-4 focus:ring-ilarica-orange" />
          <div className="flex items-center justify-end gap-3"><span className={`text-xs ${entry.isOpen ? 'text-[#269b45]' : 'text-ilarica-muted'}`}>{entry.isOpen ? 'Aberto' : 'Fechado'}</span><AvailabilitySwitch checked={entry.isOpen} label={`Alterar funcionamento de ${entry.label}`} onChange={() => toggleDay(entry.id)} /></div>
        </div>)}
      </div>
    </Card>
  );
}

export function CanteenDashboardPage(): React.JSX.Element {
  const items = useSellerStore((state) => state.items);
  const loadCatalog = useSellerStore((state) => state.loadCatalog);
  const createItem = useSellerStore((state) => state.createItem);
  const updateItem = useSellerStore((state) => state.updateItem);
  const isLoading = useSellerStore((state) => state.isCatalogLoading);
  const catalogError = useSellerStore((state) => state.catalogError);
  const [notice, setNotice] = useState('');
  const [editing, setEditing] = useState<SellerMenuItem | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [savingItem, setSavingItem] = useState(false);
  const [form, setForm] = useState<{ name: string; description: string; price: string; image_url: string; category: ProductCategory; stock_quantity: string }>({ name: '', description: '', price: '', image_url: '', category: 'outros', stock_quantity: '0' });

  useEffect(() => { void loadCatalog(); }, [loadCatalog]);

  function openForm(item?: SellerMenuItem): void {
    setEditing(item ?? null);
    setForm(item ? { name: item.name, description: item.description, price: item.price, image_url: item.imageUrl, category: item.category, stock_quantity: String(item.stockQuantity) } : { name: '', description: '', price: '', image_url: '', category: 'outros', stock_quantity: '0' });
    setShowForm(true);
  }

  async function submitItem(event: React.FormEvent): Promise<void> {
    event.preventDefault();
    if (savingItem) return;
    setSavingItem(true); setNotice('');
    try {
      const payload = { name: form.name, description: form.description || null, price: form.price, image_url: form.image_url || null, category: form.category, stock_quantity: Number(form.stock_quantity), is_active: editing?.isAvailable ?? true };
      if (editing) await updateItem(editing.id, payload); else await createItem(payload);
      setShowForm(false); setNotice('Produto salvo com sucesso.');
    } catch { setNotice('Não foi possível salvar o produto. Revise os dados e tente novamente.'); }
    finally { setSavingItem(false); }
  }

  return (
    <main className="min-h-screen bg-[#fff1d6] text-ilarica-ink">
      <SellerHeader />
      <div className="mx-auto grid w-full max-w-[1440px] gap-6 px-5 py-7 sm:px-8 lg:grid-cols-[280px_minmax(0,1fr)] lg:gap-10 lg:px-16 lg:py-10">
        <SellerSidebar />
        <section>
          <div className="flex flex-wrap items-start justify-between gap-5"><div><h1 className="font-display text-4xl font-extrabold text-[#7a1e1e]">Meu Cardápio</h1><p className="mt-1 text-base text-ilarica-muted">Gerencie seus produtos, preços e disponibilidade na plataforma.</p></div><Button leftIcon={<span aria-hidden="true" className="text-xl font-normal">+</span>} className="h-12 rounded-full bg-ilarica-orange px-7 hover:bg-[#ed5925]" onClick={() => openForm()}>Adicionar Item</Button></div>
          {notice && <p role="status" aria-live="polite" className="mt-5 rounded-xl border border-[#f1d9b4] bg-white px-4 py-3 text-sm text-[#7a1e1e]">{notice}</p>}
          {catalogError && <p role="alert" className="mt-5 rounded-xl bg-[#ffe7e7] p-4 text-[#a32020]">{catalogError}</p>}
          {showForm && <Card className="mt-6 border-[#eadfce] p-5"><form onSubmit={(event) => { void submitItem(event); }} className="grid gap-4 sm:grid-cols-2"><Input required minLength={2} disabled={savingItem} placeholder="Nome" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /><Input required type="number" min="0.01" step="0.01" disabled={savingItem} placeholder="Preço" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} /><label className="grid gap-1 text-sm font-semibold text-ilarica-muted">Categoria<select disabled={savingItem} value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value as ProductCategory })} className="h-11 rounded-xl border border-[#e0d3c0] bg-white px-3 text-ilarica-ink outline-none focus:border-ilarica-orange focus:ring-2 focus:ring-ilarica-orange/20"><option value="salgados">Salgados</option><option value="bebidas">Bebidas</option><option value="refeicoes">Refeições</option><option value="doces">Doces</option><option value="outros">Outros</option></select></label><Input required type="number" min="0" step="1" disabled={savingItem} label="Quantidade disponível" value={form.stock_quantity} onChange={(e) => setForm({ ...form, stock_quantity: e.target.value })} /><Input disabled={savingItem} placeholder="Descrição" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /><Input disabled={savingItem} placeholder="URL da imagem" value={form.image_url} onChange={(e) => setForm({ ...form, image_url: e.target.value })} /><div className="flex gap-3 sm:col-span-2"><Button type="submit" isLoading={savingItem} loadingText="Salvando...">Salvar produto</Button><Button type="button" variant="secondary" disabled={savingItem} onClick={() => setShowForm(false)}>Cancelar</Button></div></form></Card>}
          <div className="mt-7 space-y-4">{isLoading && <Card className="p-8 text-center"><span className="mx-auto block h-7 w-7 animate-spin rounded-full border-2 border-ilarica-orange border-t-transparent" aria-hidden="true" /><p className="mt-3 text-sm text-ilarica-muted">Carregando cardápio...</p></Card>}{!isLoading && items.map((item) => <MenuItemCard key={item.id} item={item} onEdit={openForm} onNotice={setNotice} />)}{!isLoading && items.length === 0 && <Card className="border-dashed p-8 text-center"><p className="font-display text-lg font-bold text-[#7a1e1e]">Seu cardápio ainda está vazio</p><p className="mt-1 text-sm text-ilarica-muted">Cadastre o primeiro produto para começar a receber pedidos.</p><Button className="mt-5 bg-ilarica-orange hover:bg-[#ed5925]" onClick={() => openForm()}>Adicionar primeiro produto</Button></Card>}</div>
          <BusinessHoursPanel onSaved={(success) => setNotice(success ? 'Horários salvos com sucesso.' : 'Não foi possível salvar os horários. Tente novamente.')} />
        </section>
      </div>
    </main>
  );
}
