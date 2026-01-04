/**
 * Tests for API service
 *
 * Tests the API client with Authorization headers
 */

import { api } from '../../services/api';
import * as secureStorage from '../../services/secureStorage';

// Mock secureStorage
jest.mock('../../services/secureStorage', () => ({
  getTokens: jest.fn(),
  saveTokens: jest.fn(),
  clearTokens: jest.fn(),
}));

// Mock fetch
global.fetch = jest.fn();

describe('ApiClient', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockReset();
  });

  describe('getAuthHeaders', () => {
    it('should include Authorization header when token exists', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({
        accessToken: 'test-token',
        refreshToken: 'refresh-token',
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'test' }),
      });

      await api.get('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer test-token',
          }),
        })
      );
    });

    it('should not include Authorization header when no token', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({
        accessToken: null,
        refreshToken: null,
      });

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ data: 'test' }),
      });

      await api.get('/test');

      const [, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(options.headers['Authorization']).toBeUndefined();
    });
  });

  describe('get', () => {
    it('should make GET request with correct URL', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: null });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ id: 1, name: 'Test' }),
      });

      const result = await api.get('/api/users');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/users'),
        expect.objectContaining({ method: 'GET' })
      );
      expect(result).toEqual({ id: 1, name: 'Test' });
    });

    it('should throw error on non-ok response', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: null });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 404,
      });

      await expect(api.get('/api/notfound')).rejects.toThrow('API Error: 404');
    });
  });

  describe('post', () => {
    it('should make POST request with JSON body', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: 'token' });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      });

      const data = { email: 'test@test.com', password: 'secret' };
      await api.post('/api/auth/login', data);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/auth/login'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(data),
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should throw error on failed POST', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: null });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 401,
      });

      await expect(api.post('/api/auth/login', {})).rejects.toThrow('API Error: 401');
    });
  });

  describe('put', () => {
    it('should make PUT request with JSON body', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: 'token' });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ updated: true }),
      });

      const data = { name: 'Updated Name' };
      await api.put('/api/users/1', data);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/users/1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(data),
        })
      );
    });
  });

  describe('delete', () => {
    it('should make DELETE request', async () => {
      (secureStorage.getTokens as jest.Mock).mockResolvedValue({ accessToken: 'token' });
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ deleted: true }),
      });

      await api.delete('/api/users/1');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/users/1'),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });
});
