'use client';

import React, { useEffect } from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Button, 
  CircularProgress, 
  TableContainer, 
  Paper, 
  Table, 
  TableHead, 
  TableRow, 
  TableCell, 
  TableBody, 
  IconButton, 
  Box, 
  FormControl, 
  Select, 
  MenuItem 
} from '@mui/material';
import LogoutIcon from '@mui/icons-material/Logout';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useCurrentUser } from '@/hooks/useUser';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

export default function UserPage() {
  const router = useRouter();
  const { t, i18n } = useTranslation();
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/login');
  };

  const { data, isLoading, error } = useQuery({
    queryKey: ['tickets'],
    queryFn: () => api.get('/api/v1/tickets').then(res => res.data),
  });
  const { data: currentUser, isLoading: userLoading } = useCurrentUser();
  const queryClient = useQueryClient();
  const { mutate: deleteTicket, status: deleteStatus } = useMutation({
    mutationFn: (id: number) => api.delete(`/api/v1/tickets/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tickets'] }),
  });
  const tickets = data ? data.filter((t: any) => !t.status.is_final) : [];

  useEffect(() => {
    console.log('CurrentUser:', currentUser);
    console.log('userLoading:', userLoading);
    console.log('Tickets:', tickets);
  }, [currentUser, userLoading, tickets]);

  return (
    <>
      <AppBar position="static" color="primary">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {t('header.title')}
          </Typography>
          <FormControl variant="standard" size="small" sx={{ mr: 2 }}>
            <Select value={i18n.language} onChange={(e) => i18n.changeLanguage(e.target.value as string)}>
              <MenuItem value="ru">Русский</MenuItem>
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="sl">Slovenščina</MenuItem>
            </Select>
          </FormControl>
          <IconButton color="inherit" onClick={handleLogout} aria-label={t('header.logout')}>
            <LogoutIcon />
          </IconButton>
        </Toolbar>
      </AppBar>
      <Container maxWidth="md" sx={{ mt: 4 }}>
        {/* Таблица незавершённых заявок */}
        {isLoading ? (
          <CircularProgress />
        ) : error ? (
          <Typography color="error">{t('tickets.error')}</Typography>
        ) : (
          <>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 4, mb: 2 }}>
              <Typography variant="h5">{t('tickets.myTasks')}</Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                {currentUser?.role_id === 1 && (
                  <Link href="/admin" passHref>
                    <Button variant="outlined" size="small">{t('tickets.additional')}</Button>
                  </Link>
                )}
                <Link href="/tickets/new" passHref>
                  <Button variant="contained" color="primary">{t('tickets.new')}</Button>
                </Link>
              </Box>
            </Box>
            <TableContainer component={Paper}>
              <Table sx={{ minWidth: 650 }} aria-label="tickets table">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('tickets.table.no')}</TableCell>
                    <TableCell>{t('tickets.table.device')}</TableCell>
                    <TableCell>{t('tickets.table.description')}</TableCell>
                    <TableCell>{t('tickets.table.priority')}</TableCell>
                    <TableCell>{t('tickets.table.status')}</TableCell>
                    <TableCell>{t('tickets.table.createdAt')}</TableCell>
                    <TableCell>{t('tickets.table.action')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {tickets.map((ticket: any) => (
                    <TableRow key={ticket.ticket_id}>
                      <TableCell>{ticket.ticket_id}</TableCell>
                      <TableCell>{ticket.device?.name || ticket.device_id}</TableCell>
                      <TableCell>{ticket.description}</TableCell>
                      <TableCell>{ticket.priority?.name || ticket.priority_id}</TableCell>
                      <TableCell>{ticket.status?.name || ticket.status_id}</TableCell>
                      <TableCell>{new Intl.DateTimeFormat(i18n.language, { dateStyle: 'short', timeStyle: 'short' }).format(new Date(ticket.created_at))}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Link href={`/tickets/${ticket.ticket_id}`} passHref>
                            <Button variant="outlined" size="small">{t('tickets.details')}</Button>
                          </Link>
                          <Button
                            variant="outlined"
                            color="error"
                            size="small"
                            disabled={
                              userLoading || deleteStatus === 'pending' || !(
                                currentUser && (
                                  currentUser.role_id === 1 ||
                                  ticket.user_id === currentUser.user_id
                                )
                              )
                            }
                            onClick={() => deleteTicket(ticket.ticket_id)}
                          >
                            {t('tickets.deleteTicket')}
                          </Button>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </>
        )}
      </Container>
    </>
  );
}
