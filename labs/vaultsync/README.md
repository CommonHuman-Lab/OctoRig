# VaultSync

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

A password-manager SaaS that can't quite keep its own secrets. VaultSync stores vaults, shared items, and a breach-check feature — chained together, they let you walk from an anonymous login straight to command execution inside the container.

> Do not expose this service on a public network.

---

## What to Try

- The **login form** trusts your username more than it should.
- **Vault search** at `/vaults/search` has the same weak spot — see what it leaks beyond titles.
- Vaults and items are fetched by plain numeric ID at `/vaults/<id>` and `/vaults/items/<id>` — and the API mirrors it. No ownership check in sight.
- `/admin/recovery-codes` only checks that you're logged in, not that you're an admin.
- Edit your **profile** and look closely at which fields the update actually accepts versus which ones the form shows you.
- Privileged users can reach a feature that fetches a URL on the server's behalf. Where else might that reach?
- Flag review notes at `/vaults/items/<id>/flag` are stored raw. What happens when an admin opens the review queue?
- There's more to find — `/robots.txt` is a good place to start.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start vaultsync

# Stop
./octorig.sh stop vaultsync
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /dashboard` | Owned and shared vaults |
| `GET /vaults/<id>` | Vault detail and items |
| `GET /vaults/items/<id>` | Single item detail |
| `GET /vaults/search` | Search vault items |
| `POST /vaults/items/<id>/flag` | Report an item to admin review |
| `GET /vaults/<id>/share` | Manage vault sharing |
| `GET /admin` | Admin dashboard |
| `GET /admin/recovery-codes` | Account recovery codes |
| `GET /admin/review` | Admin review queue |
| `POST /api/breach-check` | Server-side breach lookup (admin) |
| `GET /api/internal/vault-export` | Internal export (localhost-only) |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
