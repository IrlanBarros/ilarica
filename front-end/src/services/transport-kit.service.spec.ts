import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  TransportKit,
  TransportKitCreate,
  TransportKitUpdate,
} from '../types';
import {
  createTransportKit,
  deleteTransportKit,
  getTransportKit,
  listTransportKits,
  updateTransportKit,
} from './transport-kit.service';

describe('transport-kit.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists transport kits with the TransportKit contract', async () => {
    const contract: TransportKit[] = [
      { id: 'kit-1', serial_number: 'KIT-001', is_allocated: false, courier_id: null },
    ];
    mock.onGet('/transport-kits/').reply(200, contract);
    const response = await listTransportKits();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<TransportKit[]>();
  });

  it('creates a transport kit successfully', async () => {
    const payload: TransportKitCreate = { serial_number: 'KIT-001', is_allocated: false, courier_id: null };
    const contract: TransportKit = {
      id: 'kit-1',
      serial_number: 'KIT-001',
      is_allocated: false,
      courier_id: null,
    };
    mock.onPost('/transport-kits/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });
    const response = await createTransportKit(payload);
    expect(response).toEqual(contract);
  });

  it('updates a transport kit successfully', async () => {
    const payload: TransportKitUpdate = { is_allocated: true, courier_id: 'courier-1' };
    const contract: TransportKit = {
      id: 'kit-1',
      serial_number: 'KIT-001',
      is_allocated: true,
      courier_id: 'courier-1',
    };
    mock.onPatch('/transport-kits/kit-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });
    const response = await updateTransportKit('kit-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/transport-kits/missing-kit').reply(404, { detail: 'Transport kit not found' });
    await expect(getTransportKit('missing-kit')).rejects.toMatchObject({
      status: 404,
      message: 'Transport kit not found',
      details: 'Transport kit not found',
    });
  });

  it('deletes a transport kit and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Transport kit deleted successfully' };
    mock.onDelete('/transport-kits/kit-1').reply(200, contract);
    const response = await deleteTransportKit('kit-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});