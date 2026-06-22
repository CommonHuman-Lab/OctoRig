# HumanBank

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A deliberately vulnerable online banking application packed with real-world auth flaws, broken access control, and injection vulnerabilities. Manage accounts, wire transfers, and support tickets — or own them all.

> Do not expose this service on a public network.

---

## What to Try

- The login form trusts user input more than it should — and the error messages might tell you more than they intend to.
- Password reset tokens aren't quite as random as they look.
- Browse to `/accounts` while logged in as a regular user. Does it show only your own account?
- Support tickets have sequential integer IDs at `/tickets/<id>`. Does the server check that the ticket belongs to you?
- The transaction filter on `/accounts/<id>/transactions` takes several parameters — see how each one is used.
- `/vault`, `/wire-transfers`, and `/audit-log` are hidden from crawlers. What's inside?

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start humanbank

# Stop
./octorig.sh stop humanbank
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Landing page |
| `GET /dashboard` | Account dashboard |
| `GET /accounts` | Account list |
| `GET /accounts/<id>` | Account detail |
| `GET /accounts/<id>/transactions` | Transaction history (filterable) |
| `GET /tickets` | Support tickets |
| `GET /tickets/<id>` | Ticket detail |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
