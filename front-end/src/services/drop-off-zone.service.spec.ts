import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  DropOffZone,
  DropOffZoneCreate,
  DropOffZoneUpdate,
} from '../types';
import {
  createDropOffZone,
  deleteDropOffZone,
  getDropOffZone,
  listDropOffZones,
  updateDropOffZone,
} from './drop-off-zone.service';

describe('drop-off-zone.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists drop-off zones with the DropOffZone contract', async () => {
    const contract: DropOffZone[] = [
      { id: 'zone-1', name: 'Bloco A', capacity_total: 20, current_load: 0, is_active: true },
    ];
    mock.onGet('/drop-off-zones/').reply(200, contract);
    const response = await listDropOffZones();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<DropOffZone[]>();
  });

  it('creates a drop-off zone successfully', async () => {
    const payload: DropOffZoneCreate = { name: 'Bloco A', capacity_total: 20, current_load: 0, is_active: true };
    const contract: DropOffZone = {
      id: 'zone-1',
      name: 'Bloco A',
      capacity_total: 20,
      current_load: 0,
      is_active: true,
    };
    mock.onPost('/drop-off-zones/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });
    const response = await createDropOffZone(payload);
    expect(response).toEqual(contract);
  });

  it('updates a drop-off zone successfully', async () => {
    const payload: DropOffZoneUpdate = { is_active: false, capacity_total: 15 };
    const contract: DropOffZone = { id: 'zone-1', name: 'Bloco A', capacity_total: 15, current_load: 0, is_active: false };
    mock.onPatch('/drop-off-zones/zone-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });
    const response = await updateDropOffZone('zone-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/drop-off-zones/missing-zone').reply(404, { detail: 'Drop-off zone not found' });
    await expect(getDropOffZone('missing-zone')).rejects.toMatchObject({
      status: 404,
      message: 'Drop-off zone not found',
      details: 'Drop-off zone not found',
    });
  });

  it('deletes a drop-off zone and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Drop-off zone deleted successfully' };
    mock.onDelete('/drop-off-zones/zone-1').reply(200, contract);
    const response = await deleteDropOffZone('zone-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});