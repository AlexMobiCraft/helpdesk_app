import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';

// Примерная типизация данных пользователя (должна соответствовать API)
interface UserProfile {
  user_id: number;
  username: string;
  email: string;
  full_name: string | null;
  role_id: number; // 1 = admin, прочие = пользователь
  is_active: boolean;
  // Добавьте другие поля профиля
}

// Функция для получения данных текущего пользователя
const fetchCurrentUser = async (): Promise<UserProfile> => {
  const { data } = await api.get<UserProfile>('/api/v1/users/me');
  return data;
};

// Хук для получения данных текущего пользователя
export function useCurrentUser() {
  // Передаем queryKey, queryFn и options в одном объекте
  return useQuery<UserProfile, Error>({
    queryKey: ['user', 'me'], 
    queryFn: fetchCurrentUser,
    // Опции
    staleTime: 1000 * 60 * 5, // кэш свежий 5 минут
    retry: 1, // 1 повтор при ошибке
    refetchOnMount: 'always',
    refetchOnWindowFocus: false,
  });
}
