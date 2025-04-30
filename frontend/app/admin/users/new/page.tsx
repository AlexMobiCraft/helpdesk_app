"use client";

import React from "react";
import { Box, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import NewUserForm from "./NewUserForm";

export default function NewUserPage() {
  const { t } = useTranslation();
  return (
    <Box sx={{ mt: 4, mx: "auto", maxWidth: 600 }}>
      <Typography variant="h5" gutterBottom>
        {t("users.new") || "Новый пользователь"}
      </Typography>
      <NewUserForm />
    </Box>
  );
}
