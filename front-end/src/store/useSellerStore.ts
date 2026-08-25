import { create } from 'zustand';

import itemOneImage from '../assets/figma/cart/item-1.png';
import itemTwoImage from '../assets/figma/cart/item-2.png';
import marmitaImage from '../assets/figma/mural/marmita.png';
import { listSellerOrders, updateSellerOrderStatus } from '../services';
import type { BusinessHoursEntry, SellerMenuItem, SellerOrder, SellerOrderStage, SellerSection } from '../types';

const initialItems: SellerMenuItem[] = [
  { id: 'mock-coxinha', name: 'Coxinha de Frango', description: 'A clássica coxinha de frango com requeijão cremoso, massa de batata ultra crocante.', price: '6.50', imageUrl: itemOneImage, isAvailable: true },
  { id: 'mock-pastel', name: 'Pastel de Forno', description: 'Opção assada com recheio leve de ricota e espinafre, massa integral artesanal.', price: '7.00', imageUrl: itemTwoImage, isAvailable: true },
  { id: 'mock-suco', name: 'Suco de Laranja 400ml', description: 'Espremido na hora, sem conservantes ou adição de água.', price: '5.50', imageUrl: marmitaImage, isAvailable: false },
];

const initialHours: BusinessHoursEntry[] = [
  { id: 'weekdays', label: 'Segunda a Sexta', opensAt: '08h', closesAt: '18h', isOpen: true },
  { id: 'saturday', label: 'Sábado', opensAt: '09h', closesAt: '13h', isOpen: true },
  { id: 'sunday', label: 'Domingo', opensAt: '--:--', closesAt: '--:--', isOpen: false },
];

interface SellerState {
  activeSection: SellerSection;
  items: SellerMenuItem[];
  businessHours: BusinessHoursEntry[];
  orders: SellerOrder[];
  orderStage: SellerOrderStage;
  isOrdersLoading: boolean;
  ordersError: string | null;
  transitioningOrderId: string | null;
  setActiveSection: (section: SellerSection) => void;
  toggleItemAvailability: (itemId: string) => void;
  removeItem: (itemId: string) => void;
  toggleBusinessDay: (dayId: BusinessHoursEntry['id']) => void;
  updateBusinessHour: (dayId: BusinessHoursEntry['id'], field: 'opensAt' | 'closesAt', value: string) => void;
  setOrderStage: (stage: SellerOrderStage) => void;
  loadOrders: () => Promise<void>;
  advanceOrder: (orderId: string) => Promise<void>;
  resetOrders: () => void;
}

export const useSellerStore = create<SellerState>((set) => ({
  activeSection: 'menu',
  items: initialItems,
  businessHours: initialHours,
  orders: [],
  orderStage: 'new',
  isOrdersLoading: false,
  ordersError: null,
  transitioningOrderId: null,
  setActiveSection: (activeSection) => set({ activeSection }),
  toggleItemAvailability: (itemId) => set((state) => ({ items: state.items.map((item) => item.id === itemId ? { ...item, isAvailable: !item.isAvailable } : item) })),
  removeItem: (itemId) => set((state) => ({ items: state.items.filter((item) => item.id !== itemId) })),
  toggleBusinessDay: (dayId) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === dayId ? { ...entry, isOpen: !entry.isOpen } : entry) })),
  updateBusinessHour: (dayId, field, value) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === dayId ? { ...entry, [field]: value } : entry) })),
  setOrderStage: (orderStage) => set({ orderStage }),
  loadOrders: async () => {
    set({ isOrdersLoading: true, ordersError: null });
    try {
      const orders = await listSellerOrders();
      set({ orders, isOrdersLoading: false });
    } catch {
      set({ isOrdersLoading: false, ordersError: 'Não foi possível carregar os pedidos da cantina.' });
    }
  },
  advanceOrder: async (orderId) => {
    const order = useSellerStore.getState().orders.find((entry) => entry.id === orderId);
    if (!order || order.status === 'ready_for_pickup') return;
    const status = order.status === 'paid' ? 'preparing' : 'ready_for_pickup';
    set({ transitioningOrderId: orderId, ordersError: null });
    try {
      const updated = await updateSellerOrderStatus(orderId, { status });
      set((state) => ({
        orders: state.orders.map((entry) => entry.id === orderId ? updated : entry),
        transitioningOrderId: null,
      }));
    } catch {
      set({ transitioningOrderId: null, ordersError: 'Não foi possível atualizar o pedido. Recarregue e tente novamente.' });
    }
  },
  resetOrders: () => set({ orders: [], orderStage: 'new', isOrdersLoading: false, ordersError: null, transitioningOrderId: null }),
}));
