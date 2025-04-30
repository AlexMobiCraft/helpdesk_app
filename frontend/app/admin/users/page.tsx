"use client";

import React, { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useQuery } from "@tanstack/react-query";
import api from "@/api/axios";
import { Box, Typography, CircularProgress, Table, TableHead, TableRow, TableCell, TableBody, Paper, TableContainer, Alert, Button } from "@mui/material";
import Link from "next/link";

export default function AdminUsersPage() {
  const { t } = useTranslation();

  // Получение списка пользователей
  const { data: users, isLoading, error, refetch } = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => api.get("/api/v1/users/admin/users").then(res => res.data),
  });

  return (
    <Box sx={{ mt: 4 }}>
      <Box sx={{ mb: 2, display: 'flex', gap: 2 }}>
        <Link href="/admin" passHref>
          <Button variant="outlined">{t("admin.back")}</Button>
        </Link>
        <Link href="/admin/users/new" passHref>
          <Button variant="contained" color="primary">{t("users.new") || "Новый пользователь"}</Button>
        </Link>
      </Box>
      <Typography variant="h4" gutterBottom>{t("admin.users")}</Typography>
      {isLoading && <CircularProgress />}
      {error && <Alert severity="error">{t("users.error") || "Ошибка загрузки пользователей"}</Alert>}
      {users && (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>{t("users.fullName") || "Имя и фамилия"}</TableCell>
                <TableCell>{t("admin.roles")}</TableCell>
                <TableCell>{t("users.actions") || "Действия"}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user: any) => {
                // Маппинг ролей
                const roleMap: Record<number, string> = {
                  1: "admin",
                  2: "user",
                  3: "tech"
                };
                const fullName = `${user.first_name || ""} ${user.last_name || ""}`.trim();
                const rawRole = user.role?.name || user.role_id;
                const roleValue = typeof rawRole === "number"
                  ? (roleMap[rawRole] || String(rawRole))
                  : rawRole;
                return (
                  <TableRow key={user.user_id}>
                    <TableCell>{fullName}</TableCell>
                    <TableCell>{roleValue}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Link href={`/admin/users/edit/${user.user_id}`} passHref>
                          <Button variant="outlined" size="small">{t("users.edit") || "Редактировать"}</Button>
                        </Link>
                        <Button variant="outlined" color="error" size="small" onClick={() => {/* TODO: удалить */}}>
                          {t("users.delete") || "Удалить"}
                        </Button>
                      </Box>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      )}

    </Box>
  );
}
