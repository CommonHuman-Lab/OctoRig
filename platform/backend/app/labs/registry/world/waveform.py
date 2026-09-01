# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

WAVEFORM_LAB: LabDefinition = {
    "id": 22,
    "slug": "waveform",
    "name": "Waveform",
    "description": "An indie music-streaming SPA with a client-side router and an API that trusts it far too much. The front end looks empty until it isn't.",
    "category": "world",
    "container_names": ["octorig-waveform"],
    "images": {"app": "octorig-waveform:latest"},
    "build_contexts": {"app": "labs/waveform"},
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
            "slug": "wf-recon-admin-bac",
            "title": "Nothing To See Here",
            "description": (
                "Waveform's front page is a single-page app — most of it doesn't exist "
                "until JavaScript runs. Somewhere in what it tells search engines to "
                "ignore is a route that was never meant to be reachable by an ordinary "
                "listener.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "recon",
            "tags": ["recon", "access-control", "spa"],
            "skills": ["passive recon", "client-side routing", "broken access control"],
            "points": 100,
            "flags": [
                {"value": "FLAG{wf_admin_api_no_authz_check}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "robots.txt still lists routes, even for a single-page app.", "cost": 0},
                {"order_num": 2, "content": "The route is client-side only — a plain HTTP fetch of it won't show anything. You need a real browser or a renderer.", "cost": 50},
                {"order_num": 3, "content": "Log in as any regular user, then visit /admin. The dashboard calls /api/admin/stats, which checks that you're logged in but never checks who.", "cost": 75},
            ],
        },
        {
            "slug": "wf-sqli-login-bypass",
            "title": "Skip The Line",
            "description": (
                "You don't have an account. Waveform's login API makes a decision "
                "based on what you send it.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "sqli",
            "tags": ["sql-injection", "authentication-bypass", "sqlite"],
            "skills": ["SQLi auth bypass", "tautology injection"],
            "points": 100,
            "flags": [
                {"value": "FLAG{wf_admin_login_bypassed}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "POST /api/auth/login takes username and password as JSON. What does a quote character do to the query?", "cost": 0},
                {"order_num": 2, "content": "A SQL comment sequence can neutralise the password check entirely.", "cost": 50},
                {"order_num": 3, "content": "Try username: admin'-- with any password.", "cost": 75},
            ],
        },
        {
            "slug": "wf-sqli-search-union",
            "title": "Wrong Note",
            "description": (
                "The track search API accepts a query and passes it straight to the "
                "database. Somewhere in that database is a table that was never meant "
                "to show up in search results.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sql-injection", "sqlite"],
            "skills": ["UNION SELECT", "SQLite schema enumeration", "column-count detection"],
            "points": 300,
            "flags": [
                {"value": "FLAG{wf_union_select_from_flags}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/search?q= — try an unusual character in q.", "cost": 0},
                {"order_num": 2, "content": "The query selects two columns. Use UNION SELECT once you know the column count.", "cost": 50},
                {"order_num": 3, "content": "SELECT name FROM sqlite_master WHERE type='table' lists every table, including _flags.", "cost": 75},
            ],
        },
        {
            "slug": "wf-sqli-cred-dump",
            "title": "Backstage List",
            "description": (
                "You already found a way into the database through search. The admin's "
                "password is sitting in a table you haven't pulled from yet.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "sqli",
            "tags": ["sql-injection", "sqlite", "credential-extraction"],
            "skills": ["UNION SELECT", "credential extraction"],
            "points": 250,
            "flags": [
                {"value": "FLAG{123456789}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "The same injection point that reached _flags can reach any table.", "cost": 0},
                {"order_num": 2, "content": "There's a users table with username and password columns.", "cost": 50},
                {"order_num": 3, "content": "The admin's password is stored in plaintext. Wrap it in FLAG{}.", "cost": 75},
            ],
        },
        {
            "slug": "wf-xss-dom-search",
            "title": "Feedback Loop",
            "description": (
                "Waveform's search page shows you what you searched for. It does this "
                "entirely in the browser, and it doesn't ask any questions about what "
                "you typed.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "xss",
            "tags": ["xss", "dom-based", "javascript", "spa"],
            "skills": ["DOM XSS", "client-side sinks"],
            "points": 150,
            "flags": [
                {"value": "FLAG{wf_dom_xss_confirmed}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "The search results heading echoes your query directly into the page's HTML, client-side, not from the server.", "cost": 0},
                {"order_num": 2, "content": "This app exposes a global function, wfXssFlag(), that only runs if your injected markup executes.", "cost": 50},
                {"order_num": 3, "content": "Try /search?q=<img src=x onerror=wfXssFlag()>", "cost": 75},
            ],
        },
        {
            "slug": "wf-xss-stored-display-name",
            "title": "Signed",
            "description": (
                "Your display name follows you around Waveform — onto every playlist "
                "you've made. Nothing sanitises it before it shows up somewhere else.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "xss",
            "tags": ["xss", "stored", "javascript", "spa"],
            "skills": ["stored XSS", "client-side sinks"],
            "points": 350,
            "flags": [
                {"value": "FLAG{wf_stored_xss_confirmed}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "Register an account, then update your display name from the Account page.", "cost": 0},
                {"order_num": 2, "content": "The playlist page renders 'Created by <owner>' without escaping it. Create your own playlist attribution surface — check where display_name resurfaces.", "cost": 50},
                {"order_num": 3, "content": "Set your display name to <img src=x onerror=wfXssFlag2()>, then view any page that shows it.", "cost": 100},
            ],
        },
        {
            "slug": "wf-idor-playlist",
            "title": "Founders' Demo Vault",
            "description": (
                "Waveform has private playlists. Private just means the flag isn't set "
                "to public — the API was never taught the difference.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "access-control"],
            "skills": ["IDOR", "sequential ID enumeration"],
            "points": 200,
            "flags": [
                {"value": "FLAG{wf_private_playlist_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/playlists/<id> — the featured playlists are ids 1-3. Keep going.", "cost": 0},
                {"order_num": 2, "content": "Nothing in the handler checks is_private before returning the playlist.", "cost": 50},
                {"order_num": 3, "content": "Try /api/playlists/4.", "cost": 75},
            ],
        },
        {
            "slug": "wf-idor-royalties",
            "title": "Follow The Money",
            "description": (
                "Artist royalty statements are meant for the artist and the platform's "
                "finance team. The API doesn't check who's asking.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "idor",
            "tags": ["idor", "bola", "api", "access-control"],
            "skills": ["API IDOR", "unauthenticated enumeration"],
            "points": 250,
            "flags": [
                {"value": "FLAG{wf_royalties_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/artists/<id>/royalties — no login required at all.", "cost": 0},
                {"order_num": 2, "content": "There are 8 artists. Check each one's royalties memo field.", "cost": 50},
                {"order_num": 3, "content": "Try /api/artists/2/royalties.", "cost": 75},
            ],
        },
        {
            "slug": "wf-session-forge",
            "title": "Forged Pass",
            "description": (
                "Waveform's session cookie is signed, not encrypted — and the secret "
                "behind that signature lives in the app's own source and in a staff "
                "member's leaked config.\n\n"
                "Craft a session that says you're the admin.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["session", "flask", "crypto"],
            "skills": ["Flask session internals", "itsdangerous", "cookie signing"],
            "points": 500,
            "flags": [
                {"value": "FLAG{wf_session_forged_admin}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "Flask session cookies are signed with a SECRET_KEY. What if it leaked?", "cost": 0},
                {"order_num": 2, "content": "The staff SSH/FTP account has a .env file with a SECRET_KEY value in it.", "cost": 75},
                {"order_num": 3, "content": "Use flask-unsign: --sign --cookie '{\"user_id\": 1}' --secret '<key>', then hit /api/admin/stats with the forged cookie.", "cost": 100},
            ],
        },
        {
            "slug": "wf-mass-assign-admin",
            "title": "Field Trip",
            "description": (
                "The account form only shows a display name and a bio field. The API "
                "behind it writes whatever fields you send it — and one of your own "
                "API responses already told you the exact name of a column you're not "
                "supposed to touch.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["mass-assignment", "privilege-escalation"],
            "skills": ["mass assignment", "REST API manipulation"],
            "points": 275,
            "flags": [
                {"value": "FLAG{wf_mass_assignment_privilege_escalation}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/auth/me returns a field about your account that the account form never lets you edit.", "cost": 0},
                {"order_num": 2, "content": "POST /api/account accepts a JSON body. Try including that field directly.", "cost": 50},
                {"order_num": 3, "content": "POST {\"is_admin\": 1} to /api/account. The response itself confirms it worked.", "cost": 75},
            ],
        },
        {
            "slug": "wf-ssrf-import-cover",
            "title": "Fetch Quest",
            "description": (
                "Admins can import cover art from any URL. The server fetches whatever "
                "URL it's given and shows you a piece of the response — including "
                "responses from addresses your browser could never reach directly.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["ssrf", "api", "information-disclosure"],
            "skills": ["SSRF", "internal endpoint discovery"],
            "points": 350,
            "flags": [
                {"value": "FLAG{wf_ssrf_internal_transcode_reached}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "Cover import is behind /api/admin/import-cover and needs admin. Once you have admin, it fetches whatever URL you give it, server-side.", "cost": 0},
                {"order_num": 2, "content": "Point the import at http://127.0.0.1/ — there's a route under /api/internal/ that isn't reachable from outside the container.", "cost": 50},
                {"order_num": 3, "content": "POST {\"artist_id\": 1, \"url\": \"http://127.0.0.1/api/internal/transcode\"} to /api/admin/import-cover and read fetched_preview.", "cost": 100},
            ],
        },
        {
            "slug": "wf-insane-ssrf-cmdi-chain",
            "title": "Backstage Pass",
            "description": (
                "Three things you've already found — none of them fatal on their own "
                "— line up into something much worse when chained in the right "
                "order.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "insane",
            "category": "web",
            "tags": ["chained-exploit", "mass-assignment", "ssrf", "command-injection", "rce"],
            "skills": ["exploit chaining", "mass assignment", "SSRF", "command injection"],
            "points": 700,
            "flags": [
                {"value": "FLAG{wf_insane_ssrf_cmdi_chain}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "Being logged in isn't the same as being trusted — and once you are trusted, some features talk to the app itself, not the outside world.", "cost": 0},
            ],
        },
        {
            "slug": "wf-idor-recent-plays",
            "title": "What You Were Listening To",
            "description": (
                "Your account page shows your own recently-played tracks. The API "
                "behind it takes a user id — and never checks whose id it is.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "privacy", "access-control"],
            "skills": ["IDOR", "sequential ID enumeration"],
            "points": 190,
            "flags": [
                {"value": "FLAG{wf_recent_plays_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/users/<id>/recent — you need to be logged in, but the id doesn't have to be yours.", "cost": 0},
                {"order_num": 2, "content": "The admin account's id is small. Try it.", "cost": 50},
                {"order_num": 3, "content": "Try /api/users/1/recent.", "cost": 75},
            ],
        },
        {
            "slug": "wf-idor-follows",
            "title": "Who's Watching Who",
            "description": (
                "Following an artist comes with an optional private note about why. "
                "The API for reading someone's follows doesn't check who's asking.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "idor",
            "tags": ["idor", "bola", "privacy", "access-control"],
            "skills": ["IDOR", "sequential ID enumeration"],
            "points": 170,
            "flags": [
                {"value": "FLAG{wf_follows_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "GET /api/users/<id>/following — same missing check as recent plays.", "cost": 0},
                {"order_num": 2, "content": "Check the same account id you already had luck with.", "cost": 50},
                {"order_num": 3, "content": "Try /api/users/1/following.", "cost": 75},
            ],
        },
        {
            "slug": "wf-idor-playlist-mutate",
            "title": "Uninvited Editor",
            "description": (
                "Playlists have an owner. Adding or removing a track from one doesn't "
                "check whether you're it.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "idor",
            "tags": ["idor", "bola", "access-control"],
            "skills": ["IDOR", "state-changing BOLA"],
            "points": 230,
            "flags": [
                {"value": "FLAG{wf_playlist_mutate_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "Playlists you don't own still let you add or remove tracks through the API — the ownership check that exists for reading a playlist wasn't applied to writing to one.", "cost": 0},
                {"order_num": 2, "content": "POST /api/playlists/<id>/tracks or DELETE /api/playlists/<id>/tracks/<track_id> — try it against a playlist id that isn't yours.", "cost": 50},
                {"order_num": 3, "content": "Playlist 4 (Founders' Demo Vault) belongs to admin. Add or remove a track from it while logged in as anyone else.", "cost": 75},
            ],
        },
        {
            "slug": "wf-idor-playlist-delete",
            "title": "Scorched Earth",
            "description": (
                "There's no delete button anywhere in the app for a whole playlist — "
                "only for individual tracks. That doesn't mean the API doesn't have "
                "one, and it doesn't mean it checks who's asking.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "idor",
            "tags": ["idor", "bola", "access-control", "api-only"],
            "skills": ["IDOR", "state-changing BOLA", "undocumented endpoint discovery"],
            "points": 260,
            "flags": [
                {"value": "FLAG{wf_playlist_delete_idor}", "flag_type": "static", "case_sensitive": False}
            ],
            "hints": [
                {"order_num": 1, "content": "The playlist track endpoints follow REST conventions. What HTTP method against the playlist's own URL, with no trailing path, would delete the whole thing?", "cost": 0},
                {"order_num": 2, "content": "DELETE /api/playlists/<id> exists even though no button in the UI calls it.", "cost": 50},
                {"order_num": 3, "content": "While logged in as anyone else, send DELETE to a playlist id owned by admin.", "cost": 75},
            ],
        },
    ],
}
