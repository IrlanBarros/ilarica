import { create } from 'zustand';

import itemOneImage from '../assets/figma/cart/item-1.png';
import itemTwoImage from '../assets/figma/cart/item-2.png';
import marmitaImage from '../assets/figma/mural/marmita.png';
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

const initialOrders: SellerOrder[] = [
  { id: '80eab544-aede-45b7-a251-7c46d82dd2d8', displayCode: '#4081', customerName: 'Ana Clara', createdAt: '10:42', fulfillment: 'delivery', destination: 'Bloco C - Tecnologia, 2º andar', items: [{ productId: 'mock-coxinha', name: 'Coxinha de Frango', quantity: 2 }, { productId: 'mock-suco', name: 'Suco de Laranja 400ml', quantity: 1 }], totalAmount: '18.00', stage: 'new', notes: 'Entregar na sala 204.' },
  { id: '06ac2b63-9168-4387-9467-a99285912dfa', displayCode: '#4082', customerName: 'Lucas Mendes', createdAt: '10:35', fulfillment: 'pickup', destination: 'Retirada no balcão', items: [{ productId: 'mock-pastel', name: 'Pastel de Forno', quantity: 2 }], totalAmount: '14.00', stage: 'new' },
  { id: 'dd8920a3-4c42-43d3-b12a-884839b22cc5', displayCode: '#4079', customerName: 'Marina Alves', createdAt: '10:18', fulfillment: 'delivery', destination: 'Bloco A - Humanas, térreo', items: [{ productId: 'mock-coxinha', name: 'Coxinha de Frango', quantity: 1 }, { productId: 'mock-pastel', name: 'Pastel de Forno', quantity: 1 }], totalAmount: '13.50', stage: 'preparing' },
  { id: '683c2285-e043-4af5-aaac-061b307d2362', displayCode: '#4076', customerName: 'João Pedro', createdAt: '09:54', fulfillment: 'pickup', destination: 'Retirada no balcão', items: [{ productId: 'mock-suco', name: 'Suco de Laranja 400ml', quantity: 2 }], totalAmount: '11.00', stage: 'ready' },
];

interface SellerState {
  activeSection: SellerSection;
  items: SellerMenuItem[];
  businessHours: BusinessHoursEntry[];
  orders: SellerOrder[];
  orderStage: SellerOrderStage;
  setActiveSection: (section: SellerSection) => void;
  toggleItemAvailability: (itemId: string) => void;
  removeItem: (itemId: string) => void;
  toggleBusinessDay: (dayId: BusinessHoursEntry['id']) => void;
  updateBusinessHour: (dayId: BusinessHoursEntry['id'], field: 'opensAt' | 'closesAt', value: string) => void;
  setOrderStage: (stage: SellerOrderStage) => void;
  advanceOrder: (orderId: string) => void;
  resetOrders: () => void;
}

export const useSellerStore = create<SellerState>((set) => ({
  activeSection: 'menu',
  items: initialItems,
  businessHours: initialHours,
  orders: initialOrders,
  orderStage: 'new',
  setActiveSection: (activeSection) => set({ activeSection }),
  toggleItemAvailability: (itemId) => set((state) => ({ items: state.items.map((item) => item.id === itemId ? { ...item, isAvailable: !item.isAvailable } : item) })),
  removeItem: (itemId) => set((state) => ({ items: state.items.filter((item) => item.id !== itemId) })),
  toggleBusinessDay: (dayId) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === dayId ? { ...entry, isOpen: !entry.isOpen } : entry) })),
  updateBusinessHour: (dayId, field, value) => set((state) => ({ businessHours: state.businessHours.map((entry) => entry.id === dayId ? { ...entry, [field]: value } : entry) })),
  setOrderStage: (orderStage) => set({ orderStage }),
  advanceOrder: (orderId) => set((state) => ({ orders: state.orders.map((order) => order.id === orderId ? { ...order, stage: order.stage === 'new' ? 'preparing' : 'ready' } : order) })),
  resetOrders: () => set({ orders: initialOrders, orderStage: 'new' }),
}));
