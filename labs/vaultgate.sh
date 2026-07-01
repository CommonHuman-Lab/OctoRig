#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: VaultGate IDOR Range
# Deliberately vulnerable IDOR challenges for benchmarking.
# Built from source in labs/vaultgate/
# =============================================================================

LAB_NAME="VaultGate IDOR Range"
APP_CONTAINER="octorig-vaultgate-app"
SCORES_VOLUME="octorig-vaultgate-scores"
LAB_NET="octorig-vaultgate-net"
LAB_SUBNET="172.28.10.0/24"
LAB_IP="172.28.10.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/vaultgate"

source "${SCRIPT_DIR}/_common.sh"

if [[ "${1:-}" == "reset" ]]; then
  header "Resetting scores..."
  docker rm -f "$APP_CONTAINER" &>/dev/null || true
  if docker volume rm "$SCORES_VOLUME" &>/dev/null; then
    good "Scores volume '${SCORES_VOLUME}' removed — all scores wiped."
  else
    warn "Volume '${SCORES_VOLUME}' not found (nothing to reset)."
  fi
  info "Run './vaultgate.sh start' to bring the lab back up with a clean scoreboard."
  exit 0
fi

require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."

    ensure_container_gone "$APP_CONTAINER"

    if ! docker volume inspect "$SCORES_VOLUME" &>/dev/null; then
      docker volume create "$SCORES_VOLUME" &>/dev/null
      good "Volume ${SCORES_VOLUME} created"
    else
      good "Volume ${SCORES_VOLUME} ready (cached)"
    fi

    info "Building VaultGate image..."
    if docker build -q -t octorig-vaultgate:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check Dockerfile in labs/vaultgate/"
      exit 1
    fi

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    info "Starting VaultGate app..."
    docker run -d \
      --name "$APP_CONTAINER" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      -v "${SCORES_VOLUME}:/data" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      octorig-vaultgate:latest &>/dev/null

    good "App container started"

    info "Waiting for VaultGate to be ready..."
    _i=0
    until curl -sf "http://${LAB_IP}/health" &>/dev/null; do
      sleep 2
      _i=$((_i+2))
      if [[ $_i -ge 60 ]]; then
        warn "Timed out waiting for /health — check: docker logs $APP_CONTAINER"
        exit 1
      fi
    done
    good "VaultGate is healthy"

    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "Tokens|GET /api/tokens"
      "Login|POST /api/login"
      "Flag submit|POST /api/submit-flag"
      "Stop|./vaultgate.sh stop"
      "Reset scores|./vaultgate.sh reset"
    )
    access_card INFO_LINES

    good "VaultGate IDOR Range is up!"
    ;;

  stop)
    header "Stopping..."
    if docker rm -f "$APP_CONTAINER" &>/dev/null; then
      good "Container $APP_CONTAINER removed."
    else
      warn "Container $APP_CONTAINER was not running."
    fi
    info "Scores volume preserved (scores persist across restarts)."
    remove_network "$LAB_NET"
    ;;

  status)
    container_status "$APP_CONTAINER"
    ;;
esac
