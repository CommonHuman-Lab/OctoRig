# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# SSH — weak credentials (fleet ops console)
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash fw-ops && echo "fw-ops:logistics2026" | chpasswd

# Seed SSH home — harvestable operational secrets
RUN mkdir -p /home/fw-ops/ops && \
    printf "machine wms.fleetwave.internal login fw-ops password Wm5OpsPass!\nmachine smtp.fleetwave.internal login notify password N0tifyFleet24!\n" \
      > /home/fw-ops/.netrc && \
    printf "FW_ADMIN_API_TOKEN=fw-admin-9c4e1a7b\nFW_CARRIER_API=https://carrier.fleetwave.internal/v2\nDB_DSN=postgres://fw-ops:Wm5OpsPass!@wms.fleetwave.internal/fleetwave\n" \
      > /home/fw-ops/ops/.env && \
    printf "curl -H 'X-Admin-Token: fw-admin-9c4e1a7b' http://127.0.0.1/api/v1/shipments/1\nftp 172.28.21.2\ncat ops/.env\nsqlite3 /data/fleetwave.db '.tables'\n" \
      > /home/fw-ops/.bash_history && \
    chmod 600 /home/fw-ops/.netrc /home/fw-ops/.bash_history && \
    chown -R fw-ops:fw-ops /home/fw-ops

# FTP — anonymous read-only (nightly backup drop)
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/fleetwave.conf
COPY . .
RUN mkdir -p /data && \
    printf "FleetWave Nightly WMS Backup Manifest\n=====================================\nDatabase: /data/fleetwave.db\nAdmin API token: fw-admin-9c4e1a7b\nDefault fw-ops SSH password: logistics2026\nFLAG{fw_recon_ftp_backup_leak}\n" \
      > /srv/ftp/pub/fleetwave_backup.txt && \
    chown ftp:ftp /srv/ftp/pub/fleetwave_backup.txt && \
    chmod 644 /srv/ftp/pub/fleetwave_backup.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
