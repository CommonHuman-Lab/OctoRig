# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

REWINDRANGE_LAB: LabDefinition = {
    "id": 1,
    "slug": "rewindrange",
    "name": "Rewind",
    "description": "A retro video and games store with sticky nav menus and stickier database queries. Some things here aren't for sale — but they might still be accessible.",
    "category": "world",
    "container_names": ["octorig-rewindrange"],
    "images": {"app": "octorig-rewindrange:latest"},
    "build_contexts": {"app": "labs/rewindrange"},
    "start_order": ["app"],
    "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21},
    "access_info": [
        {"key": "URL", "value": "http://{container_ip}"},
    ],
    "volume_names": [],
    "env_vars": {},
    "requires_privileged": False,
    "challenges": [
        {
            "slug": "rw-recon-robots",
            "title": "What's Off-Limits?",
            "description": (
                "Every web server has a way to tell search engines what *not* to index. "
                "Find the right file, follow where it leads, and you'll end up somewhere "
                "the store would rather keep private.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "information-disclosure"],
            "skills": ["passive recon", "directory enumeration"],
            "points": 50,
            "flags": [
                {
                    "value": "FLAG{rw_manager_office_found}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Search engines are told what to ignore — that instruction list is itself public.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The file lives at a standard path in the web root. Follow each path it lists.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "Visit /robots.txt, then browse to each Disallow path as a logged-in user.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "rw-sqli-browse-union",
            "title": "Back Room Access",
            "description": (
                "The Rewind Range catalogue runs on a browse filter that accepts "
                "user input and passes it straight to the back end. "
                "The back room holds more than product listings — "
                "the right input might bring some of it to the surface.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sql-injection", "sqlite"],
            "skills": ["UNION SELECT", "SQLite schema enumeration", "column-count detection"],
            "points": 300,
            "flags": [
                {
                    "value": "FLAG{rw_union_select_from_flags}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The category or genre filter on the browse page is worth inspecting. Try an unusual character.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Column count matters. Use ORDER BY to count them before extending the query.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "SELECT name FROM sqlite_master WHERE type='table' lists all tables in the database.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "rw-sqli-login-bypass",
            "title": "Bypass the Velvet Rope",
            "description": (
                "You don't have admin credentials. You might not need them.\n\n"
                "Rewind Range's login form makes a decision based on what you submit. "
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sql-injection", "authentication-bypass", "sqlite"],
            "skills": ["SQLi auth bypass", "tautology injection"],
            "points": 100,
            "flags": [
                {
                    "value": "FLAG{rw_admin_login_bypassed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "What does the server do when you put a quote character in the username field?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "SQL comment sequences can neutralise parts of a query.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Try username: admin'-- with any password.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "rw-sqli-cred-dump",
            "title": "The Member Files",
            "description": (
                "Rewind Range keeps a full member registry — accounts, passwords, "
                "the kind of data customers assume stays locked away. "
                "The database knows more than what's on the shelves, "
                "and the admin's credentials are somewhere in there.\n\n"
                "Find the admin's password and wrap it in `FLAG{}`.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sql-injection", "sqlite"],
            "skills": ["UNION SELECT", "credential extraction"],
            "points": 250,
            "flags": [{"value": "FLAG{123456789}", "flag_type": "static", "case_sensitive": False}],
            "hints": [
                {
                    "order_num": 1,
                    "content": "You already found an injection point. What other tables exist in this database?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "There is a users table. Columns include username and password.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The admin's password is stored in plaintext. Extract it and wrap it in FLAG{}.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "rw-xss-reflected-search",
            "title": "Search and Destroy",
            "description": (
                "Whatever you search for, Rewind Range echoes it back on the results "
                "page. The question is whether it echoes *only* what you typed.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "xss",
            "tags": ["xss", "reflected", "javascript"],
            "skills": ["reflected XSS", "basic payload construction"],
            "points": 100,
            "flags": [
                {
                    "value": "FLAG{rw_reflected_xss_fired}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Does the search input appear verbatim on the results page? Try some HTML.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "HTML tags in the query — do they render, or get escaped?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Try: /search?q=<script>alert(1)</script> — the flag will appear in the page.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "rw-xss-stored-feedback",
            "title": "Leave Your Mark",
            "description": (
                "Satisfied customers leave feedback. Feedback gets read — "
                "or something that acts like reading happens. "
                "The question is who's on the other end, and what their browser does "
                "when your submission arrives.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "xss",
            "tags": ["xss", "stored", "javascript"],
            "skills": ["stored XSS", "cookie exfiltration", "session hijacking"],
            "points": 350,
            "flags": [
                {
                    "value": "FLAG{rw_stored_xss_admin_pwned}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "There is a feedback form. Submit something unusual and think about who reads it and how.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If the admin's browser renders your submission, and the admin has a cookie you want...",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The admin reviews feedback at /admin/feedback. Their session cookie is not HttpOnly.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "rw-idor-inbox",
            "title": "You've Got Mail",
            "description": (
                "Rewind Range has a private messaging feature. Messages are fetched "
                "by number — but whose messages can you actually read?\n\n"
                "Log in as any regular user and find out.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "access-control", "enumeration"],
            "skills": ["IDOR", "sequential ID enumeration"],
            "points": 150,
            "flags": [
                {
                    "value": "FLAG{rw_idor_inbox_read}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in and find the inbox URL. The message ID is in the path.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try different message IDs. The server may not check who the message belongs to.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Log in as alice (password: iloveyou). Try /inbox/1, /inbox/7 and nearby IDs.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "rw-idor-rental-api",
            "title": "Someone Else's Rental",
            "description": (
                "Rewind Range has a REST API for rental orders. Each order has an ID. "
                "As an authenticated user, how many orders can you actually access?\n\n"
                "Explore the API and see what turns up in records that aren't yours.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "idor",
            "tags": ["idor", "bola", "api", "access-control"],
            "skills": ["API IDOR", "Burp Intruder / ffuf", "JSON parsing"],
            "points": 250,
            "flags": [
                {
                    "value": "FLAG{rw_api_idor_rentals}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Authenticate and look for a rental orders endpoint in the API.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try different order IDs. Does the API only return your own?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "GET /api/v1/rentals/<id> as any logged-in user. Check a few IDs for a memo field.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "rw-session-forge",
            "title": "Rewind the Cookie",
            "description": (
                "Session cookies are signed, not encrypted. The signature is only as "
                "strong as the secret behind it — and secrets sometimes find their "
                "way into source code.\n\n"
                "Craft a session that says you're the admin and walk through a door "
                "you were never given a key to.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["session", "flask", "crypto"],
            "skills": ["Flask session internals", "itsdangerous", "cookie signing"],
            "points": 500,
            "flags": [
                {
                    "value": "FLAG{rw_session_forged_as_admin}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Flask session cookies are signed with a SECRET_KEY. What if you could find it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The source code is available in the lab. Look for the secret key in app.py.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Use flask-unsign: --sign --cookie '{\"user_id\": 1}' --secret '<key>'",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "rw-py-sqli-script",
            "title": "Script the Injector",
            "description": (
                "Clicking through a web form is slow. The same input that surprises the "
                "database can be sent programmatically — faster, quieter, and repeatable. "
                "Craft a Python script that talks directly to the server and pulls back "
                "something the UI was never meant to show you.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "sql-injection", "automation"],
            "skills": ["requests", "HTTP parameter injection", "response parsing"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{rw_python_sqli_automated}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "A script that loops and changes one parameter per request can cover ground no human can match.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The browse page accepts a filter parameter in the query string. Send your requests there.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Try appending to the filter value and watch what the response body contains.",
                    "cost": 100,
                },
            ],
        },
    ],
}
