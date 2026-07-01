#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: Metasploitable2
# Linux VM image with intentionally vulnerable services
# Image: tleemcjr/metasploitable2
# Services: FTP(21) SSH(22) Telnet(23) SMTP(25) HTTP(80) SMB(445) MySQL(3306)
#           PostgreSQL(5432) VNC(5900) and many more
# =============================================================================

LAB_NAME="Metasploitable2"
CONTAINER_NAME="octorig-metasploitable"
LAB_NET="octorig-metasploitable-net"
LAB_SUBNET="172.28.14.0/24"
LAB_IP="172.28.14.2"

source "$(dirname "$0")/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"
    docker_pull tleemcjr/metasploitable2:latest

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      tleemcjr/metasploitable2:latest \
      sh -c "/bin/services.sh && sleep infinity" &>/dev/null

    wait_for_port "$LAB_IP" 80 90 || exit 1
    INFO_LINES=(
      "HTTP|http://${LAB_IP}"
      "SSH|ssh msfadmin@${LAB_IP} -oHostKeyAlgorithms=+ssh-rsa"
      "SSH creds|msfadmin / msfadmin"
      "FTP|ftp ${LAB_IP}  (anonymous OK)"
      "MySQL|mysql -h ${LAB_IP} -u root --skip-ssl"
      "SMB|smbclient -L //${LAB_IP}"
      "VNC|vncviewer ${LAB_IP}:5900  (pass: password)"
      "Stop|./metasploitable.sh stop"
    )
    access_card INFO_LINES
    warn "This container is INTENTIONALLY vulnerable. Isolate your network!"
    good "Metasploitable2 is up!"
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
