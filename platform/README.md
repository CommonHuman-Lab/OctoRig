# OctoRig Platform

A self-hosted offensive security training platform built on top of OctoRig's vulnerable lab infrastructure. It adds CTF-style challenge competitions, achievement badges, user profiles, a content creator workflow, and a plugin marketplace — all API-driven and deployable with a single `docker compose up`.

---

## Features

- **CTF Events** — time-boxed competitions, static or dynamic scoring, solo or team play
- **Challenges** — markdown descriptions, file attachments, hints, flag validation, linked to live lab endpoints
- **Badges and Ranks** — award badges for solves and participation, configure rank thresholds
- **Plugin API** — DAST scanners register via the `octorig.plugins` entry point and are discovered automatically
- **Assessment Mode** — proctored, time-boxed skills testing

---

## Requirements

- Docker and Docker Compose

---

## Quick Start

```bash
cd platform
cp .env.example .env          # set ADMIN_USERNAME, ADMIN_PASSWORD, SECRET_KEY
docker compose up -d
```

---

## Access

| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API docs | http://localhost:8000/docs |

The admin account is created automatically on first boot using the credentials in `.env`.

---

## Configuration

Key environment variables (set in `.env`):

- `ADMIN_USERNAME` — initial admin account username
- `ADMIN_PASSWORD` — initial admin account password
- `ADMIN_EMAIL` — initial admin account email
- `SECRET_KEY` — JWT signing secret (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS` — comma-separated list of allowed frontend origins (default: `http://localhost:3000`)
- `STORAGE_BACKEND` — `local` (default) or `s3` for challenge file attachments

---

## Stopping

```bash
docker compose down       # stop containers, keep data volumes
docker compose down -v    # stop containers and wipe all data
```

---

## Connecting OctoRig Labs

The platform integrates directly with OctoRig labs. Start a lab from the parent directory and it will appear in the Labs section of the dashboard:

```bash
cd ..
./octorig.sh start 8    # BreachSQL fire-range (SQLi challenges)
./octorig.sh start 9    # StingXSS fire-range (XSS challenges)
```

Challenge scores from the fire-ranges feed into the platform's global scoreboard and badge engine.

---

## Importing Fire-Range Challenges

After starting the platform, import the built-in challenge sets:

```bash
docker compose exec backend python scripts/import_firerange_challenges.py
docker compose exec backend python scripts/import_firerange_challenges.py --dry-run   # preview only
docker compose exec backend python scripts/import_firerange_challenges.py --lab breachsql --reset
```
