'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import api from '@/api/axios';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, Typography, Button, CircularProgress, Box, Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import Link from 'next/link';

interface TicketDetailType {
  ticket_id: number;
  description: string;
  created_at: string;
  updated_at?: string;
  resolution_notes?: string;
  user?: { user_id: number; username: string; first_name?: string; last_name?: string };
  assignments?: { assignment_id: number; technician_id: number; technician_name: string; technician_username: string; assigned_at: string }[];
  device: { name: string };
  priority: { name: string };
  status: { name: string };
  files?: { file_id: number; file_name: string; file_path: string; file_type: string }[];
  [key: string]: any;
}

export default function TicketDetailPage() {
  const router = useRouter();
  const { ticket_id } = useParams();
  const { t, i18n } = useTranslation();
  const queryClient = useQueryClient();

  useEffect(() => {
    if (ticket_id) {
      queryClient.invalidateQueries({ queryKey: ['ticket', ticket_id!] });
    }
  }, [ticket_id, queryClient]);

  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewSrc, setPreviewSrc] = useState<string | null>(null);
  const handleOpenPreview = (src: string) => { setPreviewSrc(src); setPreviewOpen(true); };
  const handleClosePreview = () => { setPreviewOpen(false); setPreviewSrc(null); };

  const { data: ticket, isLoading, error } = useQuery<TicketDetailType, Error>({
    queryKey: ['ticket', ticket_id!],
    queryFn: () => api.get(`/api/v1/tickets/${ticket_id}`).then(res => res.data),
    refetchOnMount: 'always',
    staleTime: 0,
  });

  if (isLoading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}><CircularProgress /></Box>;
  if (error) return <Typography color="error">{(error as Error).message}</Typography>;
  if (!ticket) return null;

  return (
    <Box sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
        <Button variant="outlined" onClick={() => router.push('/user')}>{t('back')}</Button>
        <Button variant="contained" onClick={() => router.push(`/tickets/${ticket_id}/edit`)}>{t('tickets.edit')}</Button>
      </Box>
      <Card>
        <CardContent>
          <Typography variant="h5" gutterBottom>
            <strong>{t('tickets.table.description')}:</strong> {ticket.description}
          </Typography>
          <Typography>
            <strong>{t('tickets.table.no')}:</strong> {ticket.ticket_id}
          </Typography>
          <Typography><strong>{t('tickets.table.device')}:</strong> {ticket.device.name}</Typography>
          <Typography><strong>{t('tickets.table.priority')}:</strong> {ticket.priority.name}</Typography>
          <Typography><strong>{t('tickets.table.status')}:</strong> {ticket.status.name}</Typography>
          <Typography><strong>{t('tickets.table.createdAt')}:</strong> {new Intl.DateTimeFormat(i18n.language, { dateStyle: 'full', timeStyle: 'short' }).format(new Date(ticket.created_at))}</Typography>
          {ticket.updated_at && (
            <Typography><strong>{t('tickets.updatedAt')}:</strong> {new Intl.DateTimeFormat(i18n.language, { dateStyle: 'full', timeStyle: 'short' }).format(new Date(ticket.updated_at))}</Typography>
          )}
          {ticket.resolution_notes && (
            <Typography><strong>{t('tickets.resolutionNotes')}:</strong> {ticket.resolution_notes}</Typography>
          )}
          {ticket.user && (
            <Typography><strong>{t('tickets.table.user')}:</strong> {ticket.user.first_name || ticket.user.username} {ticket.user.last_name || ''}</Typography>
          )}
          {ticket.assignments && ticket.assignments.length > 0 && (
            <Box sx={{ mt: 1 }}>
              <Typography variant="subtitle1" gutterBottom>{t('tickets.assignedTechnicians')}:</Typography>
              {ticket.assignments.map(assign => (
                <Typography key={assign.assignment_id}>{assign.technician_name}</Typography>
              ))}
            </Box>
          )}
          {ticket.files && ticket.files.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>{t('tickets.files')}:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {ticket.files.map((file: any) => {
                  const apiBase = typeof window !== 'undefined'
  ? `${window.location.protocol}//${window.location.hostname}:8000`
  : process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
const src = `${apiBase}/uploads/${file.file_path}`;
                  return file.file_type.startsWith('image/') ? (
                    <Box
                      component="img"
                      key={file.file_id}
                      src={src}
                      alt={file.file_name}
                      sx={{ width: 100, height: 'auto', cursor: 'pointer' }}
                      onClick={() => handleOpenPreview(src)}
                    />
                  ) : file.file_type.startsWith('video/') ? (
                    <Box
                      component="video"
                      key={file.file_id}
                      src={src}
                      controls
                      sx={{ width: 200 }}
                    />
                  ) : (
                    <Link
                      key={file.file_id}
                      href={src}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      {file.file_name}
                    </Link>
                  );
                })}
              </Box>
            </Box>
          )}
        </CardContent>
      </Card>
      <Dialog open={previewOpen} onClose={handleClosePreview} maxWidth="lg">
        <DialogTitle sx={{ m: 0, p: 2 }}>
          <IconButton
            aria-label="close"
            onClick={handleClosePreview}
            sx={{ position: 'absolute', right: 8, top: 8, color: (theme) => theme.palette.grey[500] }}
          >
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Box
            component="img"
            src={previewSrc!}
            alt="Preview"
            sx={{ width: '100%', height: 'auto' }}
          />
        </DialogContent>
      </Dialog>
    </Box>
  );
}
