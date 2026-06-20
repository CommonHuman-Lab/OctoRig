# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared singleton: main.py registers it on app.state, route modules use @limiter.limit()
limiter = Limiter(key_func=get_remote_address)
