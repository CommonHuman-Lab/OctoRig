# NetPulse Internet Services

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

Welcome to 1998. NetPulse is a deliberately vulnerable dial-up ISP customer portal packed with server-side injection, a network diagnostic toolbox that doesn't sanitise its inputs, and a syslog nobody was supposed to read.

> Do not expose this service on a public network.

---

## What to Try

- The **Link Checker** at `/tools/linkcheck` fetches a URL on the server's behalf. What else might it reach?
- The **DNS Lookup** tool at `/tools/dnslookup` shells out to resolve a hostname. What happens with unusual input?
- The login form has an unvalidated `?next=` redirect parameter — and trusts your input in more ways than one.
- Billing records and account pages use integer IDs. Is there an ownership check on each one?
- `/syslog`, `/billing-db`, and `/dialup-pool` are disallowed in `robots.txt`. Worth a look.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start netpulse

# Stop
./octorig.sh stop netpulse
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Portal home |
| `GET /dashboard` | Account dashboard |
| `POST /tools/linkcheck` | Link / URL checker |
| `POST /tools/dnslookup` | DNS lookup |
| `GET /billing` | Billing history |
| `GET /tickets` | Support tickets |
| `GET /board` | Community board |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
