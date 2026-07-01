#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: OWASP Juice Shop
# Official Docker image — covers all OWASP Top 10 + many more vulns
# Image: bkimminich/juice-shop
# =============================================================================

LAB_NAME="Juice Shop"
CONTAINER_NAME="octorig-juiceshop"
LAB_NET="octorig-juiceshop-net"
LAB_SUBNET="172.28.12.0/24"
LAB_IP="172.28.12.2"

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"
    docker_pull bkimminich/juice-shop:latest

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      bkimminich/juice-shop:latest &>/dev/null

    wait_for_port "$LAB_IP" 3000 60 || exit 1
    INFO_LINES=(
      "URL|http://${LAB_IP}:3000"
      "Credentials|none (register on first visit)"
      "Admin email|admin@juice-sh.op"
      "Admin pass|admin123"
      "Challenges|82 OWASP Top 10 tasks"
      "Stop|./juiceshop.sh stop"
    )
    access_card INFO_LINES
    good "Juice Shop is up!"
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
