# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

TRADEFLOOR_LAB: LabDefinition = {
    "id": 2,
    "slug": "tradefloor",
    "name": "TradeFloor",
    "description": "A real-time stock trading platform where data moves fast and trust is extended a little too freely. Not every position that's accessible here should be.",
    "category": "world",
    "container_names": ["octorig-tradefloor"],
    "images": {"app": "octorig-tradefloor:latest"},
    "build_contexts": {"app": "labs/tradefloor"},
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
            "slug": "tf-recon-robots",
            "title": "Off the Books",
            "description": (
                "Every exchange has areas it doesn't want indexed. TradeFloor is "
                "no different — there's a public file that hints at paths the "
                "operators would prefer you didn't visit.\n\n"
                "Find one of those paths and access it as a logged-in user.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "information-disclosure", "bac"],
            "skills": ["passive recon", "broken access control"],
            "points": 50,
            "flags": [
                {
                    "value": "FLAG{tf_fund_manager_found}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Web servers publish a list of paths they'd prefer crawlers ignored. That list is public.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Some of the restricted paths don't actually enforce authentication.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "tf-sqli-market-union",
            "title": "Inside the Order Book",
            "description": (
                "The order book search takes a ticker symbol and surfaces market data. "
                "The database running behind it holds more than trade history — "
                "and the search field may accept more than just ticker symbols.\n\n"
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
                    "value": "FLAG{tf_union_select_from_flags}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Enter an unusual character in the ticker search and observe the response.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Column count must match before extending a query. Use ORDER BY to determine it.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "SELECT name FROM sqlite_master WHERE type='table' reveals what else is stored.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-sqli-api-token",
            "title": "Token Without a Password",
            "description": (
                "TradeFloor's REST API issues tokens via a login endpoint. "
                "The credential check has a flaw — the right username might "
                "bypass the need for a password entirely.\n\n"
                "Obtain an admin token, then call a privileged endpoint.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sql-injection", "authentication-bypass", "api"],
            "skills": ["SQLi auth bypass", "JWT", "API testing"],
            "points": 100,
            "flags": [
                {
                    "value": "FLAG{tf_api_token_injected}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The API token endpoint is at /api/token. Try a POST with unusual username values.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "What if the username contained a character that changes how the query is interpreted?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Once you have an admin token, look for a privileged API endpoint that returns the flag.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-sqli-cred-dump",
            "title": "Membership Leaked",
            "description": (
                "TradeFloor stores more than tickers and prices. "
                "Somewhere in that database is a user registry — accounts, credentials, "
                "the kind of data that was never meant to be readable from the outside.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sql-injection", "sqlite"],
            "skills": ["UNION SELECT", "credential extraction"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{tf_users_table_dumped}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "You already have an injection point. What other tables exist?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Enumerate with sqlite_master. Look for a users or members table.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The _flags table has a row called sqli-creds containing the answer.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-xss-reflected-market",
            "title": "Ticker Injection",
            "description": (
                "The market search field echoes your query back on the results page. "
                "How faithfully does it reproduce what you type?\n\n"
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
                    "value": "FLAG{tf_reflected_xss_fired}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Enter some HTML into the search field. Does the page reflect it back?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If your HTML renders, can you go further? The flag is in the browser's cookie jar.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "A script that reads document.cookie will find it.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-idor-order-detail",
            "title": "Someone Else's Trade",
            "description": (
                "Trade orders each have an ID. As a logged-in user, you can view "
                "your own orders — but are they truly *your* orders?\n\n"
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
                    "value": "FLAG{tf_idor_order_memo}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in and find the order detail URL. The ID is in the path.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try other IDs. The server may hand back orders belonging to different users.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Check the admin's orders. A memo field on one of them contains the flag.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-bac-admin-view",
            "title": "The Compliance Desk",
            "description": (
                "TradeFloor's admin panel has a per-user detail view. Being logged "
                "in might be enough to reach it — try navigating there as a "
                "regular user.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "web",
            "tags": ["broken-access-control", "bac", "idor", "vertical-privesc"],
            "skills": ["broken access control", "URL enumeration"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{tf_bac_admin_user_detail}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Admin routes are under /admin/. Log in as any user and explore.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The user detail page takes an ID. User IDs are sequential integers.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Try /admin/users/1 while logged in as alice.p.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "tf-jwt-alg-none",
            "title": "Trust Nobody, Sign Nothing",
            "description": (
                "TradeFloor's API uses tokens. The way the server verifies them "
                "is worth examining — specifically, what the token itself says "
                "about how it should be verified.\n\n"
                "Forge an admin token and call a privileged endpoint.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["jwt", "authentication", "api"],
            "skills": ["JWT internals", "algorithm confusion", "API testing"],
            "points": 450,
            "flags": [
                {
                    "value": "FLAG{tf_jwt_alg_none_bypassed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Decode your JWT (base64url). What's in the header? Pay attention to the alg field.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The server reads the algorithm from the token itself. What happens if you change it?",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Set alg to 'none', drop the signature, add role: admin to the payload. Call GET /api/admin/report as Bearer.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "tf-py-idor-sweep",
            "title": "Portfolio Sweep",
            "description": (
                "Profiles are numbered. Each number belongs to someone — or it should. "
                "Write a Python script that walks the sequence and notices when a record "
                "surfaces that the current session has no business seeing.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "idor", "automation", "api"],
            "skills": ["requests", "session handling", "sequential enumeration"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{tf_python_idor_swept}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "A loop over sequential numbers can reveal what manual clicking cannot.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The portfolio endpoint is under /api/. Authenticated requests return different data than anonymous ones.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Log in first with requests.Session(), then iterate /api/portfolio/<id> and inspect each response.",
                    "cost": 100,
                },
            ],
        },
    ],
}
