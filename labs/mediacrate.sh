#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: MediaCrate
# Deliberately vulnerable streaming/creator platform — SQLi (login bypass,
# video search), IDOR (video & subscriber-tier level), broken access control
# (stream key escrow), stored XSS (review queue), mass assignment (profile→
# admin escalation), SSRF (thumbnail import) chained into command injection
# (internal transcode), plus weak SSH/FTP credentials.
# Built from source in labs/mediacrate/
# =============================================================================

LAB_NAME="MediaCrate"
CONTAINER_NAME="octorig-mediacrate"
LAB_NET="octorig-mediacrate-net"
LAB_SUBNET="172.28.20.0/24"
LAB_IP="172.28.20.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/mediacrate"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building MediaCrate image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-mediacrate:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/mediacrate/"
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
      octorig-mediacrate:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh mc-ops@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./mediacrate.sh stop"
    )
    access_card INFO_LINES
    good "MediaCrate is up!"
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
