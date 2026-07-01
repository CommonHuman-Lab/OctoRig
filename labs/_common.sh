#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Shared helpers for lab scripts
# Source this file at the top of each lab script:
#   source "$(dirname "$0")/_common.sh"
# =============================================================================

RED='\033[0;31m'
GREEN='\033[38;5;46m'
YELLOW='\033[1;33m'
GRAY='\033[0;37m'
BOLD='\033[1m'
RESET='\033[0m'

# Per-container resource limits, applied by every lab's docker run invocation.
# Override on the host if needed, e.g. OCTORIG_LAB_MEM=1g OCTORIG_LAB_CPUS=2 ./octorig.sh start world
LAB_MEMORY="${OCTORIG_LAB_MEM:-512m}"
LAB_CPUS="${OCTORIG_LAB_CPUS:-1}"

good()  { echo -e "  ${GREEN}[+]${RESET} $*"; }
bad()   { echo -e "  ${RED}[-]${RESET} $*"; }
info()  { echo -e "  ${GRAY}[*]${RESET} $*"; }
warn()  { echo -e "  ${YELLOW}[!]${RESET} $*"; }
header(){ echo -e "\n  ${GREEN}${BOLD}[$LAB_NAME]${RESET} $*"; }

# Print a nicely boxed access card after lab start.
# Box width auto-sizes to the longest key+value pair.
access_card() {
  local -n _lines=$1          # nameref to an array of "KEY|VALUE" strings
  local gap=1  margin=2

  # --- measure widest key and value ---
  local max_key=0 max_val=0
  for line in "${_lines[@]}"; do
    IFS='|' read -r k v <<< "$line"
    (( ${#k} > max_key )) && max_key=${#k}
    (( ${#v} > max_val )) && max_val=${#v}
  done

  local key_w=$(( max_key < 10 ? 10 : max_key ))          # minimum 10
  local val_w=$(( max_val < 20 ? 20 : max_val ))          # minimum 20
  local inner=$(( margin + key_w + gap + val_w + margin )) # total inner chars
  local bar
  printf -v bar '%*s' "$inner" ''; bar="${bar// /─}"

  local title="ACCESS INFO — ${LAB_NAME}"
  local tpad
  printf -v tpad "%-${inner}s" "$title"

  echo ""
  echo -e "  ${GREEN}${BOLD}┌${bar}┐${RESET}"
  echo -e "  ${GREEN}${BOLD}│${RESET}  ${BOLD}${tpad}${RESET}${GREEN}${BOLD}│${RESET}"
  echo -e "  ${GREEN}${BOLD}├${bar}┤${RESET}"
  for line in "${_lines[@]}"; do
    IFS='|' read -r k v <<< "$line"
    local kpad vpad
    printf -v kpad "%-${key_w}s" "$k"
    printf -v vpad "%-${val_w}s" "$v"
    echo -e "  ${GREEN}${BOLD}│${RESET}  ${BOLD}${kpad}${RESET} ${vpad}  ${GREEN}${BOLD}│${RESET}"
  done
  echo -e "  ${GREEN}${BOLD}└${bar}┘${RESET}"
  echo ""
}

# Pull a Docker image with a spinner instead of raw layer output.
# Usage: docker_pull <image> [timeout_seconds]   (default timeout: 300s)
docker_pull() {
  local image="$1"
  local pull_timeout="${2:-300}"

  # Skip pull if image already exists locally
  if docker image inspect "$image" &>/dev/null; then
    good "Image ${image} ready (cached)"
    return 0
  fi

  info "Pulling image ${BOLD}${image}${RESET}..."
  local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
  local i=0
  docker pull "$image" &>/dev/null &
  local pid=$!
  local elapsed=0
  while kill -0 "$pid" 2>/dev/null; do
    printf "\r  ${GRAY}%s${RESET}  Downloading..." "${frames[$i]}"
    i=$(( (i+1) % ${#frames[@]} ))
    sleep 0.1
    elapsed=$(( elapsed + 1 ))
    if (( elapsed >= pull_timeout * 10 )); then
      kill "$pid" 2>/dev/null
      printf "\r\033[2K"
      bad "Timed out pulling ${image} (>${pull_timeout}s)"
      return 1
    fi
  done
  wait "$pid"
  local rc=$?
  printf "\r\033[2K"
  if [[ $rc -eq 0 ]]; then
    good "Image ${image} ready"
  else
    bad "Failed to pull image ${image}"
    return 1
  fi
}


wait_for_port() {
  local host="${1:-127.0.0.1}"
  local port="$2"
  local timeout="${3:-60}"
  info "Waiting for ${host}:${port} to be ready..."
  local i=0
  while ! nc -z "$host" "$port" 2>/dev/null; do
    sleep 1
    i=$((i+1))
    if [[ $i -ge $timeout ]]; then
      warn "Timed out waiting for ${host}:${port}"
      return 1
    fi
  done
  good "Port ${port} is open"
}

# Create a Docker bridge network with a fixed subnet (idempotent).
# Usage: ensure_network <name> <subnet>
ensure_network() {
  local net="$1" subnet="$2"
  if ! docker network inspect "$net" &>/dev/null; then
    docker network create --subnet="$subnet" "$net" &>/dev/null
    good "Network ${net} created (${subnet})"
  fi
}

# Remove a Docker network; silent if missing or still in use.
# Usage: remove_network <name>
remove_network() {
  local net="$1"
  docker network rm "$net" &>/dev/null || true
}

# Ensure the container name doesn't already exist (running or stopped)
ensure_container_gone() {
  local name="$1"
  if docker ps -a --format '{{.Names}}' | grep -qx "$name" 2>/dev/null; then
    info "Removing existing container: $name"
    docker rm -f "$name" &>/dev/null || true
  fi
}

# Print status of a named container
container_status() {
  local name="$1"
  local state
  state=$(docker inspect --format '{{.State.Status}}' "$name" 2>/dev/null || echo "not found")
  case "$state" in
    running) good "Container ${name} is ${GREEN}running${RESET}" ;;
    exited)  warn "Container ${name} is stopped (exited)" ;;
    *)       info "Container ${name}: ${state}" ;;
  esac
}

# Enforce that we're called with start|stop|status
require_action() {
  local action="${1:-}"
  case "$action" in
    start|stop|status) ;;
    *)
      echo "Usage: $(basename "$0") {start|stop|status}"
      exit 1 ;;
  esac
}
