"use client";

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import Link from 'next/link';
import {
  Table, TableHead, TableRow, TableCell, TableBody,
  TableContainer, Paper, Button, Box
} from '@mui/material';
import { AxiosResponse } from 'axios';

interface Device {
  device_id: number;
  name: string;
  inventory_number?: string;
  device_type?: { name: string };
}

export default function DeviceList({ devices }: { devices: Device[] }) {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const deleteMutation = useMutation<AxiosResponse<any, any>, Error, number>({
    mutationFn: (id: number) => api.delete(`/api/v1/devices/admin/devices/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['admin-devices'] }),
  });

  const handleDelete = (id: number) => {
    if (confirm(t('devices.delete') + '?')) deleteMutation.mutate(id);
  };

  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>{t('devices.id')}</TableCell>
            <TableCell>{t('devices.name')}</TableCell>
            <TableCell>{t('devices.type')}</TableCell>
            <TableCell>{t('devices.inventoryNumber')}</TableCell>
            <TableCell>{t('devices.actions')}</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {devices.map((dev, idx) => (
            <TableRow key={dev.device_id}>
              <TableCell>{dev.device_id}</TableCell>
              <TableCell>{dev.name}</TableCell>
              <TableCell>{dev.device_type?.name || '-'}</TableCell>
              <TableCell>{dev.inventory_number || '-'}</TableCell>
              <TableCell>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Link href={`/admin/devices/edit/${dev.device_id}`} passHref>
                    <Button size="small" variant="outlined">{t('devices.edit')}</Button>
                  </Link>
                  <Button
                    size="small"
                    variant="outlined"
                    color="error"
                    onClick={() => handleDelete(dev.device_id)}
                    disabled={deleteMutation.status === 'pending'}
                  >
                    {t('devices.delete')}
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
