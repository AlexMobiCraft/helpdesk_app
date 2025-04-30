"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import api from "@/api/axios";
import {
  Box,
  Typography,
  TextField,
  Button,
  Alert,
  MenuItem,
  Select,
  FormControl,
  InputLabel,
  Stack,
  CircularProgress,
} from "@mui/material";
import KeyboardArrowUpIcon from "@mui/icons-material/KeyboardArrowUp";
import KeyboardArrowDownIcon from "@mui/icons-material/KeyboardArrowDown";

import { toast } from "react-toastify";

interface User {
  user_id: number;
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role_id: number;
  role?: { id: number; name: string };
}

interface Props {
  user: User;
  userId: string;
}

// Тип данных формы
type FormData = {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  role_id: number;
};

// Интерфейс для формы изменения пароля
type PasswordFormData = {
  password: string;
  confirm_password: string;
};

export default function EditUserForm({ user, userId }: Props) {
  const { t } = useTranslation();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [form, setForm] = useState<FormData>({
    first_name: user.first_name || "",
    last_name: user.last_name || "",
    username: user.username || "",
    email: user.email || "",
    role_id: user.role_id,
  });
  const [error, setError] = useState<string | null>(null);

  // Состояния для управления формой пароля
  const [showPasswordFields, setShowPasswordFields] = useState<boolean>(false);
  const [passwordError, setPasswordError] = useState<string | null>(null);

  // Отдельный useForm для формы пароля
  const passwordForm = useForm<PasswordFormData>({
    defaultValues: {
      password: "",
      confirm_password: "",
    },
  });

  // Мутация: config-only для React Query v5
  const mutation = useMutation<User, Error, FormData>({
    mutationFn: (updated: FormData): Promise<User> =>
      api.put<User>(`/api/v1/users/admin/users/${userId}`, updated).then((res) => res.data),
    onSuccess: (updatedUser) => {
      // обновить кэш новой версией пользователя
      queryClient.setQueryData<User[]>(["admin-users"], (users) => {
        if (!users) return [];
        return users.map((u) => (u.user_id === updatedUser.user_id ? updatedUser : u));
      });
      // обновить кэш конкретного пользователя для формы
      queryClient.setQueryData<User>(["admin-user", userId], updatedUser);
      router.push("/admin/users");
    },
    onError: () => {
      setError(t("users.error_update") || "Error updating user");
    },
  });

  // Мутация для изменения пароля
  const passwordMutation = useMutation<void, Error, { new_password: string }>({
    mutationFn: (passwordData): Promise<void> => {
      return api.post<void>(`/api/v1/users/admin/users/${userId}/password`, {
        new_password: passwordData.new_password,
      }).then(() => {});
    },
    onSuccess: () => {
      // Очистка полей пароля и отображение сообщения об успехе
      setShowPasswordFields(false);
      // Сброс значений полей пароля
      passwordForm.reset({ password: "", confirm_password: "" });
      // Отображение уведомления об успешном изменении пароля
      toast.success(t("users.passwordResetSuccess") || "Пароль успешно изменен");
    },
    onError: (error) => {
      // Обработка ошибок от сервера
      toast.error(t("users.passwordResetError") || "Ошибка при изменении пароля");
      console.error("Password reset error:", error);
    },
  });

  const handleChange = (field: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
      const value = field === "role_id" ? Number(e.target.value) : e.target.value;
      setForm((prev) => ({ ...prev, [field]: value }));
    };

  // Функция для отправки формы изменения пароля
  const handlePasswordSubmit = (data: PasswordFormData) => {
    // Проверка совпадения паролей
    if (data.password !== data.confirm_password) {
      setPasswordError(t("users.passwordsDoNotMatch") || "Пароли не совпадают");
      return;
    }

    // Проверка минимальной длины пароля
    if (data.password.length < 8) {
      setPasswordError(t("users.passwordTooShort") || "Пароль должен содержать не менее 8 символов");
      return;
    }

    // Сброс ошибок
    setPasswordError(null);

    // Вызов мутации для изменения пароля
    passwordMutation.mutate({ new_password: data.password });
  };

  // Эффект для очистки полей пароля при закрытии формы
  useEffect(() => {
    if (!showPasswordFields) {
      passwordForm.reset();
      setPasswordError(null);
    }
  }, [showPasswordFields, passwordForm]);

  return (
    <Box sx={{ mt: 4, mx: "auto", maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t("users.edit") || "Edit User"}
      </Typography>
      {error && <Alert severity="error">{error}</Alert>}
      <Box component="form" sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <TextField
          label={t("users.firstName") || "First Name"}
          value={form.first_name}
          onChange={handleChange("first_name")}
          fullWidth
        />
        <TextField
          label={t("users.lastName") || "Last Name"}
          value={form.last_name}
          onChange={handleChange("last_name")}
          fullWidth
        />
        <TextField
          label={t("users.username") || "Username"}
          value={form.username}
          onChange={handleChange("username")}
          fullWidth
        />
        <TextField
          label={t("users.email") || "Email"}
          value={form.email}
          onChange={handleChange("email")}
          fullWidth
        />
        <FormControl fullWidth>
          <InputLabel id="role-label">{t("admin.roles")}</InputLabel>
          <Select
            labelId="role-label"
            label={t("admin.roles") || "Role"}
            value={String(form.role_id)}
            onChange={(e) => setForm((prev) => ({ ...prev, role_id: Number(e.target.value) }))}
          >
            <MenuItem value="1">{t("roles.admin") || "admin"}</MenuItem>
            <MenuItem value="2">{t("roles.user") || "user"}</MenuItem>
            <MenuItem value="3">{t("roles.tech") || "tech"}</MenuItem>
          </Select>
        </FormControl>
        <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={() => mutation.mutate(form)}
            disabled={mutation.status === "pending"}
          >
            {t("users.save") || "Save"}
          </Button>
          <Button variant="outlined" onClick={() => router.back()}>
            {t("admin.back") || "Back"}
          </Button>
        </Box>

        {/* Секция изменения пароля */}
        <Box mt={4}>
          <Button
            variant="outlined"
            onClick={() => setShowPasswordFields(!showPasswordFields)}
            startIcon={showPasswordFields ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
          >
            {t("users.changePassword") || "Изменить пароль"}
          </Button>

          {showPasswordFields && (
            <Box mt={2}>
              <Stack spacing={2}>
                <Stack direction={{ xs: "column", md: "row" }} spacing={2}>
                  <TextField
                    fullWidth
                    label={t("users.newPassword") || "Новый пароль"}
                    type="password"
                    {...passwordForm.register("password", { required: true })}
                    error={!!passwordForm.formState.errors.password || !!passwordError}
                    helperText={
                      passwordForm.formState.errors.password
                        ? t("common.required") || "Обязательное поле"
                        : ""
                    }
                  />
                  <TextField
                    fullWidth
                    label={t("users.confirmPassword") || "Подтвердите пароль"}
                    type="password"
                    {...passwordForm.register("confirm_password", { required: true })}
                    error={!!passwordForm.formState.errors.confirm_password || !!passwordError}
                    helperText={
                      passwordError ||
                      (passwordForm.formState.errors.confirm_password
                        ? t("common.required") || "Обязательное поле"
                        : "")
                    }
                  />
                </Stack>
                <Button
                  type="button"
                  onClick={passwordForm.handleSubmit(handlePasswordSubmit)}
                  variant="contained"
                  color="primary"
                  disabled={passwordMutation.isPending}
                >
                  {passwordMutation.isPending ? (
                    <CircularProgress size={24} />
                  ) : (
                    t("users.resetPassword") || "Сбросить пароль"
                  )}
                </Button>
              </Stack>
            </Box>
          )}
        </Box>
      </Box>
    </Box>
  );
}
