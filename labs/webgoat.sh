#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: OWASP WebGoat
# Lesson-based deliberately insecure Java web app — covers the same vuln
# classes as PortSwigger Web Academy (SQLi, XSS, SSRF, JWT, XXE, etc.)
# Image: webgoat/webgoat
# =============================================================================

LAB_NAME="WebGoat"
CONTAINER_NAME="octorig-webgoat"
LAB_NET="octorig-webgoat-net"
LAB_SUBNET="172.28.15.0/24"
LAB_IP="172.28.15.2"

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"
    docker_pull webgoat/webgoat:latest

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --tmpfs /tmp \
      --tmpfs /home/webgoat/.webgoat-2025.3 \
      -e SERVER_ADDRESS=0.0.0.0 \
      -e TZ=UTC \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      webgoat/webgoat:latest &>/dev/null

    wait_for_port "$LAB_IP" 8080 90 || exit 1
    INFO_LINES=(
      "WebGoat URL|http://${LAB_IP}:8080/WebGoat"
      "WebWolf URL|http://${LAB_IP}:9090/WebWolf"
      "Register|Create account on first visit"
      "Coverage|SQLi / XSS / XXE / JWT / IDOR / SSRF"
      "Coverage 2|Path traversal / Crypto / Auth bypass"
      "Stop|./webgoat.sh stop"
    )
    access_card INFO_LINES
    good "WebGoat is up!"
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
