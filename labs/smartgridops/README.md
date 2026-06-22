<!-- Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not -->
# SmartGridOps — Smart City Power Grid Control

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

**Author of this lab:** roc1t1z3not — https://github.com/roc1t1z3not

SmartGridOps is a deliberately vulnerable IoT energy / smart-city SCADA control dashboard. Operators manage distribution **zones**, field **devices** (transformers, reclosers, EV chargers, inverters), smart **meters**, demand-response **energy credits**, and an **MQTT** command bus. Almost every operational feature trusts its input.

> Do not connect this to real grid hardware or expose it on a public network.

---

## What to Try

- **Device status poller** — `/devices/poll` fetches a URL server-side and reflects the body back. Where else might that reach?
- **Device controls** — `/devices/<id>/reboot` and `/devices/<id>/config-push` talk to the management target in a way that trusts its input more than it should.
- **Device API** — `/api/device/*` is gated by a token. Where might that token be lying around?
- **IDOR** — `/zones/<id>` and `/meters/<id>` are fetched with no ownership check.
- **Business logic** — `/credits` transfers are worth testing at the edges of what they expect.
- **MQTT / IoT** — `/mqtt` lets you set the publish topic. What happens if you target someone else's?
- **Bonus** — the login form trusts more than it should, and `?next=` isn't validated either.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start smartgridops

# Stop
./octorig.sh stop smartgridops
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Control-room home |
| `GET /dashboard` | Grid overview |
| `GET/POST /devices/poll` | Device status poller (SSRF) |
| `POST /devices/<id>/reboot` | Reboot via shell ping (cmd injection) |
| `POST /devices/<id>/config-push` | Config push (cmd injection) |
| `GET /zones/<id>` | Zone detail (IDOR) |
| `GET /meters/<id>` | Meter detail (IDOR) |
| `GET/POST /credits` | Energy credit transfers (business logic) |
| `GET/POST /mqtt` | MQTT command dispatch (topic injection) |
| `GET /api/device/list` | Device API (hardcoded token) |
| `GET /api/admin/operators` | Operator dump (admin token) |
| `GET /admin` | Operator roster (admin only) |
| `GET /robots.txt` | Hints |

---

## Flags

Flags follow the `FLAG{sgo_*}` convention and are planted across the database, files, FTP, and the vulnerable flows (SSRF, command injection, IDOR, business logic, MQTT injection, recon).

---

## License

Licensed under the [AGPLv3](../../LICENSE).
