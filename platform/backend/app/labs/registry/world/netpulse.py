# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

NETPULSE_LAB: LabDefinition = {
    "id": 6,
    "slug": "netpulse",
    "name": "NetPulse",
    "description": "Your ISP's self-service portal: billing, support tickets, network diagnostics. Some features were built for operators. Not all of them were locked down properly.",
    "category": "world",
    "container_names": ["octorig-netpulse"],
    "images": {"app": "octorig-netpulse:latest"},
    "build_contexts": {"app": "labs/netpulse"},
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
            "slug": "np-recon-billing-db",
            "title": "Internal Memo",
            "description": (
                "An endpoint that was never meant to be public is still reachable. The billing data it serves has no gate in front of it — only the assumption that nobody would think to look.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "recon",
            "difficulty": "easy",
            "points": 50,
            "tags": ["unauthenticated", "information-disclosure"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Web servers often publish a file telling crawlers which paths to avoid. That list can be revealing.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "One of the disallowed paths serves raw JSON without requiring authentication. Look through the records.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "np-sqli-login",
            "title": "Ghost Credentials",
            "description": (
                "The admin panel sits behind a login. The form expects a username and a password — but the decision it makes may depend more on the username than you'd think.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "sqli",
            "difficulty": "easy",
            "points": 100,
            "tags": ["authentication", "sqli"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try entering unusual characters in the username. Does the error change?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A quote in the username changes the query structure. A comment character ends it early.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "After logging in as admin, check the HTTP response headers on the admin panel page.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "np-sqli-board-search",
            "title": "Thread Unraveled",
            "description": (
                "The community board has a search box. Your query travels further than the forum posts — the database has more to offer if you ask the right way.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "sqli",
            "difficulty": "medium",
            "points": 250,
            "tags": ["sqli", "sqlite"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try entering a single quote in the search. What does the response tell you?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The database stores more than posts. Enumerate the schema to find what else is there.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Use UNION SELECT — match the column count, then target the internal flags table.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "np-idor-user",
            "title": "Wrong Account",
            "description": (
                "The user API returns account details by ID. You are logged in — but does that mean you can only see yourself?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "idor",
            "difficulty": "easy",
            "points": 100,
            "tags": ["api", "horizontal-privilege-escalation"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The API spec lists a users endpoint. Try accessing IDs other than your own.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The first user created in the system usually has the lowest ID.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "np-idor-ticket",
            "title": "Internal Dispatch",
            "description": (
                "Support tickets are accessed by number. The system verifies you're logged in — not that the ticket is yours.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "idor",
            "difficulty": "easy",
            "points": 100,
            "tags": ["api", "information-disclosure"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Browse to the tickets API. What happens when you try IDs you didn't create?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Internal ops tickets were created before customer accounts. Try lower IDs.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "np-bac-admin-config",
            "title": "Backdoor Config",
            "description": (
                "There's an administrative configuration endpoint that the operators never restricted. The path exists, the server responds, and the check that should gate access may not be there.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "web",
            "difficulty": "easy",
            "points": 150,
            "tags": ["broken-access-control", "api"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Check robots.txt or the API spec for admin paths.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try accessing an admin path while logged in as a regular user. The check may only verify you have a session.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "np-ssti-template",
            "title": "Preview Flaw",
            "description": (
                "The notification system lets admins preview message templates before sending. The preview renders content on the server side — and the render context is richer than the feature implies.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "web",
            "difficulty": "hard",
            "points": 450,
            "tags": ["ssti", "broken-access-control"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try submitting `{{ 7*7 }}` in the preview body. If the result is 49, the server is evaluating your input.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The preview endpoint doesn't verify admin role — any logged-in user can reach it.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The server exposes its configuration object in the template context. Look for the flag there.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "np-cmdi-dnslookup",
            "title": "Diagnostic Override",
            "description": (
                "The network tools section has a hostname lookup feature. It runs a system command in the background. What happens when the hostname isn't a hostname?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "web",
            "difficulty": "medium",
            "points": 350,
            "tags": ["command-injection", "rce"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "What separates one shell command from another? Try those characters in the hostname field.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The tool runs a DNS lookup command. Appending a shell separator lets you run something else after it.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The flag is in a file at the root of the filesystem. Read it with `cat`.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "np-xss-reflected-board",
            "title": "Open Mic Night",
            "description": (
                "The community board search reflects your search term back in the response. The page also sets a cookie that isn't protected from client-side access.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "xss",
            "difficulty": "easy",
            "points": 150,
            "tags": ["xss", "reflected"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try entering some HTML in the search. Does the page render it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If HTML renders, JavaScript does too. The page sets a cookie that JavaScript can read.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Read `document.cookie` from your script. The cookie value is the flag.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "np-py-ssti",
            "title": "Template Tap",
            "description": (
                "A portal feature lets operators compose messages with dynamic placeholders. "
                "The engine that fills those placeholders in is more powerful than the "
                "interface suggests. A well-placed expression can reach well beyond the "
                "intended output.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "ssti", "automation"],
            "skills": ["requests", "SSTI", "template expression crafting"],
            "points": 250,
            "flags": [
                {
                    "value": "FLAG{np_python_ssti_tapped}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Template engines have a syntax for expressions. Some let expressions do more than format strings.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The diagnostics notification preview endpoint passes your input into a render call. Try an arithmetic expression first to confirm.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "POST your expression as the template_body field to /api/admin/notify/preview and inspect the rendered output.",
                    "cost": 100,
                },
            ],
        },
    ],
}
