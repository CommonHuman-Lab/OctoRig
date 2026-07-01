#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: Rewind Range
# Deliberately vulnerable retro video & games store — SQLi, XSS, IDOR
# Built from source in labs/rewindrange/
# =============================================================================

LAB_NAME="Rewind Range"
CONTAINER_NAME="octorig-rewindrange"
LAB_NET="octorig-rewindrange-net"
LAB_SUBNET="172.28.1.0/24"
LAB_IP="172.28.1.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/rewindrange"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building Rewind Range image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-rewindrange:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/rewindrange/"
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
      octorig-rewindrange:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh staff@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./rewindrange.sh stop"
    )
    access_card INFO_LINES
    good "Rewind Range is up!"
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
