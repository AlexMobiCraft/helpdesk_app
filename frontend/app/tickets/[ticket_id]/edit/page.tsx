'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useTranslation } from 'react-i18next';
import { Box, Button, TextField, Typography, FormControl, InputLabel, Select, MenuItem, CircularProgress, Alert } from '@mui/material';
import Link from 'next/link';

export default function EditTicketPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const { ticket_id } = useParams();
  const queryClient = useQueryClient();

  const [deviceId, setDeviceId] = useState('');
  const [description, setDescription] = useState('');
  const [formError, setFormError] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const { data: ticket, isLoading: loadingTicket, error: ticketError } = useQuery({
    queryKey: ['ticket', ticket_id!],
    queryFn: () => api.get(`/api/v1/tickets/${ticket_id}`).then(res => res.data),
  });
  const { data: devices, isLoading: loadingDevices, error: devicesError } = useQuery({
    queryKey: ['devices'],
    queryFn: () => api.get('/api/v1/devices').then(res => res.data),
  });

  useEffect(() => {
    if (ticket) {
      setDeviceId(String(ticket.device_id));
      setDescription(ticket.description);
    }
  }, [ticket]);

  const mutation = useMutation({
    mutationFn: (updateData: any) => api.patch(`/api/v1/tickets/${ticket_id}`, updateData).then(res => res.data),
    onSuccess: async (data) => {
      if (selectedFiles.length > 0) {
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        try {
          const uploadResp = await api.post(`/api/v1/tickets/${ticket_id}/files`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
          });
          // не обрабатывать uploadResp, только загружаем
        } catch (uploadError: any) {
          setFormError(uploadError instanceof Error ? uploadError.message : t('tickets.error'));
          return;
        }
      }
      // получить свежие данные тикета и обновить кэш
      try {
        const fresh = await api.get(`/api/v1/tickets/${ticket_id}`).then(res => res.data);
        queryClient.setQueryData(['ticket', ticket_id!], fresh);
      } catch {}
      router.push(`/tickets/${ticket_id}`);
    },
    onError: (error: any) => setFormError(error instanceof Error ? error.message : t('tickets.error')),
  });

  const deleteFileMutation = useMutation({
    mutationFn: (fileId: number) => api.delete(`/api/v1/tickets/${ticket_id}/files/${fileId}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['ticket', ticket_id!] }),
    onError: (error: any) => setFormError(error instanceof Error ? error.message : t('tickets.error')),
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    mutation.mutate({ device_id: parseInt(deviceId, 10), description });
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  if (loadingTicket || loadingDevices) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if (ticketError || devicesError) return <Alert severity="error">{t('tickets.error')}</Alert>;

  return (
    <Box maxWidth={600} mx="auto" mt={4}>
      <Typography variant="h5" gutterBottom>{t('tickets.edit')}</Typography>
      <form onSubmit={handleSubmit}>
        <FormControl fullWidth margin="normal">
          <InputLabel id="device-label">{t('tickets.table.device')}</InputLabel>
          <Select
            labelId="device-label"
            value={deviceId}
            label={t('tickets.table.device')}
            onChange={e => setDeviceId(e.target.value as string)}
            required
          >
            {devices.map((d: any) => (
              <MenuItem key={d.device_id} value={d.device_id}>{d.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          fullWidth
          margin="normal"
          label={t('tickets.table.description')}
          multiline
          minRows={3}
          value={description}
          onChange={e => setDescription(e.target.value)}
          required
        />
        {formError && <Alert severity="error" sx={{ mt: 2 }}>{formError}</Alert>}
        {ticket.files && ticket.files.length > 0 && (
          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1">{t('tickets.files')}:</Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
              {ticket.files.map((file: any) => (
                <Box key={file.file_id} sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {file.file_type.startsWith('image/') ? (
                    <Box
                      component="img"
                      src={`${process.env.NEXT_PUBLIC_API_BASE_URL}/uploads/${file.file_path}`}
                      alt={file.file_name}
                      sx={{ width: 150, height: 'auto', mb: 1 }}
                    />
                  ) : file.file_type.startsWith('video/') ? (
                    <Box
                      component="video"
                      src={`${process.env.NEXT_PUBLIC_API_BASE_URL}/uploads/${file.file_path}`}
                      controls
                      sx={{ width: 200, mb: 1 }}
                    />
                  ) : null}
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Link href={`${process.env.NEXT_PUBLIC_API_BASE_URL}/uploads/${file.file_path}`} target="_blank" rel="noopener noreferrer">
                      {file.file_name}
                    </Link>
                    <Button variant="text" color="error" size="small" disabled={deleteFileMutation.status === 'pending'} onClick={() => deleteFileMutation.mutate(file.file_id)}>
                      {t('tickets.deleteFile')}
                    </Button>
                  </Box>
                </Box>
              ))}
            </Box>
          </Box>
        )}
        <Button variant="outlined" component="label" fullWidth sx={{ mt: 2 }}>
          {t('tickets.uploadFiles')}
          <input type="file" hidden multiple accept="image/*,video/*" onChange={handleFileChange} />
        </Button>
        {selectedFiles.map(file => (
          <Typography variant="body2" key={file.name}>{file.name}</Typography>
        ))}
        <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
          <Button variant="contained" type="submit" disabled={mutation.status === 'pending'}>
            {mutation.status === 'pending' ? <CircularProgress size={24} /> : t('tickets.edit')}
          </Button>
          <Button variant="outlined" onClick={() => router.push(`/tickets/${ticket_id}`)}>{t('back')}</Button>
        </Box>
      </form>
    </Box>
  );
}
