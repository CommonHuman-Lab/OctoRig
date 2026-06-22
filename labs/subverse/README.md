<!-- Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not -->
# SubVerse

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

**Author of this lab:** roc1t1z3not — https://github.com/roc1t1z3not

A Reddit-like community forum, deliberately broken from the login form down. Posts, communities, comments, private messages, and a moderation log all share the same sloppy input handling — plus an SSH server and FTP drop with files nobody should have left lying around.

> Do not expose this service on a public network.

---

## What to Try

- The **login form** trusts your input more than it should.
- **Search** shows up in three places — `/search`, `/communities`, `/api/search`. Same weak spot, three doors in.
- Draft posts at `/post/<id>/draft` check that you're logged in, but not that the draft is yours.
- Private messages at `/messages/<id>` are just numbers. Whose inbox can you read by counting up?
- Edit your **profile** and compare what the form shows you to what actually gets saved.
- The link preview feature fetches a URL on the server's behalf — what else might it fetch?
- Votes on posts and comments fire from a plain link. No confirmation needed.
- Avatar uploads only check one thing about the file, and it isn't the contents.
- Admins can post community announcements. If you can reach that form, see what it actually renders.
- There's more to find — `/robots.txt` and the lab's FTP drop are good places to start.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start subverse

# Stop
./octorig.sh stop subverse
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Hot/new posts feed |
| `GET /search` | Search posts |
| `GET /post/<id>` | View post and comments |
| `GET /post/<id>/draft` | View a draft post |
| `POST /post/preview-link` | Server-side fetch of a link preview |
| `GET /communities` | Browse communities |
| `GET /community/<name>/modlog` | Community moderation log |
| `GET /messages/<id>` | View a private message |
| `GET /user/<username>` | Public profile |
| `POST /profile/avatar` | Upload a profile avatar |
| `GET /admin/community/<name>/announce` | Post a community announcement |
| `GET /api/internal` | Internal user data dump |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
