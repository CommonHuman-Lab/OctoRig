# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

MEDIHUMAN_LAB: LabDefinition = {
    "id": 5,
    "slug": "medihuman",
    "name": "MediHuman",
    "description": "A patient-facing healthcare portal where privacy isn't just best practice — it's the law. Explore how far a logged-in patient can actually reach.",
    "category": "world",
    "container_names": ["octorig-medihuman"],
    "images": {"app": "octorig-medihuman:latest"},
    "build_contexts": {"app": "labs/medihuman"},
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
            "slug": "mh-recon-openapi",
            "title": "Open Spec",
            "description": (
                "The portal publishes a complete map of itself — every endpoint, "
                "every parameter — without requiring a login. "
                "Read it carefully. Developers sometimes leave notes in places they assume nobody will look.\n\n"
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
                    "value": "FLAG{mh_recon_openapi_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Most REST APIs publish their schema at a well-known path. No authentication needed.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Scan the JSON for any non-standard extension fields — keys that start with `x-`.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mh-sqli-login",
            "title": "Doctor's Orders",
            "description": (
                "The login screen trusts what you give it. "
                "A username crafted to speak directly to the database might "
                "bypass the password check entirely.\n\n"
                "Once inside as admin, check the HTTP response from the admin panel — "
                "the server reveals more than just the page.\n\n"
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
                    "value": "FLAG{mh_sqli_login_bypassed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try unusual characters in the username field. Notice any difference in how the server responds?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A quote character breaks the query. A comment character after the username silences the rest.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Username: `admin'--`, any password. After logging in, check the HTTP response headers on `/admin`.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "mh-sqli-patient-search",
            "title": "Records Request",
            "description": (
                "The patient search accepts a name and queries the database. "
                "What the database returns depends entirely on how you frame the question.\n\n"
                "The system stores more than patient names.\n\n"
                "**Target:** `http://{container_ip}/patients`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sqli", "sqlite", "phi", "healthcare"],
            "skills": ["UNION SELECT", "SQLite schema enumeration"],
            "points": 250,
            "estimated_minutes": 25,
            "flags": [
                {
                    "value": "FLAG{mh_sqli_patient_search_union}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Put a special character in the search. Does the error tell you how the query is structured?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The database schema is readable if you know where to look. What tables does SQLite expose by default?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT into a hidden table. The original query returns 9 columns — match that count.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "mh-idor-lab-result",
            "title": "Classified Test Result",
            "description": (
                "Lab results are accessed by ID. The portal verifies you're "
                "authenticated — but not that the result belongs to you.\n\n"
                "One result in the system was filed by an external party "
                "and should never have been accessible to patients. "
                "The notes field tells a different story.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "phi", "healthcare", "lab-results"],
            "skills": ["IDOR", "object-level access control"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{mh_idor_lab_result_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Browse lab result IDs. Does the system restrict which records you can see?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "There are more results in the database than are shown in your patient dashboard.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mh-idor-prescription",
            "title": "Second Opinion",
            "description": (
                "Prescription records are stored by ID. "
                "The system trusts that you'll only ask for your own — "
                "but it doesn't enforce it.\n\n"
                "There is a prescription in the system that belongs to someone else. "
                "The notes field carries something that shouldn't be there.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "phi", "prescriptions"],
            "skills": ["IDOR", "horizontal privilege escalation"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{mh_idor_prescription_read}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Try accessing prescriptions by their ID number.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Your own prescription might not be ID 1. Try IDs you weren't assigned.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mh-bac-admin-export",
            "title": "Patient Data Export",
            "description": (
                "The admin section has a data export that dumps every patient record "
                "in the system. The door is labelled admin-only — "
                "but the bouncer just checks if you exist, not who you are.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["bac", "broken-access-control", "api", "phi", "data-exposure"],
            "skills": ["broken access control", "API testing", "PHI exposure"],
            "points": 150,
            "estimated_minutes": 15,
            "flags": [
                {
                    "value": "FLAG{mh_bac_admin_export_bypass}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The API spec lists admin paths. Try calling one while logged in as a regular patient.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The export endpoint returns JSON with all patient records — and one extra field.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mh-bac-staff-detail",
            "title": "Admin Profile Leak",
            "description": (
                "Staff profiles are tucked behind an admin path. "
                "The lock on the door checks whether you're logged in — "
                "not whether you're staff.\n\n"
                "The first staff member's profile has a field that doesn't belong there.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "web",
            "tags": ["bac", "broken-access-control", "admin-panel", "vertical-privesc"],
            "skills": ["broken access control", "vertical privilege escalation"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{mh_bac_staff_detail_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Look for an admin staff path — the API spec will list it.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Request staff ID 1. The profile data includes a field that shouldn't be visible to patients.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mh-xss-reflected",
            "title": "Search & Destroy",
            "description": (
                "The patient search echoes your search term back on the results page. "
                "It reads it in, and it reads it back out — without checking what it contains.\n\n"
                "There is a cookie set on this page that is readable from the browser.\n\n"
                "**Target:** `http://{container_ip}/patients`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "xss",
            "tags": ["xss", "reflected", "search"],
            "skills": ["reflected XSS", "cookie exfiltration", "Jinja2 | safe"],
            "points": 150,
            "estimated_minutes": 20,
            "flags": [
                {
                    "value": "FLAG{mh_xss_reflected_patients}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try putting some HTML in the search field. Does the page render it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If HTML renders, JavaScript runs too. The page sets a session cookie that isn't flagged HttpOnly.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Read `document.cookie` from your script. The session cookie value is the flag.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "mh-mass-assign",
            "title": "Appointment Escalation",
            "description": (
                "The appointment system lets you update your own bookings. "
                "It accepts a JSON body and trusts you to only send fields "
                "that belong to you.\n\n"
                "Some fields are never shown in the patient form — but the server "
                "will accept them anyway.\n\n"
                "**Target:** `http://{container_ip}/api/v1/appointments/1`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["mass-assignment", "api", "privilege-escalation", "bola"],
            "skills": ["mass assignment", "REST API manipulation", "BOLA"],
            "points": 300,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{mh_mass_assign_escalated}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Intercept a PUT request to the appointments endpoint. What fields does the server actually accept?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try adding fields that control who the appointment is assigned to — fields not present in the patient-facing form.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Including `doctor_id` or `patient_id` in the PUT body triggers the flag in the JSON response.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "mh-py-idor-enum",
            "title": "Record Scraper",
            "description": (
                "Patient records are fetched by ID. The IDs are sequential. "
                "Not every ID belongs to you — but the server doesn't always check. "
                "Script a sweep and see whose records surface.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "idor", "automation", "healthcare"],
            "skills": ["requests", "session handling", "sequential enumeration", "JSON parsing"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{mh_python_idor_scraped}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "An authenticated user can only view their own records — in theory.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The lab results endpoint accepts a record ID in the URL path. Try a range of IDs.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "GET /api/records/<id> with your session cookie. The flag appears in the JSON body of a record that isn't yours.",
                    "cost": 100,
                },
            ],
        },
    ],
}
