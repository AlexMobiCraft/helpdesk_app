// Простой API-клиент для авторизованных запросов
export async function apiFetch(url: string, options: RequestInit = {}) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  const headers = {
    ...(options.headers || {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
  const response = await fetch(url, { ...options, headers });
  if (!response.ok) throw new Error('Ошибка запроса');
  return response.json();
}
