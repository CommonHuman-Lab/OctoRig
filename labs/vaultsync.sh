#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: VaultSync
# Deliberately vulnerable password-manager SaaS — SQLi (login bypass, vault
# search), IDOR (vault & item level), broken access control (admin recovery
# codes), stored XSS (review queue), mass assignment (profile→admin escalation),
# SSRF (breach check) chained into command injection (internal export), plus
# weak SSH/FTP credentials.
# Built from source in labs/vaultsync/
# =============================================================================

LAB_NAME="VaultSync"
CONTAINER_NAME="octorig-vaultsync"
LAB_NET="octorig-vaultsync-net"
LAB_SUBNET="172.28.19.0/24"
LAB_IP="172.28.19.2"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="${SCRIPT_DIR}/vaultsync"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    info "Building VaultSync image (this may take ~60s for apt packages)..."
    if docker build -q -t octorig-vaultsync:latest "$APP_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check labs/vaultsync/"
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
      octorig-vaultsync:latest

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "SSH|ssh vaultops@${LAB_IP}"
      "FTP|ftp ${LAB_IP}"
      "Stop|./vaultsync.sh stop"
    )
    access_card INFO_LINES
    good "VaultSync is up!"
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
