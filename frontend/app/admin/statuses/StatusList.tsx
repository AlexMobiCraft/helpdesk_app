'use client';

import React from 'react';
import { useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import api from '@/api/axios';
import {
  Table, TableHead, TableRow, TableCell, TableBody, IconButton
} from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';

interface Status { id: number; name: string; description?: string }
interface Props { statuses: Status[] }

/**
 * Компонент отображения списка статусов
 * @param statuses - массив статусов для отображения
 */
export default function StatusList({ statuses }: Props) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/api/v1/statuses/admin/statuses/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-statuses'] }),
  });
  const isMutating = useIsMutating({ mutationKey: ['admin-statuses'] }) > 0;

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>{t('statuses.name')}</TableCell>
          <TableCell>{t('statuses.description')}</TableCell>
          <TableCell>{t('statuses.actions')}</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {statuses.map((s, idx) => (
          <TableRow key={`status-${s.id ?? idx}`}>
            <TableCell>{s.name}</TableCell>
            <TableCell>{s.description}</TableCell>
            <TableCell>
              <Link href={`/admin/statuses/edit/${s.id}`} passHref>
                <IconButton><Edit /></IconButton>
              </Link>
              <IconButton
                onClick={() => deleteMutation.mutate(s.id)}
                disabled={isMutating}
              >
                <Delete />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
