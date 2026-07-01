#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: VulnAD — Vulnerable Active Directory (Samba4 on Linux)
#
# Spins up a Samba4 Active Directory Domain Controller inside Docker and
# then runs a Python script to populate it with the same attack paths as
# the original VulnAD PowerShell script by @safebuffer:
#
#   Attack paths seeded:
#     - Kerberoastable service accounts (weak passwords)
#     - AS-REP Roastable users (pre-auth disabled)
#     - DCSync-capable users
#     - Password in AD object description
#     - Password spraying (shared passwords)
#     - Bad ACLs (GenericAll / WriteDACL / WriteOwner etc.)
#     - DnsAdmins group abuse
#     - Default/weak passwords (Changeme123!)
#
# Ports:
#   88   — Kerberos
#   389  — LDAP
#   636  — LDAPS
#   445  — SMB
#   3268 — Global Catalog LDAP
#
# Domain: vulnad.local
# Admin:  Administrator / P@ssw0rd123!
# =============================================================================

LAB_NAME="VulnAD"
CONTAINER_NAME="octorig-vulnad"
DOMAIN="vulnad.local"
DOMAIN_UPPER="VULNAD"
ADMIN_PASS="P@ssw0rd123!"
REALM="VULNAD.LOCAL"
LAB_NET="octorig-vulnad-net"
LAB_SUBNET="172.28.17.0/24"
LAB_IP="172.28.17.2"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VULNAD_DIR="${SCRIPT_DIR}/vulnad"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

# ---------------------------------------------------------------------------
# Build the Samba AD Docker image if not cached
# ---------------------------------------------------------------------------
_build_image() {
  local image_tag="octorig-samba-ad:latest"
  if docker image inspect "$image_tag" &>/dev/null; then
    info "Samba AD image already built — skipping build."
  else
    info "Building Samba AD Docker image (first run, ~2 min)..."
    local frames=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
    local i=0
    docker build -t "$image_tag" "${VULNAD_DIR}" --file "${VULNAD_DIR}/Dockerfile" &>/dev/null &
    local pid=$!
    while kill -0 "$pid" 2>/dev/null; do
      printf "\r  ${GRAY}%s${RESET}  Building image..." "${frames[$i]}"
      i=$(( (i+1) % ${#frames[@]} ))
      sleep 0.1
    done
    wait "$pid"
    local rc=$?
    printf "\r\033[2K"
    if [[ $rc -ne 0 ]]; then
      bad "Docker build failed."
      exit 1
    fi
    good "Samba AD image built."
  fi
  SAMBA_IMAGE="$image_tag"
}

# ---------------------------------------------------------------------------
# Populate AD via Python script running inside the container
# ---------------------------------------------------------------------------
_populate_ad() {
  info "Waiting for Samba AD DC to fully initialise..."
  local max=90 i=0
  until docker exec "$CONTAINER_NAME" python3 -c "
from ldap3 import Server, Connection, ALL
try:
    c = Connection(Server('127.0.0.1', port=389, get_info=ALL),
        user='CN=Administrator,CN=Users,DC=${DOMAIN//./,DC=}',
        password='${ADMIN_PASS}', authentication='SIMPLE', auto_bind=True)
    exit(0)
except Exception:
    exit(1)
" &>/dev/null; do
    i=$(( i + 1 ))
    if [[ $i -ge $max ]]; then
      warn "Samba AD DC did not become ready in time."
      return 1
    fi
    sleep 2
  done

  info "Copying VulnAD population script into container..."
  docker cp "${VULNAD_DIR}/populate_vulnad.py" "${CONTAINER_NAME}:/tmp/populate_vulnad.py"

  info "Running population script inside container..."
  docker exec "$CONTAINER_NAME" bash -c \
    "python3 /tmp/populate_vulnad.py \
      --domain ${DOMAIN} \
      --admin-pass '${ADMIN_PASS}' \
      --ldap-server 127.0.0.1" \
    && good "VulnAD populated successfully." \
    || warn "Population script encountered errors (partial population may exist)."
}

# ---------------------------------------------------------------------------
case "$1" in
  start)
    header "Starting..."
    ensure_container_gone "$CONTAINER_NAME"

    _build_image

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    info "Starting Samba4 AD DC container..."
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --hostname "dc1.${DOMAIN}" \
      --privileged \
      -e DOMAIN="$DOMAIN" \
      -e DOMAIN_UPPER="$DOMAIN_UPPER" \
      -e REALM="$REALM" \
      -e ADMIN_PASS="$ADMIN_PASS" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      "$SAMBA_IMAGE" &>/dev/null

    wait_for_port "$LAB_IP" 389 120 || exit 1
    _populate_ad

    INFO_LINES=(
      "Domain|${DOMAIN}"
      "DC hostname|dc1.${DOMAIN}"
      "Admin user|Administrator"
      "Admin pass|${ADMIN_PASS}"
      "LDAP|ldap://${LAB_IP}:389"
      "Kerberos|${LAB_IP}:88"
      "SMB|${LAB_IP}:445"
      "Attack paths|Kerb / ASREP / DCSync / BadACL"
      "Impacket|secretsdump / GetUserSPNs etc."
      "Stop|./vulnad.sh stop"
    )
    access_card INFO_LINES

    echo ""
    info "Quick-start attack examples:"
    info "  GetUserSPNs.py ${DOMAIN}/Administrator:'${ADMIN_PASS}' -dc-ip ${LAB_IP} -request"
    info "  GetNPUsers.py ${DOMAIN}/ -usersfile users.txt -dc-ip ${LAB_IP} -no-pass"
    info "  secretsdump.py ${DOMAIN}/dcsync_user@${LAB_IP}"
    info "  bloodhound-python -u Administrator -p '${ADMIN_PASS}' -d ${DOMAIN} -ns ${LAB_IP} -c All"
    echo ""

    good "VulnAD is up!"
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
    if docker ps --format '{{.Names}}' | grep -qx "$CONTAINER_NAME"; then
      info "Domain: ${DOMAIN}"
      info "LDAP:   ldap://${LAB_IP}:389"
    fi
    ;;
esac
