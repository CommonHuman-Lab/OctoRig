# Rewind Range

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

Be kind, rewind — then exploit. Rewind Range is a deliberately vulnerable retro VHS and video-game store brimming with 80s and 90s nostalgia, SQL injection across every filter, broken object-level access on private messages, and reflected script execution hiding in plain sight.

> Do not expose this service on a public network.

---

## What to Try

- The `/browse` endpoint accepts `genre`, `platform`, `type`, and `year` query parameters. How are they handled?
- The `/search` endpoint reflects `?q=` back into the page. Does it escape your input before rendering?
- Private messages are at `/inbox/<id>`. Does the server verify you're the intended recipient, or is sequential enumeration enough?
- The feedback board stores user submissions. Is the content sanitised before it's displayed to the next visitor?
- `/vhs-vault`, `/late-fees`, and `/manager-office` are disallowed in `robots.txt`. Worth a look.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start rewind

# Stop
./octorig.sh stop rewind
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Store front |
| `GET /browse` | Browse by genre, type, platform, year |
| `GET /search` | Product search |
| `GET /inbox` | Private message inbox |
| `GET /inbox/<id>` | Message detail |
| `GET /feedback` | Community feedback board |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
