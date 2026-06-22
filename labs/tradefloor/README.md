# TradeFloor

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

It's 1999. The dot-com bubble hasn't burst yet, and TradeFloor hasn't heard of CSRF tokens, parameterised queries, or output encoding. A deliberately vulnerable Y2K-era stock trading terminal where live ticking prices share a page with stored XSS, cross-site request forgery, and SQL injection.

> Do not expose this service on a public network.

---

## What to Try

- The trade form at `/trade` has no CSRF token. Can you craft an external page that places an order on behalf of a logged-in victim?
- The `?symbol=` pre-fill parameter on `/trade` is worth a closer look before the POST even happens.
- The trade memo field is stored raw. What fires in the admin's browser the next time they view it?
- The `/filings` search handles `?q=` the same way on the way in and the way back out.
- Portfolio holdings are fetched by ID. Is there an ownership check stopping you from viewing another trader's positions?
- `/trading-engine`, `/settlement`, and `/compliance-logs` are disallowed in `robots.txt`. Worth a look.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start tradefloor

# Stop
./octorig.sh stop tradefloor
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Trading dashboard |
| `GET /trade` | Place a trade |
| `GET /portfolio` | Portfolio holdings |
| `GET /filings` | Company filing search |
| `GET /filings/<id>` | Filing detail |
| `GET /watchlist` | Watchlist |
| `GET /alerts` | Price alerts |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
