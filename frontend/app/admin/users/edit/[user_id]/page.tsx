'use client'

import React from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, UseQueryOptions } from '@tanstack/react-query';
import { Box, CircularProgress, Alert } from '@mui/material';
import api from "@/api/axios";
import EditUserForm from "./EditUserForm";

interface User {
  user_id: number;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role_id: number;
  role?: { id: number; name: string };
}

export default function EditUserPage() {
  const router = useRouter();
  const { user_id } = useParams() as { user_id: string };
  const { data: user, isLoading, error } = useQuery<User, Error>({
    queryKey: ['admin-user', user_id],
    queryFn: () => api.get(`/api/v1/users/admin/users/${user_id}`).then(res => res.data),
  });
  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if (error) return <Alert severity="error">Ошибка при загрузке пользователя</Alert>;
  return <EditUserForm user={user!} userId={user_id!} />;
}
