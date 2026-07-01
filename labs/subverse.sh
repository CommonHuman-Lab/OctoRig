#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: SubVerse
# Deliberately vulnerable Reddit-like community forum — SQLi, XSS, IDOR, CSRF,
# SSTI, command injection, mass assignment, insecure file upload, SSH/FTP
# Built from source in labs/subverse/
# =============================================================================

LAB_NAME="SubVerse"
CONTAINER_NAME="octorig-subverse"
LAB_NET="octorig-subverse-net"
LAB_SUBNET="172.28.18.0/24"
LAB_IP="172.28.18.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/subverse"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building SubVerse image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-subverse:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/subverse/"
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
      octorig-subverse:latest

    wait_for_port "$LAB_IP" 80 90 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh sysadmin@${LAB_IP}  (pw: subverse2024)"
      "FTP|ftp ${LAB_IP}  (anonymous)"
      "Admin|admin / commonhuman-lab"
      "Stop|./subverse.sh stop"
    )
    access_card INFO_LINES
    good "SubVerse is up!"
    ;;

  stop)
    header "Stopping ${LAB_NAME}..."
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
