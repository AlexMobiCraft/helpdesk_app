import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';

// Типизация данных для входа (соответствует FastAPI ожиданиям - FormData)
interface LoginCredentials {
  username: string;
  password: string;
}

// Типизация ответа API при успешном входе
interface LoginResponse {
  access_token: string;
  token_type: string;
}

// Функция для выполнения запроса на вход
const loginUser = async (credentials: LoginCredentials): Promise<LoginResponse> => {
  const formData = new URLSearchParams();
  formData.append('username', credentials.username);
  formData.append('password', credentials.password);

  // Исправляем путь на /api/auth/login
  const { data } = await api.post<LoginResponse>('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return data;
};

// Хук мутации для входа
export function useLoginMutation() {
  const queryClient = useQueryClient();
  const router = useRouter();

  // Первый аргумент - функция мутации, второй - объект опций
  return useMutation<LoginResponse, Error, LoginCredentials>({
    mutationFn: loginUser, // Передаем функцию мутации сюда
    onSuccess: async (data: LoginResponse) => {
      // Сохраняем токен и перенаправляем на страницу пользователя
      localStorage.setItem('access_token', data.access_token);
      queryClient.invalidateQueries({ queryKey: ['user', 'me'] });
      router.push('/user');
    },
    onError: (error: Error) => { // Явно типизируем error
      // Обработка ошибок (можно вывести уведомление)
      console.error('Login failed:', error);
      // Очистка токена в случае ошибки (на всякий случай)
      localStorage.removeItem('access_token');
    },
  });
}
