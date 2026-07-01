#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
# =============================================================================
# Lab: SmartGridOps
# Deliberately vulnerable IoT energy / smart-city power-grid control dashboard —
# SSRF (device polling), command injection (reboot / config push),
# weak auth (hardcoded device tokens), IDOR (zones / meter data),
# business logic (energy credit manipulation), MQTT/IoT command injection
# Built from source in labs/smartgridops/
# =============================================================================

LAB_NAME="SmartGridOps"
CONTAINER_NAME="octorig-smartgridops"
LAB_NET="octorig-smartgridops-net"
LAB_SUBNET="172.28.16.0/24"
LAB_IP="172.28.16.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/smartgridops"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building SmartGridOps image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-smartgridops:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/smartgridops/"
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
      octorig-smartgridops:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh gridadmin@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./smartgridops.sh stop"
    )
    access_card INFO_LINES
    good "SmartGridOps is up!"
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
