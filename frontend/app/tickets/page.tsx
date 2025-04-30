'use client';

import React from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery } from '@tanstack/react-query';
import api from '@/api/axios';
import { CircularProgress, Typography, Table, TableHead, TableRow, TableCell, TableBody, Button, TableContainer, Paper, Box } from '@mui/material';
import Link from 'next/link';

export default function TicketsPage() {
  const { t } = useTranslation();
  const { data, isLoading, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => api.get('/api/v1/tickets').then(res => res.data),
  });

  if (isLoading) return <CircularProgress />;
  if (error) return <Typography color="error">Ошибка загрузки заявок</Typography>;

  return (
    <div>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h4" gutterBottom>Список заявок</Typography>
        <Link href="/tickets/new" passHref>
          <Button variant="contained" color="primary">{t('tickets.new')}</Button>
        </Link>
      </Box>
      <TableContainer component={Paper} sx={{ mb: 2 }}>
        <Table sx={{ minWidth: 650 }} aria-label="tickets table">
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Устройство</TableCell>
              <TableCell>Пользователь</TableCell>
              <TableCell>Описание</TableCell>
              <TableCell>Приоритет</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Дата создания</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.map((ticket: any) => (
              <TableRow key={ticket.ticket_id}>
                <TableCell>{ticket.ticket_id}</TableCell>
                <TableCell>{ticket.device?.name || ticket.device_id}</TableCell>
                <TableCell>{ticket.user?.username || ticket.user_id}</TableCell>
                <TableCell>{ticket.description}</TableCell>
                <TableCell>{ticket.priority?.name || ticket.priority_id}</TableCell>
                <TableCell>{ticket.status?.name || ticket.status_id}</TableCell>
                <TableCell>{new Date(ticket.created_at).toLocaleString()}</TableCell>
                <TableCell>
                  <Link href={`/tickets/${ticket.ticket_id}`} passHref>
                    <Button variant="outlined">Подробнее</Button>
                  </Link>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
}
