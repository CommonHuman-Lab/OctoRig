#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# OctoRig — Security Lab Manager
# Spin up / tear down vulnerable security lab environments via Docker
# =============================================================================

set -euo pipefail

trap 'echo ""; info "Caught interrupt — exiting OctoRig."; exit 0' INT

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LABS_DIR="${SCRIPT_DIR}/labs"
PLATFORM_DIR="${SCRIPT_DIR}/platform"

# ---------------- colours / output helpers -----------------------------------
RED='\033[0;31m'
GREEN='\033[38;5;46m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

good()  { echo -e "  ${GREEN}[+]${RESET} $*"; }
bad()   { echo -e "  ${RED}[-]${RESET} $*"; }
info()  { echo -e "  ${GRAY}[*]${RESET} $*"; }
warn()  { echo -e "  ${YELLOW}[!]${RESET} $*"; }
header(){ echo -e "\n  ${GREEN}${BOLD}$*${RESET}"; }

# ---------------- self-update ------------------------------------------------
update_self() {
  if ! command -v git &>/dev/null; then
    return
  fi
  if [[ ! -d "${SCRIPT_DIR}/.git" ]]; then
    return
  fi
  if ! git -C "${SCRIPT_DIR}" diff --quiet || \
     ! git -C "${SCRIPT_DIR}" diff --cached --quiet || \
     [[ -n "$(git -C "${SCRIPT_DIR}" ls-files --others --exclude-standard)" ]]; then
    info "Skipping self-update: local changes detected."
    return
  fi
  info "Checking for updates..."
  if git -C "${SCRIPT_DIR}" pull --ff-only --quiet 2>/dev/null; then
    good "Up to date."
  else
    warn "Self-update failed (non-fast-forward or remote issue). Continuing."
  fi
}

# ---------------- lab registry -----------------------------------------------
# Format: "ID|NAME|SCRIPT|DESCRIPTION"
LABS=(
  "1|Rewind|rewindrange.sh|Retro video and games store — SQLi, XSS, IDOR, SSH/FTP weak creds"
  "2|TradeFloor|tradefloor.sh|Vulnerable trading portal — XXE, CSRF, mass assignment, SQLi, IDOR, stored XSS, SSH/FTP"
  "3|GoldenAce|goldenace.sh|Vulnerable online casino — SQLi, IDOR, stored XSS, CSRF, business logic, JWT alg:none, SSH/FTP"
  "4|HumanBank|humanbank.sh|Vulnerable online banking app — SQLi, IDOR, XSS, auth flaws, file upload, business logic, SSH/FTP"
  "5|MediHuman|medihuman.sh|Vulnerable healthcare patient portal — SQLi, IDOR, XSS, file upload, SSH/FTP weak creds"
  "6|NetPulse|netpulse.sh|Vulnerable 90s ISP portal — SSRF, SSTI, command injection, open redirect, SQLi, IDOR, XSS, SSH/FTP"
  "7|Limelight|limelight.sh|Vulnerable cinema booking app — SQLi, XSS, IDOR, CSRF, SSTI, business logic, mass assignment, SSH/FTP"
  "8|SubVerse|subverse.sh|SubVerse — Reddit-like community forum — SQLi, XSS, IDOR, CSRF, SSTI, command injection, mass assignment, file upload, SSH/FTP"
  "9|BreachSQL|breachsql.sh|Tiered SQL injection challenges (T1-T5) for SQLi practice"
  "10|StingXSS|stingxss.sh|Tiered XSS challenges (T1-T8) for XSS injection practice"
  "11|VaultGate|vaultgate.sh|IDOR challenges for benchmarking"
  "12|VaultRip|vaultriprange.sh|SSH credential-rich target for VaultRip passive and remote harvesting"
  "13|Juice Shop|juiceshop.sh|OWASP Juice Shop - OWASP Top 10 web vulnerabilities"
  "14|DVWA|dvwa.sh|Damn Vulnerable Web App - PHP/MySQL classic"
  "15|Metasploitable2|metasploitable.sh|Linux VM with intentionally vulnerable services"
  "16|WebGoat|webgoat.sh|OWASP WebGoat - PortSwigger-style lesson-based labs"
  "17|VulnAD|vulnad.sh|Vulnerable Active Directory - Samba4 AD with AD attack paths"
  "18|SmartGridOps|smartgridops.sh|Vulnerable IoT smart-city power-grid control dashboard — SSRF, command injection, hardcoded device tokens, IDOR, business logic, MQTT/IoT injection, SSH/FTP"
  "19|VaultSync|vaultsync.sh|Vulnerable password manager SaaS — SQLi, IDOR, XSS, BAC, mass assignment, SSRF chained to command injection, SSH/FTP weak creds"
  "20|MediaCrate|mediacrate.sh|Vulnerable streaming/content-creator platform — SQLi, IDOR, XSS, BAC, mass assignment, SSRF chained to command injection, SSH/FTP weak creds"
  "21|FleetWave|fleetwave.sh|Vulnerable logistics/delivery fleet SaaS — SQLi, IDOR, BAC, stored XSS, mass assignment, business logic, SSRF chained to command injection, SSH/FTP weak creds"
  "22|Waveform|waveform.sh|Vulnerable indie music-streaming SPA — SQLi, DOM/stored XSS, IDOR, broken access control, session forgery, SSH/FTP weak creds"
)

# IDs of real-world scenario labs (for "start world")
WORLD_LAB_IDS=(1 2 3 4 5 6 7 8 18 19 20 21 22)

# ---------------- dependency checks ------------------------------------------
install_docker() {
  warn "Docker not found — attempting to install..."
  if [[ $EUID -ne 0 ]]; then
    bad "Root privileges required to install Docker. Re-run with sudo."
    exit 1
  fi
  apt-get update -qq
  apt-get install -y -qq docker.io
  systemctl enable --now docker
  if ! command -v docker &>/dev/null; then
    bad "Docker installation failed. Install it manually: apt install docker.io"
    exit 1
  fi
  good "Docker installed successfully"
}

check_docker() {
  if ! command -v docker &>/dev/null; then
    install_docker
  fi
  if ! docker info &>/dev/null 2>&1; then
    info "Docker daemon is not running — attempting to start it..."
    if [[ $EUID -ne 0 ]]; then
      sudo systemctl start docker 2>/dev/null || { bad "Failed to start Docker daemon. Try: sudo systemctl start docker"; exit 1; }
    else
      systemctl start docker 2>/dev/null || { bad "Failed to start Docker daemon. Try: systemctl start docker"; exit 1; }
    fi
    sleep 2
    if ! docker info &>/dev/null 2>&1; then
      bad "Docker daemon still not running after start attempt."
      exit 1
    fi
  fi
  good "Docker is running"
}

# ---------------- banner ------------------------------------------------------
banner() {
  echo ""
  echo -e "${GREEN}${BOLD}"
  echo "   ____       __        ____  _      "
  echo "  / __ \_____/ /_____  / __ \(_)___ _"
  echo " / / / / ___/ __/ __ \/ /_/ / / __ \`/"
  echo "/ /_/ / /__/ /_/ /_/ / _, _/ / /_/ / "
  echo "\____/\___/\__/\____/_/ |_/_/\__, /  "
  echo "                            /____/   "
  echo -e "${RESET}"
  echo -e "  ${BOLD}OctoRig — Security Lab Manager${RESET} — Docker-based vulnerable environment launcher"
  echo ""
}

# ---------------- list labs ---------------------------------------------------
list_labs() {
  header "Available Labs"
  echo ""
  printf "  ${BOLD}%-4s %-20s %s${RESET}\n" "ID" "NAME" "DESCRIPTION"
  echo "  ─────────────────────────────────────────────────────────────────────"
  for entry in "${LABS[@]}"; do
    IFS='|' read -r id name _script desc <<< "$entry"
    printf "  ${GREEN}%-4s${RESET} ${BOLD}%-20s${RESET} ${GRAY}%s${RESET}\n" "$id" "$name" "$desc"
  done
  echo ""
}

# ---------------- status of all running labs ----------------------------------
status_all() {
  header "Running Lab Containers"
  echo ""
  local running
  running=$(docker ps --filter "name=octorig-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || true)
  if [[ -z "$running" ]] || [[ "$running" == *"NAMES"$'\n' ]]; then
    info "No OctoRig lab containers are currently running."
  else
    echo "$running" | sed 's/^/  /'
  fi
  echo ""
}

# ---------------- dispatch to a lab script ------------------------------------
dispatch() {
  local action="$1"
  local query="$2"

  local matched="" matched_name=""

  if [[ "$query" =~ ^[0-9]+$ ]]; then
    for entry in "${LABS[@]}"; do
      IFS='|' read -r lid lname lscript _desc <<< "$entry"
      if [[ "$lid" == "$query" ]]; then
        matched="$lscript"; matched_name="$lname"; break
      fi
    done
  else
    local qnorm
    qnorm=$(echo "$query" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
    for entry in "${LABS[@]}"; do
      IFS='|' read -r _lid lname lscript _desc <<< "$entry"
      local nnorm
      nnorm=$(echo "$lname" | tr '[:upper:]' '[:lower:]' | tr -cd '[:alnum:]')
      if [[ "$nnorm" == "$qnorm"* ]]; then
        matched="$lscript"; matched_name="$lname"; break
      fi
    done
  fi

  if [[ -z "$matched" ]]; then
    bad "Unknown lab: $query"
    echo ""
    list_labs
    exit 1
  fi

  local script_path="${LABS_DIR}/${matched}"
  if [[ ! -f "$script_path" ]]; then
    bad "Lab script not found: $script_path"
    exit 1
  fi

  bash "$script_path" "$action"
}

# ---------------- start all / stop all ----------------------------------------
all_action() {
  local action="$1"
  if [[ "$action" == "stop" ]]; then
    local stopped=()
    for entry in "${LABS[@]}"; do
      IFS='|' read -r _id name lscript _desc <<< "$entry"
      [[ -f "${LABS_DIR}/${lscript}" ]] || continue
      # Check if any of this lab's containers are actually running (not just exited).
      local cnames was_running=false
      cnames=$(grep -oP '(?<==")(octorig-[^"]+)(?=")' "${LABS_DIR}/${lscript}" 2>/dev/null | sort -u)
      while IFS= read -r cname; do
        [[ -z "$cname" ]] && continue
        if docker ps --filter "name=^${cname}$" --format "{{.Names}}" 2>/dev/null | grep -q "^${cname}$"; then
          was_running=true
          break
        fi
      done <<< "$cnames"
      bash "${LABS_DIR}/${lscript}" stop &>/dev/null
      [[ "$was_running" == true ]] && stopped+=("$name")
    done
    if [[ ${#stopped[@]} -eq 0 ]]; then
      info "No labs were running."
    else
      good "Stopped: $(IFS=', '; echo "${stopped[*]}")"
    fi
  else
    local failed=()
    for entry in "${LABS[@]}"; do
      IFS='|' read -r id name lscript _desc <<< "$entry"
      header "${action^}: $name"
      if ! bash "${LABS_DIR}/${lscript}" "$action"; then
        warn "Failed to $action $name — rolling back"
        bash "${LABS_DIR}/${lscript}" stop &>/dev/null || true
        failed+=("$name")
      fi
    done
    if [[ ${#failed[@]} -gt 0 ]]; then
      bad "Failed to $action: $(IFS=', '; echo "${failed[*]}")"
      return 1
    fi
  fi
}

# ---------------- start real-world labs in parallel ---------------------------
start_world() {
  local parallel_limit="${OCTORIG_PARALLEL_LIMIT:-4}"
  header "Starting all real-world labs (up to ${parallel_limit} at a time)..."
  echo ""

  local tmpdir
  tmpdir=$(mktemp -d)
  local pids=() names=() lids=() lscripts=()

  local queued=()
  for entry in "${LABS[@]}"; do
    IFS='|' read -r lid lname lscript _desc <<< "$entry"
    local is_world=false
    for wid in "${WORLD_LAB_IDS[@]}"; do
      [[ "$lid" == "$wid" ]] && is_world=true && break
    done
    [[ "$is_world" == false ]] && continue
    [[ ! -f "${LABS_DIR}/${lscript}" ]] && continue
    queued+=("$entry")
  done

  local all_ok=true
  local batch_start=0
  while (( batch_start < ${#queued[@]} )); do
    pids=(); names=(); lids=(); lscripts=()
    local batch_end=$(( batch_start + parallel_limit ))
    (( batch_end > ${#queued[@]} )) && batch_end=${#queued[@]}

    local j
    for (( j = batch_start; j < batch_end; j++ )); do
      IFS='|' read -r lid lname lscript _desc <<< "${queued[$j]}"
      info "Queuing: $lname"
      bash "${LABS_DIR}/${lscript}" start > "${tmpdir}/${lid}.log" 2>&1 &
      pids+=($!)
      names+=("$lname")
      lids+=("$lid")
      lscripts+=("$lscript")
    done

    echo ""
    info "${#pids[@]} labs launching in this batch — waiting for them to come up..."
    echo ""

    local i
    for i in "${!pids[@]}"; do
      local pid="${pids[$i]}" name="${names[$i]}" lid="${lids[$i]}" lscript="${lscripts[$i]}"
      if wait "$pid"; then
        good "$name is up"
      else
        bad "$name failed to start — rolling back"
        bash "${LABS_DIR}/${lscript}" stop &>/dev/null || true
        all_ok=false
      fi
      cat "${tmpdir}/${lid}.log"
      echo ""
    done

    batch_start=$batch_end
  done

  rm -rf "$tmpdir"

  if [[ "$all_ok" == true ]]; then
    good "All real-world labs are running."
  else
    bad "Some labs failed to start — rolled back and check output above."
    return 1
  fi
}

# ---------------- platform (docker compose) -----------------------------------
_dc() {
  docker compose -f "${PLATFORM_DIR}/docker-compose.yml" --project-directory "${PLATFORM_DIR}" "$@"
}

_platform_env_get() {
  local key="$1" file="${PLATFORM_DIR}/.env" line val
  [[ -f "$file" ]] || return 1
  line="$(grep -E "^${key}=" "$file" | tail -1)"
  [[ -z "$line" ]] && return 1
  val="${line#*=}"
  val="${val%%#*}"
  val="$(printf '%s' "$val" | sed -e 's/[[:space:]]*$//')"
  printf '%s' "$val"
}

_platform_env_check() {
  if [[ ! -f "${PLATFORM_DIR}/.env" ]]; then
    warn "No .env found in platform/. Copying .env.example — you must set required values before starting."
    cp "${PLATFORM_DIR}/.env.example" "${PLATFORM_DIR}/.env"
  fi

  local missing=() key val
  for key in POSTGRES_PASSWORD SECRET_KEY ADMIN_PASSWORD; do
    val="$(_platform_env_get "$key")"
    [[ -z "$val" ]] && missing+=("$key")
  done

  if (( ${#missing[@]} > 0 )); then
    bad "platform/.env is missing required values: ${missing[*]}"
    info "Edit platform/.env and set:"
    info "  POSTGRES_PASSWORD  — strong random password"
    info "  SECRET_KEY         — 32+ random chars, e.g. openssl rand -hex 32"
    info "  ADMIN_PASSWORD     — strong password (not 'changeme', 'admin', etc.)"
    return 1
  fi
}

platform_action() {
  local subcmd="${1:-help}"
  local extra="${2:-}"

  case "$subcmd" in
    start)
      _platform_env_check || return 1
      check_docker
      info "Starting platform..."
      _dc --progress quiet --profile ui up -d --build
      # Wait for the API to be reachable
      info "Waiting for API to be ready..."
      local deadline=$(( $(date +%s) + 60 ))
      while (( $(date +%s) < deadline )); do
        if curl -sf http://localhost:8000/api/v1/system/health &>/dev/null; then
          break
        fi
        sleep 1
      done
      good "Platform is up"
      echo ""
      echo -e "  ${BOLD}Dashboard${RESET}  →  ${GREEN}http://localhost:3000${RESET}"
      echo -e "  ${BOLD}API docs${RESET}   →  ${GREEN}http://localhost:8000/docs${RESET}"
      echo ""
      ;;
    stop)
      info "Stopping platform..."
      _dc --profile ui down
      good "Platform stopped (data volumes preserved)"
      ;;
    restart)
      _platform_env_check || return 1
      info "Restarting platform..."
      _dc --profile ui down
      _dc --progress quiet --profile ui up -d --build
      good "Platform restarted"
      ;;
    wipe)
      warn "This will DELETE all platform data (database, caches). Type 'yes' to confirm:"
      read -r confirm
      if [[ "$confirm" != "yes" ]]; then
        info "Aborted."
        return
      fi
      info "Wiping platform..."
      _dc --profile ui down -v
      good "Platform stopped and volumes removed"
      ;;
    status)
      info "Platform Service Status"
      echo ""
      _dc ps 2>/dev/null || info "Platform is not running."
      echo ""
      ;;
    logs)
      local svc="${extra:-}"
      if [[ -n "$svc" ]]; then
        _dc logs -f --tail=100 "$svc"
      else
        _dc logs -f --tail=50
      fi
      ;;
    import)
      info "Running fire-range challenge import..."
      _dc exec backend python scripts/import_firerange_challenges.py "${extra}"
      ;;
    help|*)
      echo ""
      echo -e "  ${BOLD}platform commands:${RESET}"
      echo -e "  ${GREEN}platform start${RESET}          — Start API + workers + frontend UI"
      echo -e "  ${GREEN}platform stop${RESET}           — Stop all platform services"
      echo -e "  ${GREEN}platform restart${RESET}        — Rebuild and restart platform"
      echo -e "  ${GREEN}platform wipe${RESET}           — Stop and delete all data volumes"
      echo -e "  ${GREEN}platform status${RESET}         — Show platform container status"
      echo -e "  ${GREEN}platform logs [service]${RESET} — Tail platform logs"
      echo -e "  ${GREEN}platform import${RESET}         — Import fire-range challenges into platform DB"
      echo ""
      ;;
  esac
}

# ---------------- interactive menu --------------------------------------------
interactive_menu() {
  list_labs
  echo -e "  ${BOLD}Commands:${RESET}"
  echo -e "  ${GREEN}start <id|name>${RESET}    — Start a lab by ID or name (e.g. start 3, start goldenace)"
  echo -e "  ${GREEN}stop <id|name>${RESET}     — Stop a lab by ID or name"
  echo -e "  ${GREEN}restart <id|name>${RESET}  — Restart a lab by ID or name"
  echo -e "  ${GREEN}status${RESET}         — Show running lab containers"
  echo -e "  ${GREEN}start all${RESET}      — Start all labs"
  echo -e "  ${GREEN}start world${RESET}    — Start all real-world scenario labs in parallel"
  echo -e "  ${GREEN}stop all${RESET}       — Stop all labs"
  echo -e "  ${GREEN}restart all${RESET}    — Restart all labs"
  echo -e "  ${GREEN}list${RESET}           — List available labs"
  echo -e "  ${GREEN}platform <cmd>${RESET} — Manage the OctoRig training platform (start|stop|status|logs|wipe|import)"
  echo -e "  ${GREEN}quit${RESET}           — Exit"
  echo ""

  while true; do
    echo -ne "  ${BOLD}lab>${RESET} "
    read -r cmd arg1 arg2 || break
    case "$cmd" in
      start)
        check_docker
        if   [[ "${arg1:-}" == "all"   ]]; then all_action start
        elif [[ "${arg1:-}" == "world" ]]; then start_world
        else dispatch start "${arg1:-}"; fi ;;
      stop)
        if [[ "${arg1:-}" == "all" ]]; then all_action stop
        else dispatch stop "${arg1:-}"; fi ;;
      restart)
        check_docker
        if [[ "${arg1:-}" == "all" ]]; then all_action stop; all_action start
        else dispatch stop "${arg1:-}"; dispatch start "${arg1:-}"; fi ;;
      platform) platform_action "${arg1:-help}" "${arg2:-}" ;;
      status) status_all ;;
      list)   list_labs ;;
      quit|exit|q) info "Bye!"; exit 0 ;;
      "") ;;
      *) warn "Unknown command: $cmd — type 'quit' to exit" ;;
    esac
    echo ""
  done
}

# ---------------- main --------------------------------------------------------
update_self
banner

case "${1:-menu}" in
  menu)
    check_docker
    interactive_menu ;;
  list)
    list_labs ;;
  status)
    status_all ;;
  start)
    check_docker
    if   [[ "${2:-}" == "all"   ]]; then all_action start
    elif [[ "${2:-}" == "world" ]]; then start_world
    else dispatch start "${2:-}"; fi ;;
  stop)
    if [[ "${2:-}" == "all" ]]; then all_action stop
    else dispatch stop "${2:-}"; fi ;;
  restart)
    check_docker
    if [[ "${2:-}" == "all" ]]; then all_action stop; all_action start
    else dispatch stop "${2:-}"; dispatch start "${2:-}"; fi ;;
  platform)
    platform_action "${2:-help}" "${3:-}" ;;
  new-lab)
    python3 "$(dirname "${BASH_SOURCE[0]}")/labs/scaffold_lab.py" "${@:2}" ;;
  help|-h|--help)
    list_labs
    echo "Usage: $0 [menu|list|status|start <id|name|all|world>|stop <id|name|all>|restart <id|name|all>|platform <cmd>|new-lab]"
    echo "" ;;
  *)
    bad "Unknown command: ${1}"
    echo "Usage: $0 [menu|list|status|start <id|name|all|world>|stop <id|name|all>|restart <id|name|all>|platform <cmd>|new-lab]"
    exit 1 ;;
esac
