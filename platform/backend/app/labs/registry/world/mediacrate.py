# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
from .._types import LabDefinition

MEDIACRATE_LAB: LabDefinition = {
    "id": 20,
    "slug": "mediacrate",
    "name": "MediaCrate",
    "description": "A streaming and content-creator platform — channels, live streams, subscriber perks, and a moderation team that was clearly added as an afterthought.",
    "category": "world",
    "container_names": ["octorig-mediacrate"],
    "images": {"app": "octorig-mediacrate:latest"},
    "build_contexts": {"app": "labs/mediacrate"},
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
            "slug": "mc-recon-ftp-backup",
            "title": "Nightly Manifest",
            "description": (
                "MediaCrate runs a nightly backup job that drops a manifest "
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
                    "value": "FLAG{mc_recon_ftp_backup_leak}",
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
            "slug": "mc-sqli-login",
            "title": "Account Override",
            "description": (
                "The sign-in form checks your username and password against "
                "the database. The username travels into that check "
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
                    "value": "FLAG{mc_sqli_login_bypassed}",
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
            "slug": "mc-sqli-search-videos",
            "title": "Search Everything",
            "description": (
                "The video search box lets you filter by title. What the "
                "database actually does with your search term is worth a "
                "closer look — it stores more than video metadata.\n\n"
                "**Target:** `http://{container_ip}/videos/search`"
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
                    "value": "FLAG{mc_sqli_search_videos_union}",
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
            "slug": "mc-idor-video",
            "title": "Unlisted Doesn't Mean Hidden",
            "description": (
                "Videos are fetched by a numeric id. Some are marked "
                "unlisted or private — but does the server actually check "
                "that before showing them to you?\n\n"
                "**Target:** `http://{container_ip}/videos/1`"
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
                    "value": "FLAG{mc_idor_video_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in as any user. Try visiting /videos/<id> for ids you'd never normally see linked anywhere.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Start from video id 1. The notes field on it contains more than an editor's reminder.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mc-idor-subscriber-content",
            "title": "Free Perks",
            "description": (
                "Channels can post tier-2 subscriber-exclusive content. "
                "Whether the exclusive content page actually checks your "
                "subscription tier is a separate question.\n\n"
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
                    "value": "FLAG{mc_idor_subscriber_content_exposed}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Channel ids are sequential integers in the URL. Try /channels/<id>/exclusive for a channel you never subscribed to.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": 'Channel 4 ("Mira Sessions") has tier-2 exclusive content. Visit /channels/4/exclusive directly without subscribing.',
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mc-bac-admin-streamkeys",
            "title": "Open Escrow",
            "description": (
                "Every creator's live stream key is escrowed by the "
                "platform in case of an outage. The gate on the way in "
                "checks whether a session exists — not whose session it is.\n\n"
                "**Target:** `http://{container_ip}/admin/stream-keys`"
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
                    "value": "FLAG{mc_bac_admin_streamkeys_exposed}",
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
                    "content": "Visit /admin/stream-keys directly while signed in as your regular account.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mc-xss-stored-comment",
            "title": "Flagged for Review",
            "description": (
                "Any user can report a video to the moderation team with a "
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
                    "value": "FLAG{mc_xss_admin_cookie_stolen}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": 'The "report this video" form on any video submits a note. Try submitting HTML.',
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
            "slug": "mc-mass-assign-verified",
            "title": "Self-Verification",
            "description": (
                "The profile form only shows a name, email, and bio field. "
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
                    "value": "FLAG{mc_mass_assign_admin_escalated}",
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
                    "content": "Try sending a JSON body to /profile instead of a form post. Include a field related to account role.",
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
            "slug": "mc-ssrf-thumbnail-import",
            "title": "Import Anything",
            "description": (
                "Admins can import a video thumbnail from any URL. The "
                "server fetches whatever URL it's given and shows you the "
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
                    "value": "FLAG{mc_ssrf_internal_transcode}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The thumbnail-import feature is admin-only. You'll need admin access before you can reach it.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "POST to /api/admin/import-thumbnail with a url field pointing at http://127.0.0.1/. There's an internal-only transcode endpoint under /api/internal/.",
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Point the import at http://127.0.0.1/api/internal/transcode?format=mp4 and read the JSON it reflects back.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "mc-py-idor-video-api",
            "title": "Video Sweep",
            "description": (
                "Every video has a JSON API endpoint. Video ids are small "
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
                    "value": "FLAG{mc_python_idor_video_swept}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in with requests.Session(), then GET /api/v1/videos/<id> for a small range of ids.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "The endpoint doesn't check video visibility. One video's notes field is worth reading.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Sweep video ids 1 through 10. Video 9's notes field has the flag.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "mc-lfi-banner-traversal",
            "title": "Outside The Frame",
            "description": (
                "Creators can upload a channel banner image. The server "
                "trusts the filename you send it on the way in — and trusts "
                "it again on the way back out when it serves the file. "
                "Walking that filename somewhere it shouldn't go reaches "
                "things that were never meant to be public.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["file-upload", "path-traversal", "lfi"],
            "skills": ["unrestricted file upload", "path traversal", "local file read"],
            "points": 300,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{mc_path_traversal_legal_hold}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "Log in, open your own channel page, and find the banner upload form (only the channel owner sees it).",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Uploaded banners are served from /uploads/<channel_id>/<filename>. The filename isn't sanitized on either the upload or the serve side.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "GET /uploads/<your_channel_id>/../../../data/.private/legal_takedowns.txt — count the ../ until you land outside the upload directory entirely.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "mc-csrf-tip-drain",
            "title": "Generous By Accident",
            "description": (
                "Viewers can tip a creator's channel straight from their "
                "coin balance. The tip endpoint trusts any POST that arrives "
                "with a valid session — it never checks where the request "
                "actually came from.\n\n"
                "**Target:** `http://{container_ip}`"
            ),
            "challenge_type": "flag",
            "difficulty": "medium",
            "category": "web",
            "tags": ["csrf", "state-changing", "wallet"],
            "skills": ["CSRF", "auto-submitting forms"],
            "points": 200,
            "estimated_minutes": 20,
            "flags": [
                {
                    "value": "FLAG{mc_csrf_tip_drained}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "POST /channels/<id>/tip takes just an `amount` form field. Check what protects it from a forged cross-site request — nothing does.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Host an auto-submitting HTML form targeting that endpoint and have a logged-in session (yours is fine) open it. A successful cross-channel tip returns the flag inline.",
                    "cost": 50,
                },
            ],
        },
        {
            "slug": "mc-open-redirect-login",
            "title": "See You On The Other Side",
            "description": (
                "After signing in, MediaCrate sends you wherever you asked "
                "to go via a `next` parameter on the login page. It never "
                "checks that 'wherever' is still MediaCrate.\n\n"
                "**Target:** `http://{container_ip}/login`"
            ),
            "challenge_type": "flag",
            "difficulty": "easy",
            "category": "web",
            "tags": ["open-redirect", "auth"],
            "skills": ["open redirect", "phishing-flow analysis"],
            "points": 100,
            "estimated_minutes": 10,
            "flags": [
                {
                    "value": "FLAG{mc_open_redirect_login_next}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "The login form posts a hidden `next` field. Try setting it to a full external URL before logging in.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "POST /login with next=http://evil.example.com and valid credentials. Check the response headers on the redirect.",
                    "cost": 25,
                },
            ],
        },
        {
            "slug": "mc-jwt-alg-none-admin",
            "title": "Trust, But Don't Verify",
            "description": (
                "Your profile can mint a developer API token — a JWT — for "
                "scripting against the `/api/v1/` endpoints. The verifier on "
                "the other end decides whether to check the signature based "
                "on what the token's own header claims its algorithm is.\n\n"
                "**Target:** `http://{container_ip}/api/v1/admin/secrets`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["jwt", "broken-auth", "alg-none"],
            "skills": ["JWT forging", "alg=none attack", "Bearer auth"],
            "points": 350,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{mc_jwt_alg_none_admin}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "GET /api/v1/auth/token while logged in to see a legitimate token's shape: header.payload.signature, each base64url.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": 'Decode the header and payload. Try rebuilding a token with {"alg":"none"} in the header, a payload claiming role: admin, and an empty signature segment.',
                    "cost": 75,
                },
                {
                    "order_num": 3,
                    "content": "Send it as `Authorization: Bearer <header>.<payload>.` (trailing dot, empty third segment) to /api/v1/admin/secrets.",
                    "cost": 100,
                },
            ],
        },
        {
            "slug": "mc-credential-reuse-pivot",
            "title": "One Password, Two Platforms",
            "description": (
                "Sequential ids are still sequential past the ones you've "
                "already found. An unlisted personal vlog from creator id 2 "
                "(Nova Plays) admits to a habit that doesn't stay contained "
                "to MediaCrate.\n\n"
                "This challenge is **cross-lab**: it only pays off if "
                "Limelight (lab id 7) is also running. Start it with "
                "`./octorig.sh start limelight` alongside MediaCrate.\n\n"
                "**Target:** `http://{container_ip}/videos/11`"
            ),
            "challenge_type": "flag",
            "difficulty": "hard",
            "category": "web",
            "tags": ["cross-lab", "idor", "credential-reuse"],
            "skills": ["IDOR enumeration", "credential reuse", "cross-application pivoting"],
            "points": 300,
            "estimated_minutes": 30,
            "flags": [
                {
                    "value": "FLAG{mc_credential_reuse_pivot}",
                    "flag_type": "static",
                    "case_sensitive": False,
                }
            ],
            "hints": [
                {
                    "order_num": 1,
                    "content": "You already know /videos/<id> has no visibility check. Keep enumerating past the ids you've already found.",
                    "cost": 0,
                },
                {
                    "order_num": 2,
                    "content": "Video 11's notes mention a password reused on a Limelight bookings account. Start the Limelight lab (id 7) and try logging in with it there.",
                    "cost": 50,
                },
                {
                    "order_num": 3,
                    "content": "Username nova.lee, password Popcorn21! on Limelight. Check that account's own profile after logging in.",
                    "cost": 75,
                },
            ],
        },
        {
            "slug": "mc-insane-chain-rce",
            "title": "Total Platform Compromise",
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
                    "value": "FLAG{mc_insane_chained_rce}",
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
