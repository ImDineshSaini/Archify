import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance for tenant operations
const tenantApi = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tenant API endpoints
export const tenantAPI = {
  create: (data) => tenantApi.post('/tenants/create', data),
  list: () => tenantApi.get('/tenants/'),  // Add trailing slash
  get: (id) => tenantApi.get(`/tenants/${id}`),
  update: (id, data) => tenantApi.put(`/tenants/${id}`, data),
  delete: (id) => tenantApi.delete(`/tenants/${id}`),
};

export default tenantApi;
