import axios from 'axios';

// Получаем базовый URL API из переменных окружения
// По умолчанию используем префикс /api для проксирования запросов через Next.js
const baseURL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: baseURL, // Меняется через .env.local
  withCredentials: true, // Важно для работы с httpOnly cookies, если они используются
});

// Регистрация интерсепторов только в клиентской среде
if (typeof window !== 'undefined') {
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  // Автоматический выход при 401 Unauthorized
  api.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response?.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
      return Promise.reject(error);
    }
  );
}

export default api;
