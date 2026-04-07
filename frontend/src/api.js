import axios from 'axios';

// Use environment variable for API URL in production, default to relative path for local dev
const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('authToken');
  if (token && !config.url?.includes('?')) {
    // Add token as query parameter if not already present
    config.url = config.url?.includes('?') 
      ? `${config.url}&token=${token}` 
      : `${config.url}?token=${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
