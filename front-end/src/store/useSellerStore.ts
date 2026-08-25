import { create } from 'zustand';

import { confirmSellerOrderPickup, createMyCanteenProduct, deleteMyCanteenProduct, getMyCanteen, listMyCanteenProducts, listSellerOrders, updateMyCanteen, updateMyCanteenProduct, updateSellerOrderStatus } from '../services';
import type { BusinessHoursEntry, ProductCreate, ProductUpdate, SellerMenuItem, SellerOrder, SellerOrderStage, SellerSection } from '../types';

const labels: Record<BusinessHoursEntry['id'], string> = { weekdays: 'Segunda a Sexta', saturday: 'Sábado', sunday: 'Domingo' };
const toItem = (product: Awaited<ReturnType<typeof listMyCanteenProducts>>[number]): SellerMenuItem => ({ id: product.id, name: product.name, description: product.description ?? '', price: String(product.price), imageUrl: product.image_url ?? '', isAvailable: product.is_active });

interface SellerState {
  activeSection: SellerSection; items: SellerMenuItem[]; businessHours: BusinessHoursEntry[];
  isCatalogLoading: boolean; catalogError: string | null; orders: SellerOrder[]; orderStage: SellerOrderStage;
  isOrdersLoading: boolean; ordersError: string | null; transitioningOrderId: string | null; confirmingOrderId: string | null;
  setActiveSection: (section: SellerSection) => void; loadCatalog: () => Promise<void>;
  createItem: (payload: ProductCreate) => Promise<void>; updateItem: (id: string, payload: ProductUpdate) => Promise<void>;
  toggleItemAvailability: (id: string) => Promise<void>; removeItem: (id: string) => Promise<void>;
  toggleBusinessDay: (id: BusinessHoursEntry['id']) => void;
  updateBusinessHour: (id: BusinessHoursEntry['id'], field: 'opensAt' | 'closesAt', value: string) => void;
  saveBusinessHours: () => Promise<void>; setOrderStage: (stage: SellerOrderStage) => void;
  loadOrders: () => Promise<void>; advanceOrder: (id: string) => Promise<void>;
  confirmPickup: (id: string, pin: string) => Promise<void>; resetOrders: () => void;
}

export const useSellerStore = create<SellerState>((set, get) => ({
  activeSection: 'menu', items: [], businessHours: [], isCatalogLoading: false, catalogError: null,
  orders: [], orderStage: 'new', isOrdersLoading: false, ordersError: null, transitioningOrderId: null, confirmingOrderId: null,
  setActiveSection: (activeSection) => set({ activeSection }),
  loadCatalog: async () => {
    set({ isCatalogLoading: true, catalogError: null });
    try {
      const [products, canteen] = await Promise.all([listMyCanteenProducts(), getMyCanteen()]);
      set({ items: products.map(toItem), businessHours: (canteen.opening_hours ?? []).map((entry) => ({ id: entry.day, label: labels[entry.day], opensAt: entry.opens_at, closesAt: entry.closes_at, isOpen: entry.is_open })), isCatalogLoading: false });
    } catch { set({ isCatalogLoading: false, catalogError: 'Não foi possível carregar o cardápio da cantina.' }); }
  },
  createItem: async (payload) => { const created = toItem(await createMyCanteenProduct(payload)); set((state) => ({ items: [...state.items, created] })); },
  updateItem: async (id, payload) => { const updated = toItem(await updateMyCanteenProduct(id, payload)); set((state) => ({ items: state.items.map((item) => item.id === id ? updated : item) })); },
  toggleItemAvailability: async (id) => { const item = get().items.find((entry) => entry.id === id); if (item) await get().updateItem(id, { is_active: !item.isAvailable }); },
  removeItem: async (id) => { await deleteMyCanteenProduct(id); set((state) => ({ items: state.items.filter((item) => item.id !== id) })); },
  toggleBusinessDay: (id) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === id ? { ...entry, isOpen: !entry.isOpen } : entry) })),
  updateBusinessHour: (id, field, value) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === id ? { ...entry, [field]: value } : entry) })),
  saveBusinessHours: async () => { await updateMyCanteen({ opening_hours: get().businessHours.map((entry) => ({ day: entry.id, opens_at: entry.opensAt, closes_at: entry.closesAt, is_open: entry.isOpen })) }); },
  setOrderStage: (orderStage) => set({ orderStage }),
  loadOrders: async () => { set({ isOrdersLoading: true, ordersError: null }); try { set({ orders: await listSellerOrders(), isOrdersLoading: false }); } catch { set({ isOrdersLoading: false, ordersError: 'Não foi possível carregar os pedidos da cantina.' }); } },
  advanceOrder: async (id) => { const order = get().orders.find((entry) => entry.id === id); if (!order || order.status === 'ready_for_pickup') return; const status = order.status === 'paid' ? 'preparing' : 'ready_for_pickup'; set({ transitioningOrderId: id, ordersError: null }); try { const updated = await updateSellerOrderStatus(id, { status }); set((state) => ({ orders: state.orders.map((entry) => entry.id === id ? updated : entry), transitioningOrderId: null })); } catch { set({ transitioningOrderId: null, ordersError: 'Não foi possível atualizar o pedido. Recarregue e tente novamente.' }); } },
  confirmPickup: async (id, pin) => {
    set({ confirmingOrderId: id, ordersError: null });
    try {
      await confirmSellerOrderPickup(id, pin);
      set((state) => ({ orders: state.orders.filter((order) => order.id !== id), confirmingOrderId: null }));
    } catch (error) {
      set({ confirmingOrderId: null, ordersError: 'PIN inválido ou pedido indisponível para retirada.' });
      throw error;
    }
  },
  resetOrders: () => set({ orders: [], orderStage: 'new', isOrdersLoading: false, ordersError: null, transitioningOrderId: null, confirmingOrderId: null }),
}));
