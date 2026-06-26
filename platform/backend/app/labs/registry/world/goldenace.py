# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

GOLDENACE_LAB: LabDefinition = {
    "id": 3,
    "slug": "goldenace",
    "name": "GoldenAce",
    "description": "The house sets the rules, and the house trusts its own systems. See how far a registered player can reach before anyone notices.",
    "category": "world",
    "container_names": ["octorig-goldenace"],
    "images": {"app": "octorig-goldenace:latest"},
    "build_contexts": {"app": "labs/goldenace"},
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
            "slug": "ga-recon-robots",
            "title": "House Rules",
            "description": (
                "Every casino has areas off-limits to regular guests. The web equivalent of a staff-only door is well-known — and what's listed behind it doesn't always require a key.\n\n"
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
                    "content": "Web servers publish a list of paths they'd prefer crawlers ignored. That list is itself public.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Some of the restricted paths don't actually require authentication. Try each one.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ga-sqli-promo",
            "title": "Free Chips",
            "description": (
                "The promo desk is how the casino hands out credits. You enter a code, the system checks it, and something happens. The question is whether that check is as airtight as the house assumes.\n\n"
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
                    "content": "What happens when you put special characters in the promo code field?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The injection takes you to the database. Use sqlite_master to see what tables exist.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT against a hidden table. Column count must match the original query.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ga-sqli-leaderboard",
            "title": "Rigged Rankings",
            "description": (
                "The leaderboard keeps score. The search helps you find your ranking. What you type into that field and what the database does with it may not be the same thing.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "sqli",
            "points": 150,
            "challenge_type": "flag",
            "estimated_minutes": 15,
            "tags": ["sqli", "sqlite"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Enter an unusual character in the search. What does the response tell you about how it's processed?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The query uses a LIKE clause. What happens when you close it early?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT to pivot into a hidden table. Match the column count of the users query.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ga-xss-chat",
            "title": "Dealer's Message",
            "description": (
                "The live casino chat is open to all registered players. What you post is visible to everyone who loads the room — including what you didn't intend to post.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "xss",
            "points": 150,
            "challenge_type": "flag",
            "estimated_minutes": 15,
            "tags": ["xss", "stored", "cookies"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Post a message with some HTML in it. Does the chat render it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If HTML renders, so does JavaScript. The page sets a cookie when it loads.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Not all cookies have the HttpOnly flag. Some are readable from JavaScript.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "ga-idor-suite",
            "title": "Wrong Room",
            "description": (
                "Every high-roller gets a suite: their own room, their own history. The suite number lives in the URL. Whether the hotel actually checks your key card is another question.\n\n"
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
                    "content": "Room numbers are sequential integers in the URL.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Start from room 1. Game history memos sometimes contain more than scores.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "ga-biz-negative-bet",
            "title": "The House Loses",
            "description": (
                "The slot machine accepts your bet via a form. The server processes what you send — but does it validate it?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "web",
            "points": 200,
            "challenge_type": "flag",
            "estimated_minutes": 15,
            "tags": ["business-logic", "parameter-tampering"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Intercept the bet submission. What fields are in the POST body?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The bet field accepts numbers. Explore its boundaries — in both directions.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "ga-bac-admin",
            "title": "Staff Only",
            "description": (
                "The casino's administrative area isn't linked from the player dashboard. But the route exists, the server responds to it, and the guest list may not be as exclusive as the signage implies.\n\n"
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
                    "content": "Register a regular account and navigate to /admin.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The flag is displayed on the admin panel page.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ga-bac-high-rollers",
            "title": "VIP Lounge",
            "description": (
                "Every casino keeps a back room for its best clients. This one's not advertised, but it's there — and the velvet rope may be less strict than the signage implies.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "easy",
            "category": "web",
            "points": 100,
            "challenge_type": "flag",
            "estimated_minutes": 10,
            "tags": ["bac", "access-control", "recon"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The path to the VIP area is listed in a file crawlers are told to avoid.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Log in as any user and request the path directly.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "ga-promo-reuse",
            "title": "Double Down",
            "description": (
                "The promo system hands out rewards. What happens if you try to collect more than once?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "difficulty": "medium",
            "category": "web",
            "points": 150,
            "challenge_type": "flag",
            "estimated_minutes": 15,
            "tags": ["business-logic", "promo-abuse"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Redeem a valid promo code. Now try redeeming it again with the same account.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The system tracks total redemptions across all users, but not per-user redemptions.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "ga-py-logic-abuse",
            "title": "House Edge",
            "description": (
                "The house always wins — unless you move faster than the rules allow. "
                "There's a sequence of calls that can leave your balance in a state the "
                "server didn't intend. A Python script can issue them in the right order, "
                "at the right speed.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "python",
            "tags": ["python", "scripting", "business-logic", "race-condition"],
            "skills": ["requests", "session handling", "concurrency", "state manipulation"],
            "points": 200,
            "flags": [
                {
                    "value": "FLAG{ga_python_logic_edge}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Two actions that should be mutually exclusive can both succeed if they arrive close enough together.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Look at the bet and withdraw endpoints. What happens if both fire before the balance updates?",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Use threading.Thread or concurrent.futures to send requests in parallel within the same session.",
                    "cost": 100,
                },
            ],
        },
    ],
}
