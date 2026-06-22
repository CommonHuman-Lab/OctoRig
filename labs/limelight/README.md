# Limelight

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

The popcorn smells real. The vulnerabilities are too. Limelight is a deliberately vulnerable cinema booking platform where you can browse films, select seats, write reviews, and redeem gift cards — and where almost every feature has a flaw waiting to be found.

> Do not expose this service on a public network.

---

## What to Try

- The search bar at `/movies?q=` handles your input the same way on the way into the database and the way back out onto the page.
- Movie reviews are stored raw. Post something on any film's page and wait for someone else to load it.
- Booking references are sequential integers at `/booking/<id>`. Is there any check that the booking belongs to you?
- The API at `/api/booking/<id>` and `/api/user/<id>` — try them without logging in at all.
- Profile editing at `/profile/<user_id>` checks that you're logged in — but look closely at which fields the update actually accepts.
- Gift card redemption at `/gift` is worth a closer look.
- The `/admin` panel checks for a session but never verifies whether you're actually an admin.
- The announcement editor at `/admin/announce` renders your input through a template engine. What does that let you do?
- Login accepts a `?next=` redirect parameter — where can you send someone after they authenticate?
- Ticket price is submitted as a hidden field from the seat-selection form. What does the server actually trust?

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start limelight

# Stop
./octorig.sh stop limelight
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Now showing homepage |
| `GET /movies` | Browse and search films |
| `GET /movie/<id>` | Film detail, showtimes, and reviews |
| `GET /book/<showing_id>` | Seat selection map |
| `GET /booking/<id>` | View a booking (IDOR) |
| `GET /bookings` | My bookings |
| `GET /profile/<user_id>` | User profile (IDOR, mass assignment) |
| `GET /gift` | Gift card redemption (SQLi) |
| `GET /admin` | Admin panel (broken access control) |
| `GET /admin/announce` | Announcement editor (SSTI) |
| `GET /api/booking/<id>` | Booking API — no auth required |
| `GET /api/user/<id>` | User API — no auth required |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
