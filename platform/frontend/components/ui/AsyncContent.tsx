// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ReactNode } from "react";
import { PageSpinner } from "@/components/ui/Spinner";

interface Props<T> {
  isLoading: boolean;
  data: T[] | undefined;
  empty: ReactNode;
  children: (data: T[]) => ReactNode;
}

export function AsyncContent<T>({ isLoading, data, empty, children }: Props<T>) {
  if (isLoading) return <PageSpinner />;
  if (!data || data.length === 0) return <>{empty}</>;
  return <>{children(data)}</>;
}
