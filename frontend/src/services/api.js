import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Attach the JWT access token to every request when present.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sb_access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Central 401 handling: clear the stale token and let the app react.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('sb_access_token');
    }
    return Promise.reject(error);
  }
);

export default api;
