// Хук и функции для аутентификации и получения текущего пользователя
import { useEffect, useState } from 'react';
import { apiFetch } from './api';

export function getToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

export function setToken(token: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem('access_token', token);
}

export function removeToken() {
  if (typeof window === 'undefined') return;
  localStorage.removeItem('access_token');
}

export function useCurrentUser() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = getToken();
    if (!token) {
      setLoading(false);
      setUser(null);
      return;
    }
    apiFetch('/api/users/me')
      .then(setUser)
      .catch((err) => {
        setError('Ошибка авторизации');
        removeToken();
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  return { user, loading, error };
}
