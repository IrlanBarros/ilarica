import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type { ApiMessageResponse, Canteen, CanteenCreate, CanteenUpdate } from '../types';
import {
  createCanteen,
  deleteCanteen,
  getCanteen,
  listCanteens,
  updateCanteen,
} from './canteen.service';

describe('canteen.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists canteens with the Canteen contract', async () => {
    const contract: Canteen[] = [
      {
        id: 'canteen-1',
        user_id: 'user-1',
        name: 'Cantina Central',
        location: 'Campus Juazeiro',
        is_open: true,
        products: [],
      },
    ];

    mock.onGet('/canteens/').reply(200, contract);

    const response = await listCanteens();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Canteen[]>();
  });

  it('creates a canteen successfully', async () => {
    const payload: CanteenCreate = {
      name: 'Cantina Central',
      location: 'Campus Juazeiro',
      user_id: 'user-1',
      is_open: true,
    };
    const contract: Canteen = {
      id: 'canteen-1',
      name: 'Cantina Central',
      location: 'Campus Juazeiro',
      user_id: 'user-1',
      is_open: true,
      products: [],
    };

    mock.onPost('/canteens/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await createCanteen(payload);
    expect(response).toEqual(contract);
  });

  it('updates a canteen successfully', async () => {
    const payload: CanteenUpdate = {
      name: 'Cantina do Bloco B',
      location: 'Bloco B - Campus Juazeiro',
      is_open: false,
    };
    const contract: Canteen = {
      id: 'canteen-1',
      user_id: 'user-1',
      name: 'Cantina do Bloco B',
      location: 'Bloco B - Campus Juazeiro',
      is_open: false,
      products: [],
    };

    mock.onPatch('/canteens/canteen-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });

    const response = await updateCanteen('canteen-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/canteens/missing-canteen').reply(404, { detail: 'Canteen not found' });

    await expect(getCanteen('missing-canteen')).rejects.toMatchObject({
      status: 404,
      message: 'Canteen not found',
      details: 'Canteen not found',
    });
  });

  it('deletes a canteen and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Canteen deleted successfully' };
    mock.onDelete('/canteens/canteen-1').reply(200, contract);
    const response = await deleteCanteen('canteen-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});
