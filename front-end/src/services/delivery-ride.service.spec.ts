import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import type {
  ApiMessageResponse,
  DeliveryRide,
  DeliveryRideCreate,
  DeliveryRideUpdate,
} from '../types';
import {
  createDeliveryRide,
  deleteDeliveryRide,
  getDeliveryRide,
  listDeliveryRides,
  updateDeliveryRide,
} from './delivery-ride.service';

describe('delivery-ride.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists delivery rides with the DeliveryRide contract', async () => {
    const contract: DeliveryRide[] = [
      {
        id: 'ride-1',
        drop_off_zone_id: 'zone-1',
        status: 'draft',
        assigned_courier_id: null,
        is_arrived: false,
      },
    ];

    mock.onGet('/delivery-rides/').reply(200, contract);
    const response = await listDeliveryRides();
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<DeliveryRide[]>();
  });

  it('creates a delivery ride successfully', async () => {
    const payload: DeliveryRideCreate = {
      drop_off_zone_id: 'zone-1',
      status: 'draft',
      assigned_courier_id: null,
      is_arrived: false,
    };
    const contract: DeliveryRide = {
      id: 'ride-1',
      drop_off_zone_id: 'zone-1',
      status: 'draft',
      assigned_courier_id: null,
      is_arrived: false,
    };

    mock.onPost('/delivery-rides/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await createDeliveryRide(payload);
    expect(response).toEqual(contract);
  });

  it('updates a delivery ride successfully', async () => {
    const payload: DeliveryRideUpdate = { status: 'accepted', assigned_courier_id: 'courier-1' };
    const contract: DeliveryRide = {
      id: 'ride-1',
      drop_off_zone_id: 'zone-1',
      status: 'accepted',
      assigned_courier_id: 'courier-1',
      is_arrived: false,
    };

    mock.onPatch('/delivery-rides/ride-1').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });

    const response = await updateDeliveryRide('ride-1', payload);
    expect(response).toEqual(contract);
  });

  it('normalizes not-found errors', async () => {
    mock.onGet('/delivery-rides/missing-ride').reply(404, { detail: 'Delivery ride not found' });

    await expect(getDeliveryRide('missing-ride')).rejects.toMatchObject({
      status: 404,
      message: 'Delivery ride not found',
      details: 'Delivery ride not found',
    });
  });

  it('deletes a delivery ride and returns the API message contract', async () => {
    const contract: ApiMessageResponse = { detail: 'Delivery ride deleted successfully' };
    mock.onDelete('/delivery-rides/ride-1').reply(200, contract);
    const response = await deleteDeliveryRide('ride-1');
    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});