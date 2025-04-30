'use client';

import React, { useState, useEffect } from 'react';
import { Box, Button, TextField, Typography, Paper, Alert, FormControl, Select, MenuItem, InputAdornment, IconButton } from '@mui/material';
import Visibility from '@mui/icons-material/Visibility';
import VisibilityOff from '@mui/icons-material/VisibilityOff';
import { useLoginMutation } from '@/hooks/useAuth'; // Импортируем хук
import { useTranslation } from 'react-i18next';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { i18n, t } = useTranslation();
  const [currentLang, setCurrentLang] = useState(i18n.language);

  useEffect(() => {
    setCurrentLang(i18n.language);
  }, [i18n.language]);

  // Используем хук мутации
  const loginMutation = useLoginMutation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    // Вызываем мутацию с данными пользователя
    loginMutation.mutate({ username, password });
  };

  return (
    <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh" sx={{ position: 'relative' }}>
      <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
        <FormControl variant="standard" size="small">
          <Select
            value={currentLang}
            onChange={(e) => {
              const lang = e.target.value as string;
              i18n.changeLanguage(lang);
              setCurrentLang(lang);
            }}
          >
            <MenuItem value="ru">Русский</MenuItem>
            <MenuItem value="en">English</MenuItem>
            <MenuItem value="sl">Slovenščina</MenuItem>
          </Select>
        </FormControl>
      </Box>
      <Paper elevation={3} sx={{ p: 4, minWidth: 320 }}>
        <Typography variant="h5" gutterBottom align="center">
          {t('login.title')}
        </Typography>
        <form onSubmit={handleSubmit}>
          <TextField
            label={t('login.username')}
            fullWidth
            margin="normal"
            value={username}
            onChange={e => setUsername(e.target.value)}
            required
          />
          <TextField
            label={t('login.password')}
            fullWidth
            margin="normal"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={e => setPassword(e.target.value)}
            required
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton onClick={() => setShowPassword(!showPassword)} edge="end">
                    {showPassword ? <VisibilityOff /> : <Visibility />}
                  </IconButton>
                </InputAdornment>
              )
            }}
          />
          {/* Отображаем ошибку из состояния мутации */}
          {loginMutation.status === 'error' && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {loginMutation.error instanceof Error ? loginMutation.error.message : t('login.error')}
            </Alert>
          )}
          <Button
            type="submit"
            variant="contained"
            color="primary"
            fullWidth
            sx={{ mt: 2 }}
            // Блокируем кнопку во время выполнения мутации
            disabled={loginMutation.status === 'pending'}
          >
            {/* Меняем текст кнопки в зависимости от состояния мутации */}
            {loginMutation.status === 'pending' ? t('login.loading') : t('login.submit')}
          </Button>
        </form>
      </Paper>
    </Box>
  );
}
