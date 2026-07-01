#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: StingXSS Fire Range
# Deliberately vulnerable Flask + SQLite app with tiered XSS challenges.
# Built from source in labs/stingxss/
# =============================================================================

LAB_NAME="StingXSS Fire Range"
APP_CONTAINER="octorig-stingxss-app"
SCORES_VOLUME="octorig-stingxss-scores"
LAB_NET="octorig-stingxss-net"
LAB_SUBNET="172.28.9.0/24"
LAB_IP="172.28.9.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/stingxss"

source "${SCRIPT_DIR}/_common.sh"

# reset must be handled before require_action (which only accepts start|stop|status)
if [[ "${1:-}" == "reset" ]]; then
  header "Resetting scores..."
  docker rm -f "$APP_CONTAINER" &>/dev/null || true
  if docker volume rm "$SCORES_VOLUME" &>/dev/null; then
    good "Scores volume '${SCORES_VOLUME}' removed — all scores wiped."
  else
    warn "Volume '${SCORES_VOLUME}' not found (nothing to reset)."
  fi
  info "Run './stingxss.sh start' to bring the lab back up with a clean scoreboard."
  exit 0
fi

require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."

    # --- clean up any leftovers ---
    ensure_container_gone "$APP_CONTAINER"

    # --- scores volume ---
    if ! docker volume inspect "$SCORES_VOLUME" &>/dev/null; then
      docker volume create "$SCORES_VOLUME" &>/dev/null
      good "Volume ${SCORES_VOLUME} created"
    else
      good "Volume ${SCORES_VOLUME} ready (cached)"
    fi

    # --- build image ---
    info "Building StingXSS Fire Range image..."
    if docker build -q -t octorig-stingxss:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check Dockerfile in labs/stingxss/"
      exit 1
    fi

    # --- app container ---
    ensure_network "$LAB_NET" "$LAB_SUBNET"
    info "Starting StingXSS Fire Range app..."
    docker run -d \
      --name "$APP_CONTAINER" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      -v "${SCORES_VOLUME}:/data" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      octorig-stingxss:latest &>/dev/null

    good "App container started"

    # --- wait for /health ---
    info "Waiting for StingXSS Fire Range to be ready..."
    _i=0
    until curl -sf "http://${LAB_IP}/health" &>/dev/null; do
      sleep 2
      _i=$((_i+2))
      if [[ $_i -ge 60 ]]; then
        warn "Timed out waiting for /health — check: docker logs $APP_CONTAINER"
        exit 1
      fi
    done
    good "StingXSS Fire Range is healthy"

    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "Flag submit|POST /api/submit-flag"
      "Stop|./stingxss.sh stop"
      "Reset scores|./stingxss.sh reset"
    )
    access_card INFO_LINES
    good "StingXSS Fire Range is up!"
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
