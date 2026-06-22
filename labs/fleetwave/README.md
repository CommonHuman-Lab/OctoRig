<!-- Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not -->
# FleetWave — Fleet & Delivery Management

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

**Author of this lab:** roc1t1z3not — https://github.com/roc1t1z3not

FleetWave is a deliberately vulnerable logistics / delivery fleet-management SaaS — an internal dispatcher console (DHL-internal-dashboard vibe) for shipments, depots, driver rosters, freight-credit billing, and carrier status checks. Nearly every operational feature trusts its input.

> Do not route real freight or expose this on a public network.

---

## What to Try

- **Recon** — anonymous FTP drops more than you'd expect in `pub/`.
- **Login** — the sign-in form trusts your username more than it should.
- **Search** — `/shipments/search` has the same weak spot as the login form.
- **Shipments** — `/shipments/<id>` has no ownership check. Walk the ids.
- **Depot manifests** — `/depots/<id>` exposes restricted notes — is access actually enforced?
- **Driver roster** — `/admin/driver-roster` checks only that you're logged in, not that you're an admin.
- **Review queue** — a delivery-issue report note ends up rendered in `/admin/review`. How carefully?
- **Profile** — compare what the form shows you to what the update endpoint actually accepts.
- **Billing** — freight-credit transfers are worth testing at the edges of what they expect.
- **The deep chain** — a privileged feature fetches a URL server-side. Where else might that reach?

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start fleetwave

# Stop
./octorig.sh stop fleetwave
```

---

## License

Licensed under the [AGPLv3](../../LICENSE).
