<p align="center">
  <img src="assets/octorig_logo.png" alt="OctoRig" width="200"/>
</p>

<h1 align="center">OctoRig</h1>
<p align="center"><em>Realistic vulnerable labs and a self-hosted CTF platform — events, badges, scoreboards — spun up with one command.</em></p>

<p align="center">
  <img src="https://img.shields.io/badge/Shell-Bash-green.svg" />
  <img src="https://img.shields.io/badge/Runtime-Docker-blue.svg" />
  <img src="https://img.shields.io/badge/focus-offensive--security-darkred.svg" />
</p>

---

OctoRig pairs 21 realistic, layered-vulnerability lab environments with a built-in training platform — CTF events, badges, scoreboards, and a plugin API for your own DAST tools. No artificial puzzle boxes: labs feel like real apps and infrastructure, mistakes and all.

## Features

- One-command deploy, fully isolated in Docker
- 21 labs — world scenarios, scanner fire-ranges, and classics (Juice Shop, DVWA, AD, more)
- Built-in CTF platform — events, badges, scoreboards, team play
- Assessment Mode for proctored skills testing
- Plugin API to wire in your own DAST scanners
- Hidden easter eggs and chained exploit paths

---

## Quick Start

```bash
git clone https://github.com/CommonHuman-Lab/OctoRig.git
cd OctoRig
./octorig.sh platform start      # API + workers + UI  →  http://localhost:3000
./octorig.sh platform stop       # stop platform services
```

Drive labs directly from the CLI instead:

```bash
./octorig.sh              # interactive menu
./octorig.sh start 1      # Start a specific lab
./octorig.sh start all    # Start all labs
./octorig.sh status       # Show running labs
./octorig.sh stop all     # Tear everything down
```

---

## Available Labs

OctoRig ships with multiple labs across three categories:

- **Real-world scenarios** — full-stack web apps (e-commerce, banking, healthcare, trading, ISP portal, casino, cinema, community forum) with layered, realistic vulnerability chains
- **Scanner fire-ranges** — purpose-built SQLi, XSS, and IDOR challenge sets for tool benchmarking and focused practice
- **Third-party classics** — Juice Shop, DVWA, Metasploitable2, WebGoat, and a Vulnerable Active Directory environment

Full lab list with IPs, credentials, and vulnerability details: [Labs Overview →](https://github.com/CommonHuman-Lab/OctoRig/wiki/Labs-Overview)

---

## Platform

The other half of OctoRig: a self-hosted CTF engine that runs alongside the labs.

- Time-boxed competitions, teams, and a global scoreboard fed by live fire-range scores
- Badges, ranks, and a challenge-creator workflow
- Plugin API for wiring in your own DAST scanners, plus proctored Assessment Mode

→ Full setup and feature breakdown: [platform/README.md](platform/README.md)

---

## Requirements

- Docker (daemon running)
- Bash 4.0+
- `nc` (netcat)
- Internet access on first run (image pulls)

---

## Legal & Ethical Use

OctoRig is intended for use in **isolated lab environments only**.

- Run on a dedicated machine or VM — never expose lab containers to a public network
- All labs contain intentionally vulnerable software — treat accordingly

---

## License

This project is dual-licensed.

### Community License (AGPL-3.0)

You may use, modify, and distribute this software under the terms of the GNU Affero General Public License v3.0 (AGPL-3.0).

If you distribute this software or make it available as a network service, you must comply with the requirements of the AGPL, including providing access to the corresponding source code.

### Commercial License

A separate commercial license is available for organizations that wish to use this software without the obligations of the AGPL, including proprietary products, closed-source services, OEM integrations, white-label solutions, or commercial redistribution.

For commercial licensing inquiries, contact the author.