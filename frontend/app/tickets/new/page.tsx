'use client';

import React, { useState } from 'react';
import { Box, Button, TextField, Typography, FormControl, InputLabel, Select, MenuItem, CircularProgress, Alert } from '@mui/material';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useRouter } from 'next/navigation';

export default function NewTicketPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: devices, isLoading: devLoading, error: devError } = useQuery({
    queryKey: ['devices'],
    queryFn: () => api.get('/api/v1/devices').then(res => res.data)
  });
  const { data: priorities, isLoading: priLoading, error: priError } = useQuery({
    queryKey: ['priorities'],
    queryFn: () => api.get('/api/v1/priorities').then(res => res.data)
  });

  const [deviceId, setDeviceId] = useState('');
  const [description, setDescription] = useState('');
  const [priorityId, setPriorityId] = useState('');
  const [formError, setFormError] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFiles(Array.from(e.target.files));
    }
  };

  const createMutation = useMutation({
    mutationFn: (newTicket: any) => api.post('/api/v1/tickets', newTicket).then(res => res.data),
    onSuccess: async (data) => {
      queryClient.invalidateQueries({ queryKey: ['tickets'] });
      if (selectedFiles.length > 0) {
        const formData = new FormData();
        selectedFiles.forEach(file => formData.append('files', file));
        try {
          await api.post(`/api/v1/tickets/${data.ticket_id}/files`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });
        } catch (error: any) {
          setFormError(error instanceof Error ? error.message : t('tickets.error'));
          return;
        }
      }
      router.push(`/tickets/${data.ticket_id}`);
    },
    onError: (error: any) => {
      setFormError(error instanceof Error ? error.message : t('tickets.error'));
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    createMutation.mutate({
      device_id: parseInt(deviceId, 10),
      description,
      priority_id: parseInt(priorityId, 10)
    });
  };

  if (devLoading || priLoading) return <CircularProgress />;
  if (devError || priError) return <Alert severity="error">{t('tickets.error')}</Alert>;

  return (
    <Box maxWidth={600} mx="auto" mt={4}>
      <Typography variant="h5" gutterBottom>{t('tickets.new')}</Typography>
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
          label={t('tickets.description')}
          multiline
          minRows={3}
          value={description}
          onChange={e => setDescription(e.target.value)}
          required
        />
        <FormControl fullWidth margin="normal">
          <InputLabel id="priority-label">{t('tickets.table.priority')}</InputLabel>
          <Select
            labelId="priority-label"
            value={priorityId}
            label={t('tickets.table.priority')}
            onChange={e => setPriorityId(e.target.value as string)}
            required
          >
            {priorities.map((p: any) => (
              <MenuItem key={p.priority_id} value={p.priority_id}>{p.name}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <Button variant="outlined" component="label" fullWidth sx={{ mt: 2 }}>
          {t('tickets.uploadFiles')}
          <input
            type="file"
            hidden
            multiple
            accept="image/*,video/*"
            capture
            onChange={handleFileChange}
          />
        </Button>
        {selectedFiles.map(file => (
          <Typography variant="body2" key={file.name}>{file.name}</Typography>
        ))}
        {formError && <Alert severity="error" sx={{ mt: 2 }}>{formError}</Alert>}
        <Button
          type="submit"
          variant="contained"
          color="primary"
          fullWidth
          sx={{ mt: 2 }}
          disabled={createMutation.status === 'pending'}
        >
          {createMutation.status === 'pending' ? <CircularProgress size={24} /> : t('tickets.submit')}
        </Button>
      </form>
    </Box>
  );
}
