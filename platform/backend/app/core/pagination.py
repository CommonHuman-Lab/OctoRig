# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from typing import Annotated

from fastapi import Query

DefaultLimit = Annotated[int, Query(ge=1, le=200)]
WideLimit = Annotated[int, Query(ge=1, le=500)]
NarrowLimit = Annotated[int, Query(ge=1, le=30)]
