# MediaCrate

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A streaming and content-creator platform with channels, subscriber tiers, tips, and a thumbnail importer that trusts URLs a little too much. Chain enough of MediaCrate's flaws together and you can walk from an anonymous signup to executing commands inside the container.

> Do not expose this service on a public network.

---

## What to Try

- The **login form** trusts your username more than it should.
- **Video search** at `/videos/search` has the same weak spot.
- Videos are fetched by plain numeric ID at `/videos/<id>` and `/api/v1/videos/<id>` — visibility settings don't seem to matter.
- Subscriber-exclusive content at `/channels/<id>/exclusive` only checks that you're logged in, not what tier you're on.
- `/admin/stream-keys` hands out stream credentials to anyone with a session — admin or not.
- Edit your **profile** and compare what the form shows you to what the update endpoint actually accepts.
- Privileged users can reach a feature that imports a thumbnail from any URL, server-side. Where else might that reach?
- The token issuer trusts the client more than it should when it comes to how a token is signed.
- File paths under `/uploads/<channel_id>/<filename>` are built straight from your input — and tipping a channel doesn't check where the request came from.
- There's more to find — `/robots.txt` is a good place to start.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start mediacrate

# Stop
./octorig.sh stop mediacrate
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /dashboard` | Subscriptions and owned channel |
| `GET /videos/<id>` | View video and comments |
| `GET /videos/search` | Search public videos |
| `POST /videos/<id>/report` | Report video to admin review |
| `GET /channels/<id>` | Public channel videos |
| `GET /channels/<id>/exclusive` | Subscriber-tier exclusive content |
| `POST /channels/<id>/tip` | Tip a channel creator |
| `GET /uploads/<channel_id>/<filename>` | Channel banner / uploaded file |
| `GET /admin` | Admin dashboard |
| `GET /admin/stream-keys` | Live stream credentials |
| `GET /admin/review` | Admin review queue |
| `POST /api/admin/import-thumbnail` | Server-side thumbnail import (admin) |
| `GET /api/internal/transcode` | Internal transcode (localhost-only) |
| `GET /api/v1/auth/token` | Issue an API token |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
