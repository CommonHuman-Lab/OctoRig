# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
WebSocket connection manager.

`manager` is the module-level singleton.
`emit()` is the thread-safe fire-and-forget helper used by sync code (lab_service,
notification_service, etc.) to broadcast an event to all connected browser tabs.
"""

import asyncio
import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.add(ws)

    def register(self, ws: WebSocket) -> None:
        """Track an already-accepted socket (e.g. one authenticated via a first message)."""
        self._connections.add(ws)

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.discard(ws)

    async def broadcast(self, event_type: str, data: Any) -> None:
        if not self._connections:
            return
        payload = json.dumps({"type": event_type, "data": data})
        dead: set[WebSocket] = set()
        for ws in list(self._connections):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        self._connections -= dead

    def emit(self, event_type: str, data: Any) -> None:
        """Thread-safe fire-and-forget — safe to call from sync background tasks."""
        if self._loop is None or not self._connections:
            return
        asyncio.run_coroutine_threadsafe(self.broadcast(event_type, data), self._loop)


manager = ConnectionManager()


def emit(event_type: str, data: Any) -> None:
    manager.emit(event_type, data)
