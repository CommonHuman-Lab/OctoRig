#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: TradeFloor
# Deliberately vulnerable Y2K-era stock trading terminal — XXE, CSRF, mass
# assignment, SQLi, IDOR, stored XSS, broken access control
# Built from source in labs/tradefloor/
# =============================================================================

LAB_NAME="TradeFloor"
CONTAINER_NAME="octorig-tradefloor"
LAB_NET="octorig-tradefloor-net"
LAB_SUBNET="172.28.2.0/24"
LAB_IP="172.28.2.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/tradefloor"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building TradeFloor image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-tradefloor:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/tradefloor/"
      exit 1
    fi

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      octorig-tradefloor:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh trader@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./tradefloor.sh stop"
    )
    access_card INFO_LINES
    good "TradeFloor is up!"
    ;;

  stop)
    header "Stopping..."
    if docker rm -f "$CONTAINER_NAME" &>/dev/null; then
      good "Container $CONTAINER_NAME removed."
    else
      warn "Container $CONTAINER_NAME was not running."
    fi
    remove_network "$LAB_NET"
    ;;

  status)
    container_status "$CONTAINER_NAME"
    ;;
esac
