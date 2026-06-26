# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

SUBVERSE_LAB: LabDefinition = {
    "id": 8,
    "slug": "subverse",
    "name": "SubVerse",
    "description": "An open community platform where anyone can post, comment, and share. The content moderation isn't the only thing that's porous.",
    "category": "world",
    "container_names": ["octorig-subverse"],
    "images": {"app": "octorig-subverse:latest"},
    "build_contexts": {"app": "labs/subverse"},
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
            "slug": "sv-recon-robots",
            "title": "Hidden Community",
            "description": (
                "SubVerse hosts communities for all kinds of groups. Not all of them are listed publicly. A file the site publishes for crawlers hints at where the private ones live.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "recon",
            "difficulty": "easy",
            "points": 50,
            "tags": ["information-disclosure"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Check the standard file that web crawlers are expected to read before indexing a site.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "One of the disallowed paths is a community that isn't linked from anywhere. Visit it and read the announcements.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "sv-sqli-login",
            "title": "Skeleton Key",
            "description": (
                "The login form takes a username and a password. Whether both of them actually matter is worth investigating.\n\n"
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
                    "content": "Try entering a special character in the username. What does the server respond with?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "A quote character breaks the authentication query. A comment character ends the query before the password check.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "After gaining access as admin, inspect the HTTP response headers on the admin panel.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-sqli-search-union",
            "title": "Search Party",
            "description": (
                "The post search takes your query and finds matching content. The database stores more than forum posts — and how you phrase the query affects what comes back.\n\n"
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
                    "content": "Try unusual characters in the search box. Does the error reveal anything about how the query works?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The database has internal tables not visible through the UI. You can enumerate them.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "UNION SELECT — determine the column count, then target the internal flags table.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-idor-message",
            "title": "Someone's DM",
            "description": (
                "Private messages are meant to stay private. Every message has an ID, and the API has an endpoint that retrieves by that ID. Try pulling up a conversation you were never part of.\n\n"
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
                    "content": "Browse to the messages endpoint. Try IDs you didn't send or receive.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Early messages in the system were sent between admin accounts. Low IDs may contain sensitive information.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "sv-idor-draft-post",
            "title": "Unpublished",
            "description": (
                "Before a post goes live, it lives as a draft. Draft posts aren't linked in the UI — but if you know the path, and you're logged in, the server will show you.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "idor",
            "difficulty": "easy",
            "points": 100,
            "tags": ["information-disclosure", "broken-access-control"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Draft posts have their own URL pattern. Log in and explore the post path — there may be a draft sub-path.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try iterating post IDs on the draft path. Some posts were never published but are still accessible.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "sv-mass-assign-escalate",
            "title": "Power Up",
            "description": (
                "The profile editor shows you a few fields: display name, bio, the basics. The server that handles your update may be listening for a few more than that.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "web",
            "difficulty": "medium",
            "points": 250,
            "tags": ["mass-assignment", "privilege-escalation"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Intercept the profile update request. Are there fields the server accepts that aren't in the HTML form?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Try including fields related to account standing or permissions in the POST body.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Including `role=admin` in the profile edit POST escalates your account. Then visit the admin secret endpoint.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-ssti-announce",
            "title": "The Announcement",
            "description": (
                "Community moderators can preview announcements before publishing. The preview renders on the server — and the rendering context is more capable than a text formatter should be.\n\n"
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
                    "content": "Try submitting `{{ 7*7 }}` in the announcement preview. If the response shows 49, the server evaluates your input.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The preview endpoint checks login but not role. Any registered user can submit a preview.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The server exposes its application config in the template context. The flag is stored there.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-cmdi-preview-link",
            "title": "Preview Exploit",
            "description": (
                "When you share a link in a post, the site fetches a preview. Somewhere between your input and the network request, the URL is processed in a way that may allow more than fetching.\n\n"
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
                    "content": "Try submitting a URL with shell metacharacters in it. What does the server return?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The URL is passed to a shell command. Characters that separate shell commands can break out of the URL argument.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The flag is in a file at the root of the server filesystem. Use a command to read it.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-xss-stored-bio",
            "title": "Bio Hazard",
            "description": (
                "User bios are displayed on public profile pages. The profile page also sets a session cookie. Is the bio display safe to include arbitrary text?\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "category": "xss",
            "difficulty": "easy",
            "points": 200,
            "tags": ["xss", "stored"],
            "skills": [],
            "flags": [],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Edit your profile bio. Try including some HTML. Does your profile page render it?",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "If HTML renders in the bio, JavaScript does too. The profile page sets a session cookie.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "The session cookie on this page is not HttpOnly — JavaScript can read it with `document.cookie`.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "sv-py-cmdi",
            "title": "Command Drone",
            "description": (
                "Somewhere in this forum a field passes its value straight into an OS-level "
                "call. A browser makes that awkward to exploit — a Python script does not. "
                "Construct the right payload, send it programmatically, and read what the "
                "server hands back.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "python",
            "tags": ["python", "scripting", "command-injection", "rce", "automation"],
            "skills": ["requests", "session handling", "command injection", "shell metacharacters"],
            "points": 300,
            "flags": [
                {
                    "value": "FLAG{sv_python_cmdi_droned}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Find a feature that sends data off-server on your behalf. The value you supply may reach a shell.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The link-preview endpoint passes your URL into a system call. Shell separators can append a second command.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "POST to /api/posts with a crafted url field. Add a separator and a read command. The flag lives at /flag.txt on the host.",
                    "cost": 100,
                },
            ],
        },
    ],
}
