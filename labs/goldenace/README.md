# GoldenAce

[![License](https://img.shields.io/badge/License-AGPLv3-green.svg)](../../LICENSE)
[![Backend](https://img.shields.io/badge/Backend-SQLite-blue.svg)](.)
[![OctoRig](https://img.shields.io/badge/OctoRig-Lab-purple.svg)](https://github.com/CommonHuman-Lab/OctoRig)

The house always wins — unless you know where the vulnerabilities are. GoldenAce is a deliberately vulnerable online casino with live slots, blackjack, roulette, and dice alongside a broken promo system, a chat room with no XSS filter, and an admin panel that forgets to check who's asking.

> Do not expose this service on a public network.

---

## What to Try

- The **slot machine** at `/slots/spin` takes the bet amount straight from the POST body. What happens at the edges of what it expects?
- The promo code endpoint at `/promo` doesn't verify whether you've already redeemed the same code.
- The leaderboard at `/leaderboard` takes `?q=` — see how it's handled on the way in and on the way back out.
- Player suites are at `/suite/<user_id>`. Is there anything stopping you from viewing any player's private profile by incrementing the ID?
- The live casino chat at `/chat` stores messages raw. Post something and wait for another player — or the admin — to load the page.
- The `/admin` panel checks if you're logged in, but not whether you're actually an admin.

---

## Quick Start

```bash
# From the OctoRig root
./octorig.sh start goldenace

# Stop
./octorig.sh stop goldenace
```

---

## Key Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /lobby` | Casino lobby with live feed |
| `GET /slots` | Slot machine |
| `GET /blackjack` | Blackjack table |
| `GET /roulette` | Roulette |
| `GET /dice` | Dice game |
| `GET /leaderboard` | Player leaderboard |
| `GET /suite/<id>` | Player suite / profile |
| `GET /promo` | Promo code redemption |
| `GET /chat` | Live casino chat |
| `GET /admin` | Admin panel |
| `GET /robots.txt` | Hints for further exploration |

---

## License

Licensed under the [AGPLv3](../../LICENSE).
