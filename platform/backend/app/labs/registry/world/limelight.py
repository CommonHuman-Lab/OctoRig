# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

LIMELIGHT_LAB: LabDefinition = {
    "id": 7,
    "slug": "limelight",
    "name": "Limelight",
    "description": "Book a seat. Check your confirmation. Start to wonder whether the seat next to yours is yours to look at too.",
    "category": "world",
    "container_names": ["octorig-limelight"],
    "images": {"app": "octorig-limelight:latest"},
    "build_contexts": {"app": "labs/limelight"},
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
            "slug": "ll-recon-robots",
            "title": "Curtain Call",
            "description": (
                "Before the main feature begins, someone left instructions for web crawlers. Read the disallowed lines — one of those paths hands back more than it should to any logged-in visitor.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "recon",
            "points": 50,
            "challenge_type": "flag",
            "estimated_minutes": 5,
            "tags": ["recon"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Every web server's first secret lives at a well-known path in the root.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "One of the disallowed paths responds to authenticated users with internal status information and something extra.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ll-sqli-search",
            "title": "Director's Cut",
            "description": (
                "The film catalogue search is how you find what's playing. The database has more in it than the current programme — and what comes back may depend on more than the title you type.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "sqli",
            "points": 200,
            "challenge_type": "flag",
            "estimated_minutes": 20,
            "tags": ["sqli", "sqlite"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try unusual characters in the search. Does the error reveal how your input is being used?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The search wraps your input in a string comparison. Closing that string lets you append your own query.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Use UNION SELECT — match the column count of the movies query and pivot to the schema tables.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ll-sqli-gift",
            "title": "Redeem Yourself",
            "description": (
                "Gift cards are validated by code. The redemption form takes your input, checks it against the database, and tells you whether you're in credit. What the database does with that input is worth examining.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "sqli",
            "points": 250,
            "challenge_type": "flag",
            "estimated_minutes": 25,
            "tags": ["sqli", "sqlite"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try putting a special character in the gift code field. What does the response look like?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The code field goes straight into a WHERE clause. Enumerate the database schema to find what other tables exist.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT into a hidden table. Match the column count of the gift card query.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ll-sqli-api-reviews",
            "title": "Critical Review",
            "description": (
                "A JSON endpoint returns film reviews by ID. The ID segment travels from the URL into the query without a stop in between.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "sqli",
            "points": 200,
            "challenge_type": "flag",
            "estimated_minutes": 20,
            "tags": ["sqli", "api"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Check /openapi.json — the spec lists every available route including newer v1 endpoints.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The review endpoint uses an f-string SQL query. The path parameter is the injection point.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "ll-xss-stored-review",
            "title": "Standing Ovation",
            "description": (
                "The review system stores and renders submitted text without sanitisation. A payload posted on any film page executes in the browser of every subsequent visitor.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "xss",
            "points": 150,
            "challenge_type": "flag",
            "estimated_minutes": 15,
            "tags": ["xss", "stored"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Review text is rendered with no output encoding. A script tag in a review runs for every visitor.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Check what cookies are present when the movie page loads. Not all of them carry the HttpOnly flag.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ll-idor-booking",
            "title": "Not Your Seat",
            "description": (
                "You booked a seat. So did everyone else. Booking IDs are assigned when a reservation is made — whether the cinema enforces whose reservation you can view is worth testing.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "idor",
            "points": 100,
            "challenge_type": "flag",
            "estimated_minutes": 10,
            "tags": ["idor", "access-control"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Booking IDs are sequential integers. Start from 1.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The confirmation code field on the first booking contains something unusual.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ll-bac-admin-panel",
            "title": "Staff Entrance",
            "description": (
                "The administration panel verifies that a session exists. It does not verify whether the session holder is supposed to be there.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "web",
            "points": 150,
            "challenge_type": "flag",
            "estimated_minutes": 10,
            "tags": ["bac", "access-control"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Register a regular account and navigate to the path listed in robots.txt.",
                    "cost": 0,
                },
            ],
        },
        {
            "slug": "ll-ssti-announce",
            "title": "The Projectionist's Script",
            "description": (
                "The announcement editor lets you preview your message before publishing. The preview is rendered on the server — and the render context may know more than the message author.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "hard",
            "category": "web",
            "points": 450,
            "challenge_type": "flag",
            "estimated_minutes": 35,
            "tags": ["ssti", "web"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Try submitting `{{ 7*7 }}` in the preview body. If you see 49, the server is evaluating your input.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The server-side context exposes internal application state. What objects are available in the template?",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ll-mass-assign-privesc",
            "title": "Rewrite the Credits",
            "description": (
                "Profile updates accept fields straight from the POST body with no filtering. Sending fields that were never shown in the form can change more than a display name.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "web",
            "points": 250,
            "challenge_type": "flag",
            "estimated_minutes": 20,
            "tags": ["mass-assignment", "privilege-escalation"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The profile form shows display_name, email, and password — but the endpoint accepts every user column.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "After updating your own profile with extra fields, an authenticated API endpoint will unlock. Check /api/v1/.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "ll-gift-admin-noauth",
            "title": "Unlocked Vault",
            "description": (
                "An administrative endpoint for managing gift cards was deployed without any authentication requirement. The path is hinted from a familiar file.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "web",
            "points": 100,
            "challenge_type": "flag",
            "estimated_minutes": 5,
            "tags": ["bac", "unauthenticated", "recon"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "robots.txt lists several disallowed paths. One of them needs no credentials at all.",
                    "cost": 0,
                },
            ],
        },
        {
            "slug": "ll-py-bulk-book",
            "title": "Bulk Booker",
            "description": (
                "Seats are finite. The booking logic enforces that limit — but only if "
                "requests arrive one at a time. A Python script can send many at once. "
                "What happens to the seat count when the server can't keep up?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "python",
            "tags": ["python", "scripting", "race-condition", "business-logic", "concurrency"],
            "skills": ["requests", "threading", "session handling", "race condition exploitation"],
            "points": 300,
            "flags": [
                {
                    "value": "FLAG{ll_python_race_booked}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The seat limit is checked at read time. What if two writes land before either check completes?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The booking endpoint is POST /api/bookings. The seat_count check happens in the request handler, not a transaction.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Fire 10+ booking requests for the same fully-booked show in parallel threads sharing one session. Inspect the responses — one may carry the flag.",
                    "cost": 100,
                },
            ],
        },
    ],
}
