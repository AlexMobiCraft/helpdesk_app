'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import Link from 'next/link';
import { Table, TableHead, TableRow, TableCell, TableBody, TableContainer, Paper, Button, Box } from '@mui/material';
import { AxiosResponse } from 'axios';

interface Role {
  id: number;
  name: string;
  description?: string;
}

/**
 * Компонент отображения списка ролей с кнопками действий
 */
export default function RoleList({ roles }: { roles: Role[] }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const deleteMutation = useMutation<AxiosResponse<any>, Error, number>({
    mutationFn: (id: number) => api.delete(`/api/v1/users/admin/roles/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-roles'] }),
  });

  const handleDelete = (id: number) => {
    if (confirm(t('roles.delete') + '?')) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>#</TableCell>
            <TableCell>{t('roles.name')}</TableCell>
            <TableCell>{t('roles.description')}</TableCell>
            <TableCell>{t('roles.actions')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {roles.map((role, idx) => (
            <TableRow key={role.id}>
              <TableCell>{idx + 1}</TableCell>
              <TableCell>{role.name}</TableCell>
              <TableCell>{role.description || '-'}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Link href={`/admin/roles/edit/${role.id}`} passHref>
                    <Button size="small" variant="outlined">{t('roles.edit')}</Button>
                  </Link>
                  <Button
                    size="small"
                    variant="outlined"
                    color="error"
                    onClick={() => handleDelete(role.id)}
                    disabled={deleteMutation.status === 'pending'}
                  >
                    {t('roles.delete')}
                  </Button>
                </Box>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
