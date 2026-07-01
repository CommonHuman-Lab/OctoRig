#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: VaultRip Range
#
# A deliberately credential-rich SSH target for testing VaultRip's passive
# harvesting and remote SSH modules.
#
# Two user accounts are seeded with credential files across all formats
# VaultRip recognises: SSH keys, AWS credentials, kubeconfig, Docker auth,
# git-credentials, .pgpass, .netrc, .my.cnf, shell history, and .env files.
#
# A background process holds secrets in environment variables so the memory
# scanner fires when vaultrip is run locally inside the container.
#
# Usage:
#   ./vaultriprange.sh start
#   ./vaultriprange.sh stop
#   ./vaultriprange.sh status
#
# Test with VaultRip (remote SSH mode):
#   vaultrip --remote 127.0.0.1 --ssh-port 2222 \
#            --ssh-user labuser --ssh-pass "LabUser123!" \
#            --no-memory --no-browser
#
# Test locally inside the container:
#   docker exec -it octorig-vaultriprange bash
#   vaultrip /home  (if vaultrip is installed in the container)
#
# AD attack modules (DCSync, PTH, ticket forging) — pair with VulnAD:
#   ./vulnad.sh start
# =============================================================================

LAB_NAME="VaultRip Range"
CONTAINER_NAME="octorig-vaultriprange"
LAB_NET="octorig-vaultriprange-net"
LAB_SUBNET="172.28.11.0/24"
LAB_IP="172.28.11.2"
SSH_PORT=22

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAB_DIR="${SCRIPT_DIR}/vaultriprange"

source "${SCRIPT_DIR}/_common.sh"

require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."

    ensure_container_gone "$CONTAINER_NAME"

    info "Building VaultRip Range image..."
    if docker build -q -t octorig-vaultriprange:latest "$LAB_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check Dockerfile in labs/vaultriprange/"
      exit 1
    fi

    ensure_network "$LAB_NET" "$LAB_SUBNET"
    info "Starting VaultRip Range container..."
    docker run -d \
      --name "$CONTAINER_NAME" \
      --network "$LAB_NET" \
      --ip "$LAB_IP" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      octorig-vaultriprange:latest &>/dev/null

    wait_for_port "$LAB_IP" 22 30 || exit 1
    INFO_LINES=(
      "SSH host|${LAB_IP}"
      "User A|labuser / LabUser123!"
      "User B|deploy  / Deploy456!"
      "Credentials|SSH key, AWS, kube, Docker, git, pgpass, .env ..."
      "Memory process|secrets in env — run vaultrip locally for memory scan"
      "Remote test|vaultrip --remote ${LAB_IP} --ssh-user labuser --ssh-pass 'LabUser123!'"
      "Shell access|ssh labuser@${LAB_IP}"
      "AD attacks|./vulnad.sh start  (DCSync / PTH / ticket forging)"
      "Stop|./vaultriprange.sh stop"
    )
    access_card INFO_LINES

    echo ""
    info "Quick test commands:"
    info "  # Remote sweep (passive — files, kerberos, system)"
    info "  vaultrip --remote ${LAB_IP} \\"
    info "           --ssh-user labuser --ssh-pass 'LabUser123!' \\"
    info "           --no-memory --no-browser"
    echo ""
    info "  # Restrict to deploy user only"
    info "  vaultrip --remote ${LAB_IP} \\"
    info "           --ssh-user deploy --ssh-pass 'Deploy456!'"
    echo ""
    info "  # Shell access for local vaultrip run (memory scanner)"
    info "  ssh labuser@${LAB_IP}"
    echo ""

    good "VaultRip Range is up!"
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
      info "SSH: 127.0.0.1:${SSH_PORT}  (labuser / LabUser123!)"
    fi
    ;;
esac
