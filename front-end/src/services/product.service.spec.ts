import MockAdapter from 'axios-mock-adapter';
import { beforeEach, describe, expect, expectTypeOf, it } from 'vitest';

import { apiClient } from '../api';
import {
  createProduct,
  deleteProduct,
  getProduct,
  listProducts,
  updateProduct,
} from './product.service';
import type { ApiMessageResponse, Product, ProductCreate, ProductUpdate } from '../types';

describe('product.service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(apiClient);
  });

  it('lists products with the Product contract', async () => {
    const contract: Product[] = [
      {
        id: 'product-1',
        name: 'Sandwich',
        description: 'Natural sandwich',
        price: '12.50',
        is_active: true,
        canteen_id: 'canteen-1',
        is_fast_stock_enabled: false,
      },
    ];

    mock.onGet('/products/').reply(200, contract);

    const response = await listProducts();

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Product[]>();
  });

  it('creates a product successfully', async () => {
    const payload: ProductCreate = {
      name: 'Juice',
      canteen_id: 'canteen-1',
      price: '6.00',
      description: 'Orange juice',
      is_active: true,
    };

    const contract: Product = {
      id: 'product-2',
      name: 'Juice',
      description: 'Orange juice',
      price: '6.00',
      is_active: true,
      canteen_id: 'canteen-1',
      is_fast_stock_enabled: false,
    };

    mock.onPost('/products/').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [201, contract];
    });

    const response = await createProduct(payload);

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<Product>();
  });

  it('updates a product successfully', async () => {
    const payload: ProductUpdate = {
      description: 'Updated orange juice',
      price: '6.50',
    };

    const contract: Product = {
      id: 'product-2',
      name: 'Juice',
      description: 'Updated orange juice',
      price: '6.50',
      is_active: true,
      canteen_id: 'canteen-1',
      is_fast_stock_enabled: false,
    };

    mock.onPatch('/products/product-2').reply((config) => {
      expect(JSON.parse(String(config.data))).toEqual(payload);
      return [200, contract];
    });

    const response = await updateProduct('product-2', payload);

    expect(response).toEqual(contract);
  });

  it('returns a normalized error when fetching a missing product', async () => {
    mock.onGet('/products/missing-product').reply(404, { detail: 'Product not found' });

    await expect(getProduct('missing-product')).rejects.toMatchObject({
      status: 404,
      message: 'Product not found',
      details: 'Product not found',
    });
  });

  it('deletes a product and returns the API message contract', async () => {
    const contract: ApiMessageResponse = {
      detail: 'Product deleted successfully',
    };

    mock.onDelete('/products/product-2').reply(200, contract);

    const response = await deleteProduct('product-2');

    expect(response).toEqual(contract);
    expectTypeOf(response).toEqualTypeOf<ApiMessageResponse>();
  });
});