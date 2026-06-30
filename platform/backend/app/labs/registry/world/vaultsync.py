# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

VAULTSYNC_LAB: LabDefinition = {
    "id": 19,
    "slug": "vaultsync",
    "name": "VaultSync",
    "description": "A password-manager SaaS that promises zero-knowledge encryption and seamless sync. The sharing model and the admin tooling were both built in a hurry.",
    "category": "world",
    "container_names": ["octorig-vaultsync"],
    "images": {"app": "octorig-vaultsync:latest"},
    "build_contexts": {"app": "labs/vaultsync"},
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
            "slug": "vs-recon-ftp-backup",
            "title": "Nightly Backup",
            "description": (
                "VaultSync runs a nightly backup job that drops a manifest "
                "somewhere outside the web app entirely. The FTP service "
                "accepts anonymous connections — see what the backup left behind.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "ftp", "information-disclosure"],
            "skills": ["anonymous FTP", "backup harvesting"],
            "points": 50,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{vs_recon_ftp_backup_leak}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The FTP service is on port 21. Try connecting anonymously — no credentials required.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Browse the pub/ directory and read what's there in full.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "vs-sqli-login",
            "title": "Master Key Override",
            "description": (
                "The sign-in form checks your username and master password "
                "against the database. The username travels into that check "
                "unescaped — a crafted value might decide the outcome before "
                "the password is even considered.\n\n"
                "Once signed in as the platform admin, the admin panel's "
                "response carries something extra.\n\n"
                "**Target:** `http://{container_ip}/login`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sqli", "login-bypass", "sqlite", "auth"],
            "skills": ["SQL injection", "authentication bypass", "HTTP response headers"],
            "points": 100,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{vs_sqli_login_bypassed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try a special character in the username field. Does the server behave differently?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A single quote breaks the query. A comment character after the username silences the password check.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Username: admin'-- with any password. After signing in, inspect the HTTP response headers on /admin.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "vs-sqli-search-vaults",
            "title": "Search Everything",
            "description": (
                "The item search lets you filter your own vault by title. "
                "What the database actually does with your search term is "
                "worth a closer look — it stores more than vault items.\n\n"
                "**Target:** `http://{container_ip}/vaults/search`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sqli", "sqlite", "union"],
            "skills": ["UNION SELECT", "SQLite schema enumeration", "column-count detection"],
            "points": 250,
            "estimated_minutes": 25,
            "flags": [
                {
                    "value": "FLAG{vs_sqli_vault_search_union}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try an unusual character in the search box. Does the error tell you how the query is built?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The search wraps your input in a LIKE clause. Closing it early lets you append your own query — match the column count first.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT into the _flags table. The original query returns 4 columns.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "vs-idor-vault-item",
            "title": "Someone Else's Secret",
            "description": (
                "Vault items are fetched by a numeric id. You're logged in — "
                "but does the server actually check that the item belongs to you?\n\n"
                "**Target:** `http://{container_ip}/vaults/items/1`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "access-control"],
            "skills": ["IDOR", "sequential ID enumeration"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{vs_idor_vault_item_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Try visiting /vaults/items/<id> for ids you don't own.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Start from item id 1. The notes field on it contains more than a reminder.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "vs-idor-share-link",
            "title": "Uninvited Guest",
            "description": (
                "VaultSync lets vault owners share read access with specific "
                "users through the sharing feature. Whether the vault page "
                "itself enforces that grant is a separate question.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "access-control"],
            "skills": ["IDOR", "object-level access control"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{vs_idor_shared_vault_read}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Vault ids are sequential integers in the URL. Try ones that were never shared with you.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": 'Vault 8 ("Shared Family Vault") wasn\'t shared with your account. Visit /vaults/8 directly and open its items.',
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "vs-bac-admin-recovery",
            "title": "Open Recovery",
            "description": (
                "The platform's master recovery codes live behind an admin "
                "path. The gate on the way in checks whether a session "
                "exists — not whose session it is.\n\n"
                "**Target:** `http://{container_ip}/admin/recovery-codes`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["bac", "broken-access-control", "vertical-privesc"],
            "skills": ["broken access control", "vertical privilege escalation"],
            "points": 150,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{vs_bac_admin_recovery_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Register a regular account. The path is listed in robots.txt under Disallow.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Visit /admin/recovery-codes directly while signed in as your regular account.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "vs-xss-stored-note",
            "title": "Flagged for Review",
            "description": (
                "Any user can report a vault item to the review team with a "
                "free-text note. The admin review queue renders those notes "
                "back out exactly as submitted.\n\n"
                "If you can reach the review queue as admin, your own "
                "payload renders in your own browser — and the admin "
                "session cookie isn't HttpOnly.\n\n"
                "**Target:** `http://{container_ip}/admin/review`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "xss",
            "tags": ["xss", "stored", "admin-panel"],
            "skills": ["stored XSS", "cookie exfiltration"],
            "points": 200,
            "estimated_minutes": 20,
            "flags": [
                {
                    "value": "FLAG{vs_xss_admin_cookie_stolen}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": 'The "report this item" form on any vault item submits a note. Try submitting HTML.',
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The review queue doesn't escape notes when it renders them. You'll need an admin session to view the queue — there's a faster way to get one than waiting.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Bypass login as admin (SQLi), submit a report containing a script that reads document.cookie, then visit /admin/review yourself.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "vs-mass-assign-admin",
            "title": "Self-Promotion",
            "description": (
                "The profile form only shows a name and an email field. "
                "The endpoint behind it accepts whatever fields you send it, "
                "checked against an allow-list that was built too broadly.\n\n"
                "**Target:** `http://{container_ip}/profile`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["mass-assignment", "privilege-escalation"],
            "skills": ["mass assignment", "REST API manipulation"],
            "points": 300,
            "estimated_minutes": 25,
            "flags": [
                {
                    "value": "FLAG{vs_mass_assign_admin_escalated}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Intercept the profile update request. Are there fields the server accepts that the HTML form never shows?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try sending a JSON body to /profile instead of a form post. Include fields related to account role or plan.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": 'POST {"role": "admin"} as JSON to /profile, then visit /admin — the X-Admin-Flag header confirms escalation.',
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "vs-ssrf-breach-check",
            "title": "Check Yourself",
            "description": (
                'Admins can run a "breach check" against any URL to confirm '
                "a credential hasn't leaked. The server fetches whatever URL "
                "it's given and shows you the response — including responses "
                "from addresses your browser could never reach directly.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["ssrf", "api", "information-disclosure"],
            "skills": ["SSRF", "internal endpoint discovery"],
            "points": 350,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{vs_ssrf_internal_vault_export}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The breach-check feature is admin-only. You'll need admin access before you can reach it.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "POST to /api/breach-check with a url field pointing at http://127.0.0.1/. There's an internal-only export endpoint under /api/internal/.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Point the breach check at http://127.0.0.1/api/internal/vault-export?format=json and read the JSON it reflects back.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "vs-py-idor-vault-sweep",
            "title": "Vault Sweep",
            "description": (
                "Every vault has an items API endpoint. Vault ids are small "
                "sequential integers, and clicking through them one at a "
                "time is slow. Script a sweep and see what surfaces.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "idor", "automation", "api"],
            "skills": ["requests", "session handling", "sequential enumeration", "JSON parsing"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{vs_python_idor_vault_swept}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in with requests.Session(), then GET /api/v1/vaults/<id>/items for a small range of ids.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The endpoint doesn't check that the vault belongs to you. One vault's items include a notes field worth reading.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Sweep vault ids 1 through 8. Vault 6's items include a notes field with the flag.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "vs-credential-reuse-pivot",
            "title": "Old Habits",
            "description": (
                "Not every vault item points at a fictional site. Some of "
                "VaultSync's users reuse their master password on services "
                "you've already met elsewhere in OctoRig.\n\n"
                "This challenge spans two labs: keep enumerating beyond the "
                "items you've already found here, and have **HumanBank** "
                "(lab id 4, `172.28.4.0/24`) running alongside VaultSync — "
                "the credential only pays off there.\n\n"
                "**Target:** `http://{container_ip}` and HumanBank's login page"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["credential-reuse", "lateral-movement", "cross-lab", "idor"],
            "skills": ["IDOR enumeration", "credential reuse", "lateral movement across labs"],
            "points": 300,
            "estimated_minutes": 30,
            "requires_labs": ["humanbank"],
            "flags": [
                {
                    "value": "FLAG{vs_credential_reuse_pivot}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "You've already found vault items by guessing sequential ids. Keep going past the ones you've already seen.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "One item beyond the ones you've already found isn't for a made-up site — it's for a bank you may have already broken into once before.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Start HumanBank (./octorig.sh start 4) alongside VaultSync. /vaults/items/11 has a username and password — log into HumanBank with them directly and check the account's profile page.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "vs-insane-chain-rce",
            "title": "Total Vault Compromise",
            "description": (
                "Three things you've already found — none of them fatal on "
                "their own — line up into something much worse when chained "
                "in the right order.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "insane",
            "category": "web",
            "tags": ["chained-exploit", "mass-assignment", "ssrf", "command-injection", "rce"],
            "skills": ["exploit chaining", "mass assignment", "SSRF", "command injection"],
            "points": 700,
            "estimated_minutes": 60,
            "flags": [
                {
                    "value": "FLAG{vs_insane_chained_rce}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Nothing here is exploitable alone. Look at what each vulnerability hands the next one.",
                    "cost": 0,
                },
            ],
        },
    ],
}
