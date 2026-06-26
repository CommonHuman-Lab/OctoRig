# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

HUMANBANK_LAB: LabDefinition = {
    "id": 4,
    "slug": "humanbank",
    "name": "HumanBank",
    "description": "A retail banking portal that knows your balance and your transaction history. It may also know things about other customers.",
    "category": "world",
    "container_names": ["octorig-humanbank"],
    "images": {"app": "octorig-humanbank:latest"},
    "build_contexts": {"app": "labs/humanbank"},
    "start_order": ["app"],
    "exposed_ports": {"http": 80, "ssh": 22, "ftp": 21, "redis": 6379},
    "access_info": [
        {"key": "URL", "value": "http://{container_ip}"},
    ],
    "volume_names": [],
    "env_vars": {},
    "requires_privileged": False,
    "challenges": [
        {
            "slug": "hb-recon-audit-log",
            "title": "Open Books",
            "description": (
                "An internal diagnostics endpoint was deployed and never locked down. "
                "It responds to anyone who asks — no session required. "
                "The raw financial history of the entire bank is there for the taking.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "openapi", "unauthenticated", "information-disclosure"],
            "skills": ["API enumeration", "OpenAPI spec reading"],
            "points": 50,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{hb_recon_audit_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The API publishes a machine-readable description of every endpoint it exposes.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "One of the paths listed contains audit information. Try accessing it without a session cookie.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "hb-sqli-login",
            "title": "Master Key",
            "description": (
                "The login screen accepts your name and passphrase. "
                "What if the passphrase weren't the deciding factor? "
                "A carefully chosen username might make the decision for you.\n\n"
                "Once inside as admin, check the admin profile — "
                "there is a field the bank keeps very close to its chest.\n\n"
                "**Target:** `http://{container_ip}/login`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sqli", "login-bypass", "sqlite", "auth"],
            "skills": ["SQL injection", "authentication bypass"],
            "points": 100,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{hb_sqli_login_bypassed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "What happens when you put special characters in the username field?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A single quote in the username causes an error. What if you also added a comment character after the username?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Username: `admin'--`, any password. After login, the flag is in `/profile` under the admin's address field.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "hb-sqli-search",
            "title": "Transaction Miner",
            "description": (
                "The transaction search takes your query and goes hunting. "
                "What it brings back might surprise you — especially if you ask "
                "it to go looking somewhere it wasn't designed to reach.\n\n"
                "**Target:** `http://{container_ip}/search`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sqli", "sqlite"],
            "skills": ["UNION SELECT", "SQLite schema enumeration"],
            "points": 250,
            "estimated_minutes": 25,
            "flags": [
                {
                    "value": "FLAG{hb_sqli_search_union}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try entering unusual characters in the search box. Does the response change?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The database has more tables than the app shows you. SQLite keeps a schema table you can query.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT into the `_flags` table. Match the 7-column count of the original query.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "hb-sqli-txn-memo",
            "title": "Between the Lines",
            "description": (
                "The transaction list accepts filters — search by memo, type, date range. "
                "Each field shapes how the underlying query is built. "
                "The database knows more than just transaction history.\n\n"
                "**Target:** `http://{container_ip}/accounts/1/transactions`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sqli", "sqlite"],
            "skills": ["UNION SELECT", "filter parameter injection"],
            "points": 200,
            "estimated_minutes": 20,
            "flags": [
                {"value": "FLAG{hb_sqli_txn_dump}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try putting unusual characters in the `memo` filter. What does the server respond with?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The memo filter wraps your input in a LIKE clause. Closing it early opens the door to appending your own query.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT into the `_flags` table from the memo param. The original query returns 6 columns.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "hb-idor-accounts",
            "title": "Everyone's Balance",
            "description": (
                "Banking works on the assumption that you can only see your own accounts. "
                "But what if the account list page didn't share that assumption?\n\n"
                "One account in the system belongs to an entity that shouldn't be visible "
                "to regular customers. Its transaction history has a memo worth reading.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "accounts", "banking"],
            "skills": ["IDOR", "object-level access control"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{hb_idor_cmnh_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Browse to the accounts list — does it only show your own?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Look for an account with an unusual holder name. Its transactions contain a flag in an internal memo.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "hb-idor-ticket",
            "title": "Someone Else's Ticket",
            "description": (
                "Support tickets are assigned a number when filed. "
                "Does the system verify that the number you're requesting belongs to you?\n\n"
                "An internal ticket was created by bank staff and was never meant "
                "to be seen by customers. Find it.\n\n"
                "**Target:** `http://{container_ip}/tickets/`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "tickets", "enumeration"],
            "skills": ["IDOR", "horizontal privilege escalation"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{hb_idor_ticket_read}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Ticket IDs are sequential numbers. Try visiting a ticket that isn't yours.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Internal support tickets were created before any customer accounts. Try the earliest IDs.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "hb-bac-admin-api",
            "title": "Teller Without a Badge",
            "description": (
                "There's an API endpoint meant for administrators only. "
                "The door asks if you have a key — not whether the key is the right one. "
                "Any customer who walks in authenticated might find the vault wide open.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["bac", "broken-access-control", "api", "privilege-escalation"],
            "skills": ["broken access control", "API testing"],
            "points": 150,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{hb_bac_api_admin_bypass}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The API spec lists every endpoint. Look for paths under an `/admin/` prefix.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Log in as any regular customer and call an admin endpoint. Inspect the JSON response carefully.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "hb-bac-user-detail",
            "title": "Open Door Policy",
            "description": (
                "The admin area has a page that shows detailed user profiles. "
                "The gate on the way in checks whether you have a session — "
                "not whose session it is.\n\n"
                "The first account in the system has something stored that "
                "was never meant to be customer-facing.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "web",
            "tags": ["bac", "broken-access-control", "admin-panel"],
            "skills": ["broken access control", "vertical privilege escalation"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{hb_bac_admin_detail_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Look for an admin section in the API spec or robots.txt. Try navigating there while logged in as a regular user.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The admin user-detail path takes a user ID. User ID 1 is the admin. The flag is in the profile data.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "hb-xss-stored-ticket",
            "title": "Your Complaint Has Been Received",
            "description": (
                "The bank's support system stores everything customers submit "
                "and surfaces it for staff review in the admin panel. "
                "When an admin reads your ticket, their browser does the rendering — "
                "and rendering decisions have consequences.\n\n"
                "Leave something in a ticket that persists.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "xss",
            "tags": ["xss", "stored", "admin-panel"],
            "skills": ["stored XSS", "cookie exfiltration", "session hijacking"],
            "points": 300,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{hb_xss_admin_cookie_stolen}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try submitting HTML in a ticket body. Does the admin panel render it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The admin ticket view renders content without escaping. JavaScript submitted in a ticket runs when an admin views it.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Log in as admin (hint: the login form has its own flaw) and visit the ticket list. `document.cookie` will have the flag.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "hb-py-sqli-dump",
            "title": "Account Drain",
            "description": (
                "The bank's data doesn't stay locked when the query is written carelessly. "
                "A Python script can do in seconds what a proxy intercept does one request "
                "at a time — chain the steps together and the vault opens itself.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "sql-injection", "automation"],
            "skills": ["requests", "session handling", "SQLi chaining", "response parsing"],
            "points": 225,
            "flags": [
                {
                    "value": "FLAG{hb_python_sqli_chained}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "One endpoint lets you in without the right password. Another leaks more than it should once you're authenticated.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The account search endpoint accepts user input that reaches the query directly.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Use a single requests.Session() — first post to /login with the bypass, then query /accounts/search with your payload.",
                    "cost": 100,
                },
            ],
        },
    ],
}
