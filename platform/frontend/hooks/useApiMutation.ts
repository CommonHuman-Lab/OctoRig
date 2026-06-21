"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useMutation, useQueryClient, type UseMutationOptions } from "@tanstack/react-query";
import { useNotificationsStore } from "@/stores/notifications.store";

interface Options<TData, TVariables>
  extends Omit<UseMutationOptions<TData, any, TVariables>, "onSuccess" | "onError"> {
  invalidateKeys: readonly (readonly unknown[])[];
  successMessage?: string | ((data: TData) => string);
  errorMessage?: string | ((err: any) => string);
  onSuccess?: (data: TData) => void;
}

export function useApiMutation<TData, TVariables>(opts: Options<TData, TVariables>) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const { invalidateKeys, successMessage, errorMessage, onSuccess, ...rest } = opts;

  return useMutation<TData, any, TVariables>({
    ...rest,
    onSuccess: (data) => {
      for (const key of invalidateKeys) {
        qc.invalidateQueries({ queryKey: key as unknown[] });
      }
      if (successMessage) {
        push("success", typeof successMessage === "function" ? successMessage(data) : successMessage);
      }
      onSuccess?.(data);
    },
    onError: (err: any) => {
      const message = typeof errorMessage === "function" ? errorMessage(err) : errorMessage;
      push("error", message ?? err?.response?.data?.detail ?? "Something went wrong.");
    },
  });
}
