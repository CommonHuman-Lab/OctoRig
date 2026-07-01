# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# SSH — weak credentials (creator ops console)
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash mc-ops && echo "mc-ops:creator2026" | chpasswd

# Seed SSH home — harvestable operational secrets
RUN mkdir -p /home/mc-ops/ops && \
    printf "machine cdn.mediacrate.internal login mc-ops password Cdn4dminPass!\nmachine smtp.mediacrate.internal login notify password N0tify2024!\n" \
      > /home/mc-ops/.netrc && \
    printf "MC_ADMIN_API_TOKEN=mc-admin-7f2e9b1a\nMC_BACKUP_BUCKET=s3://mediacrate-backups\nDB_DSN=postgres://mc-ops:Cdn4dminPass!@cdn.mediacrate.internal/mediacrate\n" \
      > /home/mc-ops/ops/.env && \
    printf "curl -H 'X-Admin-Token: mc-admin-7f2e9b1a' http://127.0.0.1/api/v1/videos/1\nftp 172.28.20.2\ncat ops/.env\nsqlite3 /data/mediacrate.db '.tables'\n" \
      > /home/mc-ops/.bash_history && \
    chmod 600 /home/mc-ops/.netrc /home/mc-ops/.bash_history && \
    chown -R mc-ops:mc-ops /home/mc-ops

# FTP — anonymous read-only (backup drop)
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/mediacrate.conf
COPY . .
RUN mkdir -p /data /app/uploads && \
    printf "MediaCrate Nightly Backup Manifest\n===================================\nDatabase: /data/mediacrate.db\nAdmin API token: mc-admin-7f2e9b1a\nDefault mc-ops SSH password: creator2026\nFLAG{mc_recon_ftp_backup_leak}\n" \
      > /srv/ftp/pub/mediacrate_backup.txt && \
    chown ftp:ftp /srv/ftp/pub/mediacrate_backup.txt && \
    chmod 644 /srv/ftp/pub/mediacrate_backup.txt

# Legal/DMCA holds — outside the web root and upload tree entirely. Only
# reachable via the banner-serving path traversal bug in routes/uploads.py.
RUN mkdir -p /data/.private && \
    printf "MediaCrate Legal Holds — DMCA & Takedown Queue\n===============================================\nCase #4471: pending counter-notice review.\nCase #4488: escalated to trust & safety.\nFLAG{mc_path_traversal_legal_hold}\n" \
      > /data/.private/legal_takedowns.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
