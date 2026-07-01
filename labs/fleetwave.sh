#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
# =============================================================================
# Lab: FleetWave
# Deliberately vulnerable logistics / delivery fleet-management SaaS — SQLi
# (login bypass, shipment search), IDOR (shipment & depot-manifest level),
# broken access control (driver roster), stored XSS (delivery-feedback review),
# mass assignment (profile→admin), business logic (freight-credit overflow),
# SSRF (carrier-status check) chained into command injection (internal manifest
# export), plus weak SSH/FTP credentials.
# Built from source in labs/fleetwave/
# =============================================================================

LAB_NAME="FleetWave"
CONTAINER_NAME="octorig-fleetwave"
LAB_NET="octorig-fleetwave-net"
LAB_SUBNET="172.28.21.0/24"
LAB_IP="172.28.21.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/fleetwave"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building FleetWave image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-fleetwave:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/fleetwave/"
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
      octorig-fleetwave:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh fw-ops@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./fleetwave.sh stop"
    )
    access_card INFO_LINES
    good "FleetWave is up!"
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
