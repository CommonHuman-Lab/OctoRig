# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# SSH — weak credentials (ops console)
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash vaultops && echo "vaultops:sync2024" | chpasswd

# Seed SSH home — harvestable operational secrets
RUN mkdir -p /home/vaultops/ops && \
    printf "machine db.vaultsync.internal login vaultops password Db4dminPass!\nmachine smtp.vaultsync.internal login notify password N0tify2024!\n" \
      > /home/vaultops/.netrc && \
    printf "VS_ADMIN_API_TOKEN=vs-admin-9f3a7c1e8b\nVS_BACKUP_BUCKET=s3://vaultsync-backups\nDB_DSN=postgres://vaultops:Db4dminPass!@db.vaultsync.internal/vaultsync\n" \
      > /home/vaultops/ops/.env && \
    printf "curl -H 'X-Admin-Token: vs-admin-9f3a7c1e8b' http://127.0.0.1/api/v1/vaults/1/items\nftp 172.28.19.2\ncat ops/.env\nsqlite3 /data/vaultsync.db '.tables'\n" \
      > /home/vaultops/.bash_history && \
    chmod 600 /home/vaultops/.netrc /home/vaultops/.bash_history && \
    chown -R vaultops:vaultops /home/vaultops

# FTP — anonymous read-only (backup drop)
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/vaultsync.conf
COPY . .
RUN mkdir -p /data && \
    printf "VaultSync Nightly Backup Manifest\n==================================\nDatabase: /data/vaultsync.db\nAdmin API token: vs-admin-9f3a7c1e8b\nDefault vaultops SSH password: sync2024\nFLAG{vs_recon_ftp_backup_leak}\n" \
      > /srv/ftp/pub/vault_backup.txt && \
    chown ftp:ftp /srv/ftp/pub/vault_backup.txt && \
    chmod 644 /srv/ftp/pub/vault_backup.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
