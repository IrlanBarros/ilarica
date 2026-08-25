import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface PreferencesState {
  orderUpdates: boolean;
  pickupReady: boolean;
  setPreference: (key: 'orderUpdates' | 'pickupReady', value: boolean) => void;
}

export const usePreferencesStore = create<PreferencesState>()(persist((set) => ({
  orderUpdates: true,
  pickupReady: true,
  setPreference: (key, value) => set({ [key]: value }),
}), { name: 'ilarica-preferences', version: 1 }));
