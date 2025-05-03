'use client';

import React from 'react';
import { useMutation, useQueryClient, useIsMutating } from '@tanstack/react-query';
import api from '@/api/axios';
import { Table, TableHead, TableRow, TableCell, TableBody, IconButton } from '@mui/material';
import { Edit, Delete } from '@mui/icons-material';
import Link from 'next/link';
import { useTranslation } from 'react-i18next';

interface Priority { id: number; name: string; description?: string; display_order: number; }
interface Props { priorities: Priority[] }

/**
 * Шаг 4: Компонент PriorityList (выполнено)
 */
export default function PriorityList({ priorities }: Props) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/api/v1/priorities/admin/priorities/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-priorities'] }),
  });
  const isMutating = useIsMutating({ mutationKey: ['admin-priorities'] }) > 0;

  return (
    <Table>
      <TableHead>
        <TableRow>
          <TableCell>{t('priorities.name')}</TableCell>
          <TableCell>{t('priorities.order')}</TableCell>
          <TableCell>{t('priorities.actions')}</TableCell>
        </TableRow>
      </TableHead>
      <TableBody>
        {priorities.map((p, idx) => (
          <TableRow key={`priority-${p.id ?? idx}`}>
            <TableCell>{p.name}</TableCell>
            <TableCell>{p.display_order}</TableCell>
            <TableCell>
              <Link href={`/admin/priorities/edit/${p.id}`} passHref>
                <IconButton><Edit /></IconButton>
              </Link>
              <IconButton onClick={() => deleteMutation.mutate(p.id)} disabled={isMutating}>
                <Delete />
              </IconButton>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
