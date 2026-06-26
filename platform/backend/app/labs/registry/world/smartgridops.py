# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

SMARTGRIDOPS_LAB: LabDefinition = {
    "id": 18,
    "slug": "smartgridops",
    "name": "SmartGridOps",
    "description": "A SCADA control room for a municipal power grid. Operators log in to manage zone load, issue device commands, and dispatch energy credits. Not every operator is supposed to reach every zone.",
    "category": "world",
    "container_names": ["octorig-smartgridops"],
    "images": {"app": "octorig-smartgridops:latest"},
    "build_contexts": {"app": "labs/smartgridops"},
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
            "slug": "sgo-recon-ftp",
            "title": "Configuration Drop",
            "description": (
                "SmartGridOps runs an FTP service for distributing firmware and "
                "field device configurations to the operator fleet. "
                "The server accepts anonymous connections. "
                "Not everything in the config directory was meant for the public internet.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "ftp", "information-disclosure"],
            "skills": ["anonymous FTP", "config harvesting"],
            "points": 50,
            "flags": [
                {
                    "value": "FLAG{sgo_recon_ftp_config_leak}",
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
                    "content": "Browse the pub/ directory. There is more than firmware in there.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "Download scada_config.txt. Read it carefully — all the way to the end.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "sgo-sqli-login",
            "title": "Control Room Access",
            "description": (
                "The operator login submits your credentials against the database. "
                "The query that does the check is built with the username inline — "
                "a crafted username might make the password less relevant than "
                "the form implies.\n\n"
                "Once inside the admin panel, check the HTTP response headers.\n\n"
                "**Target:** `http://{container_ip}/login`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sqli", "authentication-bypass", "sqlite"],
            "skills": ["SQL injection", "auth bypass"],
            "points": 100,
            "flags": [
                {
                    "value": "FLAG{sgo_sqli_login_bypassed}",
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
                    "content": "Username: admin'-- with any password. After logging in, inspect the response headers on /admin.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sgo-idor-zone",
            "title": "Restricted Zone",
            "description": (
                "Every grid zone has a detail page showing load figures, capacity, "
                "and a restricted notes field used by senior operators for "
                "operational procedures. Your account is assigned to a specific zone. "
                "The endpoint that serves zone details doesn't enforce that assignment.\n\n"
                "Zone 4 carries something that should be restricted to its operator.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "access-control"],
            "skills": ["IDOR", "object-level access control"],
            "points": 100,
            "flags": [
                {
                    "value": "FLAG{sgo_idor_zone_secret_note}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any operator. Navigate to the Zones section and look at the URL structure.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Zone IDs are sequential integers. Your account's zone may not be zone 4.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "Browse to /zones/4. The restricted notes field contains the flag.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "sgo-api-admin",
            "title": "Fleet Token",
            "description": (
                "The device API is gated by a static token shared across the entire "
                "field hardware fleet. The FTP config file hints at where to find it. "
                "Once you have the admin token, a privileged endpoint hands back "
                "the full operator roster — and whatever the admin keeps in their notes field.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["api", "hardcoded-token", "information-disclosure"],
            "skills": ["API token reuse", "operator enumeration"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{sgo_idor_operator_token_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The FTP config file contains two API tokens. One is for field devices, one is for admin.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The admin API endpoint is /api/admin/operators. It requires an X-Device-Token header or ?token= query param.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Call GET /api/admin/operators?token=<admin_token>. Look at the notes field of operator ID 1.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sgo-ssrf-poll",
            "title": "Reach Inside",
            "description": (
                "The device status poller is a diagnostic tool: provide a URL, "
                "the server fetches it and reflects the response back. "
                "The server-side fetch can reach addresses that aren't reachable from "
                "your browser — including endpoints that only respond to local requests.\n\n"
                "**Target:** `http://{container_ip}/devices/poll`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["ssrf", "api", "information-disclosure"],
            "skills": ["SSRF", "internal endpoint discovery"],
            "points": 250,
            "flags": [
                {
                    "value": "FLAG{sgo_ssrf_internal_fetch}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The poller at /devices/poll accepts any URL and fetches it server-side. Try pointing it at http://127.0.0.1/.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "There is an internal-only endpoint under /api/internal/ that refuses connections from outside.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Fetch http://127.0.0.1/api/internal/ssrf-flag via the poller. The JSON response contains the flag.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "sgo-cmdi-reboot",
            "title": "Remote Reboot",
            "description": (
                "Issuing a reboot signal to a field device first pings the management IP "
                "to confirm the device is reachable. An operator can override the "
                "management target address before the ping fires. "
                "The override goes directly into a shell call, unsanitised.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["command-injection", "rce"],
            "skills": ["command injection", "shell metacharacters"],
            "points": 350,
            "flags": [
                {
                    "value": "FLAG{sgo_cmdi_device_reboot_rce}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Open any device detail page. The Reboot form has a target address field. Try adding shell separator characters.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The target is passed to: ping -c 1 -W 1 <target> && echo ... — you can chain commands after the ping.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Set target to: 127.0.0.1; cat /flag_cmdi.txt — the command output appears in the response.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "sgo-biz-credits",
            "title": "Demand Response",
            "description": (
                "Operators accumulate energy credits through demand-response programmes "
                "and can forward them to colleagues. The credit transfer form accepts "
                "a recipient ID and an amount. "
                "The system does not check the sign of that amount before applying it.\n\n"
                "**Target:** `http://{container_ip}/credits`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["business-logic", "parameter-tampering"],
            "skills": ["business logic abuse", "negative value injection"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{sgo_business_logic_credit_overflow}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in and go to /credits. Try transferring credits to another operator. Now think about the amount field.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The amount is a floating-point number. Explore both ends of its range.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Transfer a large negative amount to any operator. Your balance grows. Once it exceeds 1,000,000 the flag appears.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sgo-mqtt-inject",
            "title": "Zone Override",
            "description": (
                "The MQTT console pre-fills the publish topic with your assigned zone's "
                "command channel. Grid commands are supposed to stay within an operator's "
                "own zone. The topic field is editable — what happens when you publish "
                "to a zone you don't control?\n\n"
                "**Target:** `http://{container_ip}/mqtt`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["iot", "mqtt", "access-control"],
            "skills": ["IoT command injection", "MQTT topic manipulation"],
            "points": 150,
            "flags": [
                {
                    "value": "FLAG{sgo_mqtt_topic_injection}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in and go to /mqtt. The topic field is pre-filled with your zone. Try changing it.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Publishing to another zone's command topic trips the broker ACL audit. Wildcards do the same.",
                    "cost": 25,
                },
                {
                    "order_num": 3,
                    "content": "Change the topic to grid/zone/1/cmd (if you're not zone 1) and publish any payload. The flag appears on submission.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "sgo-py-cmdi",
            "title": "Automated Override",
            "description": (
                "The device reboot endpoint passes an operator-supplied management "
                "target through a shell call without sanitisation. "
                "A browser makes injection awkward — a Python script makes it precise. "
                "Authenticate, target the reboot endpoint, and read the flag from "
                "the host filesystem.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "command-injection", "automation"],
            "skills": ["requests", "session handling", "command injection", "shell metacharacters"],
            "points": 250,
            "flags": [
                {
                    "value": "FLAG{sgo_python_cmdi_automated}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in via POST /login with requests.Session(). Then POST to /devices/<id>/reboot with a crafted target field.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The target field is inserted into a shell ping command. A semicolon lets you append a second command.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Set target to '127.0.0.1; cat /flag_py_cmdi.txt' in your POST body. The output appears in the rendered page.",
                    "cost": 100,
                },
            ],
        },
    ],
}
