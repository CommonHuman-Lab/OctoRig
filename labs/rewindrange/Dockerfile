FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash -N staff && echo "staff:dragon" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/staff/store && \
    printf "DB_URL=sqlite:////data/rewind.db\nDB_PASSWORD=rw-db-secret-2026\nSECRET_KEY=rewind-xK9mPq3\nSTRIPE_KEY=sk_live_FakeRewindStripe1234567890\nAWS_REGION=eu-west-1\n" \
      > /home/staff/store/.env && \
    printf "machine ftp.retro-supplier.com login staff password SupplierFTP99!\nmachine api.retro-dist.com login rewind password DistApi2026!\n" \
      > /home/staff/.netrc && \
    printf "cd /app\ngit clone https://staff:ghp_FakeRewindGitHubToken1234567890@github.com/rewind/store-config.git\nmysql -u root -prw-db-secret-2026 rewind\ntar czf /tmp/backup.tgz /data\n" \
      > /home/staff/.bash_history && \
    chmod 600 /home/staff/.netrc /home/staff/.bash_history && \
    chown -R staff:staff /home/staff

# FTP — anonymous read-only
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/rewind.conf
COPY . .
RUN mkdir -p /data && \
    printf "sku,title,platform,qty,buy_price\nRW-001,Super Mario World,SNES,12,4.99\nRW-002,Sonic the Hedgehog 2,Mega Drive,8,3.99\nRW-003,Doom,DOS,5,6.99\nRW-004,Street Fighter II,SNES,3,8.50\nRW-005,GoldenEye 007,N64,7,12.00\n" \
      > /srv/ftp/pub/inventory_export.csv && \
    printf "Rewind Store — System Notes\n===========================\nDB path:      /data/rewind.db\nApp secret:   rewind-xK9mPq3\nDefault staff pw: dragon\nStripe test key stored in ~/store/.env\n" \
      > /srv/ftp/pub/store_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/inventory_export.csv /srv/ftp/pub/store_notes.txt && \
    chmod 644 /srv/ftp/pub/inventory_export.csv /srv/ftp/pub/store_notes.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
