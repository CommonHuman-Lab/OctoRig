# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
from .._types import LabDefinition

FLEETWAVE_LAB: LabDefinition = {
    "id": 21,
    "slug": "fleetwave",
    "name": "FleetWave",
    "description": "A logistics and delivery fleet-management SaaS — shipment tracking, depot manifests, driver rosters, freight-credit billing, and a carrier-status checker that will fetch anything you point it at.",
    "category": "world",
    "container_names": ["octorig-fleetwave"],
    "images": {"app": "octorig-fleetwave:latest"},
    "build_contexts": {"app": "labs/fleetwave"},
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
            "slug": "fw-recon-ftp-backup",
            "title": "Nightly Manifest",
            "description": (
                "FleetWave's warehouse-management system writes a nightly "
                "backup manifest somewhere outside the web app. The FTP "
                "service accepts anonymous connections — see what the backup "
                "left behind.\n\n"
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
                    "value": "FLAG{fw_recon_ftp_backup_leak}",
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
                    "content": "Browse the pub/ directory and read the backup manifest in full.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "fw-sqli-login",
            "title": "Dispatcher Override",
            "description": (
                "The sign-in form checks your username and password against "
                "the database. The username travels into that check "
                "unescaped — a crafted value can decide the outcome before "
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
                    "value": "FLAG{fw_sqli_login_bypassed}",
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
            "slug": "fw-sqli-search-shipments",
            "title": "Track Everything",
            "description": (
                "The shipment search box filters by tracking number or "
                "recipient. What the database actually does with your search "
                "term is worth a closer look — it stores more than shipment "
                "rows.\n\n"
                "**Target:** `http://{container_ip}/shipments/search`"
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
                    "value": "FLAG{fw_sqli_shipment_search_union}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try an unusual character in the search box. Does an error reveal how the query is built?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The search wraps your input in a LIKE clause. Close it early and append your own query — match the column count first.",
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
            "slug": "fw-idor-shipment",
            "title": "Someone Else's Parcel",
            "description": (
                "Shipments are fetched by a numeric id. Some carry "
                "restricted manifests — but does the server check that the "
                "shipment belongs to your account before showing it?\n\n"
                "**Target:** `http://{container_ip}/shipments/1`"
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
                    "value": "FLAG{fw_idor_shipment_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Sign in as any dispatcher. Try /shipments/<id> for ids you'd never normally be linked to.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Start at shipment id 1. Its manifest notes field contains more than handling instructions.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "fw-idor-depot-manifest",
            "title": "Bonded Cargo",
            "description": (
                "Each depot stores a restricted manifest note — override "
                "PINs and bonded-cargo seals — meant only for staff assigned "
                "to that depot. Whether the depot page actually checks your "
                "depot assignment is a separate question.\n\n"
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
                    "value": "FLAG{fw_idor_depot_manifest_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Depot ids are sequential integers. Try /depots/<id> for a depot you're not assigned to.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": 'Depot 4 ("Harbor Depot") has a bonded-cargo manifest note. Visit /depots/4 directly — the depot_access table is never consulted.',
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "fw-bac-admin-driver-roster",
            "title": "Roster Leak",
            "description": (
                "The driver roster holds personal data — licence numbers "
                "and phone numbers. The gate on the way in checks whether a "
                "session exists, not whose session it is.\n\n"
                "**Target:** `http://{container_ip}/admin/driver-roster`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["bac", "broken-access-control", "vertical-privesc", "pii"],
            "skills": ["broken access control", "vertical privilege escalation"],
            "points": 150,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{fw_bac_admin_driver_roster_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Register a regular dispatcher account. The path is listed in robots.txt under Disallow.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Visit /admin/driver-roster directly while signed in as your regular account. Read every driver's notes.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "fw-xss-stored-feedback",
            "title": "Flagged for Review",
            "description": (
                "Any user can file a delivery-issue report with a free-text "
                "note. The operations review queue renders those notes back "
                "out exactly as submitted.\n\n"
                "Reach the review queue as admin and your own payload renders "
                "in your own browser — and the admin session cookie isn't "
                "HttpOnly.\n\n"
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
                    "value": "FLAG{fw_xss_admin_cookie_stolen}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": 'The "report a delivery issue" form on any shipment submits a note. Try submitting HTML.',
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The review queue doesn't escape notes when it renders them. You'll need an admin session to view the queue — there's a faster way than waiting.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Bypass login as admin (SQLi), file a report containing a script that reads document.cookie, then visit /admin/review yourself.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "fw-mass-assign-admin",
            "title": "Self-Promotion",
            "description": (
                "The profile form only shows a name, email, and bio field. "
                "The endpoint behind it accepts whatever fields you send, "
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
                    "value": "FLAG{fw_mass_assign_admin_escalated}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Intercept the profile update. Are there fields the server accepts that the form never shows?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Send a JSON body to /profile instead of a form post. Include a field related to account role.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": 'POST {"role": "admin"} as JSON to /profile — the profile page confirms the escalation with the flag.',
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "fw-biz-freight-credit",
            "title": "Credit Where It Isn't Due",
            "description": (
                "Dispatchers can settle freight credits to other accounts. "
                "The transfer endpoint never checks the sign of the amount or "
                "whether you have the balance to cover it.\n\n"
                "**Target:** `http://{container_ip}/billing`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["business-logic", "idor", "integer"],
            "skills": ["business logic abuse", "negative-amount manipulation"],
            "points": 200,
            "estimated_minutes": 20,
            "flags": [
                {
                    "value": "FLAG{fw_biz_freight_credit_overflow}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "What happens if you transfer a negative amount to another account?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A negative transfer moves credit the wrong way — your own balance goes up. Push it past the reconciliation threshold to trip the alarm.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "fw-ssrf-carrier-check",
            "title": "Check Any Carrier",
            "description": (
                "Admins can run a carrier status check against any URL. The "
                "server fetches whatever it's given and shows you the "
                "response — including responses from addresses your browser "
                "could never reach directly.\n\n"
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
                    "value": "FLAG{fw_ssrf_internal_manifest}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The carrier-check feature is admin-only. You'll need admin access before you can reach it.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "POST to /api/admin/carrier-check with a url field pointing at http://127.0.0.1/. There's an internal-only endpoint under /api/internal/.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Point the check at http://127.0.0.1/api/internal/manifest-export?format=csv and read the JSON it reflects back.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "fw-py-idor-shipment-api",
            "title": "Shipment Sweep",
            "description": (
                "Every shipment has a JSON API endpoint. Ids are small "
                "sequential integers, and clicking through them one at a time "
                "is slow. Script a sweep and see what surfaces.\n\n"
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
                    "value": "FLAG{fw_python_idor_shipment_swept}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in with requests.Session(), then GET /api/v1/shipments/<id> for a small range of ids.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The endpoint doesn't check ownership. One shipment's notes field is worth reading.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Sweep shipment ids 1 through 10. Shipment 9's notes field has the flag.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "fw-insane-chain-rce",
            "title": "Total Fleet Compromise",
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
                    "value": "FLAG{fw_insane_chained_rce}",
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
