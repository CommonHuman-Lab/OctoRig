#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: DVWA — Damn Vulnerable Web App
# PHP + MySQL, classic sqli/xss/csrf/rfi/lfi/command injection labs
# Image: vulnerables/web-dvwa
# =============================================================================

LAB_NAME="DVWA"
CONTAINER_NAME="octorig-dvwa"
LAB_NET="octorig-dvwa-net"
LAB_SUBNET="172.28.13.0/24"
LAB_IP="172.28.13.2"

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"
    docker_pull vulnerables/web-dvwa:latest

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      vulnerables/web-dvwa:latest &>/dev/null

    wait_for_port "$LAB_IP" 80 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "Username|admin"
      "Password|password"
      "Setup DB|http://${LAB_IP}/setup.php"
      "Difficulty|Low / Medium / High / Impossible"
      "Stop|./dvwa.sh stop"
    )
    access_card INFO_LINES
    warn "First visit: click 'Create / Reset Database' on the setup page."
    good "DVWA is up!"
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
