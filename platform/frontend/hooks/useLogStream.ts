"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useRef, useState } from "react";
import { useUserStore } from "@/stores/user.store";
import { BUFFER_LIMITS } from "@/lib/config";

interface Options {
  deploymentId: number;
  container?: string;
  tail?: number;
  enabled?: boolean;
}

export function useLogStream({ deploymentId, container = "app", tail = 100, enabled = true }: Options) {
  const [lines, setLines] = useState<string[]>([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const { accessToken } = useUserStore();

  useEffect(() => {
    if (!enabled || !accessToken) return;

    const wsBase = process.env.NEXT_PUBLIC_API_URL?.replace(/^http/, "ws") ?? "";
    const url = `${wsBase}/api/v1/deployments/${deploymentId}/logs?container=${container}&tail=${tail}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({ token: accessToken }));
      setConnected(true);
    };
    ws.onmessage = (e) => {
      const chunk: string = e.data;
      const newLines = chunk.split(/\r?\n/);
      setLines((prev) => {
        const next = [...prev, ...newLines].filter(Boolean);
        return next.slice(-BUFFER_LIMITS.LOG_STREAM_MAX_LINES);
      });
    };
    ws.onerror = () => setConnected(false);
    ws.onclose = () => setConnected(false);

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [deploymentId, container, tail, enabled, accessToken]);

  function clearLines() {
    setLines([]);
  }

  return { lines, connected, clearLines };
}
