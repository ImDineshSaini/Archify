import axios from 'axios';

const API_BASE_URL = '/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials) => api.post('/v2/auth/login', credentials),
  register: (userData) => api.post('/v2/auth/register', userData),
};

// Repository API
export const repositoryAPI = {
  list: () => api.get('/repositories/'),  // Add trailing slash
  get: (id) => api.get(`/repositories/${id}`),
  create: (data) => api.post('/repositories/', data),  // Add trailing slash
  delete: (id) => api.delete(`/repositories/${id}`),
};

// Analysis API
export const analysisAPI = {
  list: (repositoryId = null) => {
    const params = repositoryId ? { repository_id: repositoryId } : {};
    return api.get('/analyses/', { params });  // Add trailing slash
  },
  get: (id) => api.get(`/analyses/${id}`),
  create: (data) => api.post('/analyses/', data),  // Add trailing slash
  delete: (id) => api.delete(`/analyses/${id}`),
};

// Settings API
export const settingsAPI = {
  list: () => api.get('/settings/'),  // Add trailing slash
  configureLLM: (config) => api.put('/settings/llm-provider', config),
  configureGit: (config) => api.put('/settings/git-config', config),
  getCurrentLLM: () => api.get('/settings/current-llm-provider'),
};

export default api;
