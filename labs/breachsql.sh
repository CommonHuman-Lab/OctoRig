#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# Lab: BreachSQL Fire Range
# Deliberately vulnerable Flask + MySQL + PostgreSQL + SQLite app
# with tiered SQL injection challenges across three backends.
# Built from source in labs/firerange/
# =============================================================================

LAB_NAME="BreachSQL Fire Range"
NETWORK_NAME="octorig-breachsql-net"
LAB_SUBNET="172.28.8.0/24"
LAB_IP="172.28.8.2"
MYSQL_CONTAINER="octorig-breachsql-db"
PG_CONTAINER="octorig-breachsql-pg"
APP_CONTAINER="octorig-breachsql-app"
SCORES_VOLUME="octorig-breachsql-scores"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FIRERANGE_DIR="${SCRIPT_DIR}/firerange"

source "${SCRIPT_DIR}/_common.sh"
require_action "${1:-}"

case "$1" in
  start)
    header "Starting..."

    # --- clean up any leftovers ---
    ensure_container_gone "$APP_CONTAINER"
    ensure_container_gone "$MYSQL_CONTAINER"
    ensure_container_gone "$PG_CONTAINER"

    # --- network (subnet lets us assign the app container a fixed IP) ---
    if ! docker network inspect "$NETWORK_NAME" &>/dev/null; then
      docker network create --subnet="$LAB_SUBNET" "$NETWORK_NAME" &>/dev/null
      good "Network ${NETWORK_NAME} created (${LAB_SUBNET})"
    else
      good "Network ${NETWORK_NAME} ready (cached)"
    fi

    # --- scores volume ---
    if ! docker volume inspect "$SCORES_VOLUME" &>/dev/null; then
      docker volume create "$SCORES_VOLUME" &>/dev/null
      good "Volume ${SCORES_VOLUME} created"
    else
      good "Volume ${SCORES_VOLUME} ready (cached)"
    fi

    # --- MySQL ---
    info "Starting MySQL..."
    docker run -d \
      --name "$MYSQL_CONTAINER" \
      --network "$NETWORK_NAME" \
      -e MYSQL_ROOT_PASSWORD=rootpass \
      -e MYSQL_DATABASE=firerange \
      -e MYSQL_USER=firerange \
      -e MYSQL_PASSWORD=firerange \
      -v "${FIRERANGE_DIR}/init.sql:/docker-entrypoint-initdb.d/init.sql:ro" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      mysql:8.0 \
      --default-authentication-plugin=mysql_native_password &>/dev/null

    good "MySQL container started"

    # --- PostgreSQL ---
    info "Starting PostgreSQL..."
    docker run -d \
      --name "$PG_CONTAINER" \
      --network "$NETWORK_NAME" \
      -e POSTGRES_DB=firerange \
      -e POSTGRES_USER=firerange \
      -e POSTGRES_PASSWORD=firerange \
      -v "${FIRERANGE_DIR}/init_pg.sql:/docker-entrypoint-initdb.d/init_pg.sql:ro" \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      postgres:16-alpine &>/dev/null

    good "PostgreSQL container started"

    # --- build Flask image ---
    info "Building Fire Range image..."
    if docker build -q -t octorig-breachsql:latest "$FIRERANGE_DIR" >/dev/null; then
      good "Image built"
    else
      bad "Image build failed — check Dockerfile in labs/firerange/"
      exit 1
    fi

    # --- Flask app ---
    info "Starting Fire Range app..."
    docker run -d \
      --name "$APP_CONTAINER" \
      --network "$NETWORK_NAME" \
      --ip "$LAB_IP" \
      -v "${SCORES_VOLUME}:/data" \
      -e MYSQL_HOST="$MYSQL_CONTAINER" \
      -e MYSQL_PORT=3306 \
      -e MYSQL_USER=firerange \
      -e MYSQL_PASSWORD=firerange \
      -e MYSQL_DATABASE=firerange \
      -e PG_HOST="$PG_CONTAINER" \
      -e PG_PORT=5432 \
      -e PG_USER=firerange \
      -e PG_PASSWORD=firerange \
      -e PG_DATABASE=firerange \
      --restart unless-stopped \
      --memory="$LAB_MEMORY" \
      --cpus="$LAB_CPUS" \
      octorig-breachsql:latest &>/dev/null

    good "App container started"

    # --- wait for /health (MySQL-gated) ---
    info "Waiting for Fire Range to be ready (DB init can take ~30s)..."
    _i=0
    until curl -sf "http://${LAB_IP}/health" &>/dev/null; do
      sleep 2
      _i=$((_i+2))
      if [[ $_i -ge 120 ]]; then
        warn "Timed out waiting for /health — check: docker logs $APP_CONTAINER"
        exit 1
      fi
    done
    good "Fire Range is healthy"

    INFO_LINES=(
      "URL|http://${LAB_IP}"
      "Flag submit|POST /api/submit-flag"
      "Stop|./breachsql.sh stop"
    )
    access_card INFO_LINES
    good "BreachSQL Fire Range is up!"
    ;;

  stop)
    header "Stopping..."
    _stopped=0
    for cname in "$APP_CONTAINER" "$MYSQL_CONTAINER" "$PG_CONTAINER"; do
      if docker rm -f "$cname" &>/dev/null; then
        good "Container $cname removed."
        _stopped=$((_stopped+1))
      fi
    done
    [[ $_stopped -eq 0 ]] && warn "No Fire Range containers were running."

    info "Scores volume preserved (scores persist across restarts)."
    remove_network "$NETWORK_NAME"
    ;;

  status)
    container_status "$APP_CONTAINER"
    container_status "$MYSQL_CONTAINER"
    container_status "$PG_CONTAINER"
    ;;

  reset)
    header "Resetting scores..."
    # Stop all containers first
    for cname in "$APP_CONTAINER" "$MYSQL_CONTAINER" "$PG_CONTAINER"; do
      docker rm -f "$cname" &>/dev/null
    done
    if docker volume rm "$SCORES_VOLUME" &>/dev/null; then
      good "Scores volume '${SCORES_VOLUME}' removed — all scores wiped."
    else
      warn "Volume '${SCORES_VOLUME}' not found (nothing to reset)."
    fi
    info "Run './breachsql.sh start' to bring the lab back up with a clean scoreboard."
    ;;
esac
