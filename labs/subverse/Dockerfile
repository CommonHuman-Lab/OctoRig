FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor netcat-openbsd curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials for sysadmin user
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash sysadmin && echo "sysadmin:subverse2024" | chpasswd && \
    mkdir -p /home/sysadmin/.ssh && \
    ssh-keygen -t rsa -b 2048 -f /home/sysadmin/.ssh/id_rsa -N "" -q && \
    chown -R sysadmin:sysadmin /home/sysadmin/.ssh && \
    chmod 700 /home/sysadmin/.ssh && chmod 600 /home/sysadmin/.ssh/id_rsa

# Bash history hints
RUN printf 'sqlite3 /data/subverse.db .dump > /tmp/backup.sql\nftp localhost\ncat /app/.env\n' \
    > /home/sysadmin/.bash_history && \
    chown sysadmin:sysadmin /home/sysadmin/.bash_history

# FTP — vsftpd anonymous access
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/subverse.conf
COPY ftp_files/ /srv/ftp/pub/
COPY . .

RUN mkdir -p /data /app/static/uploads

# App environment hints (discoverable via SSH)
RUN printf 'SECRET_KEY=subverse-2026-xK9mQp7\nDB_PATH=/data/subverse.db\n' > /app/.env

# Fix FTP pub file ownership
RUN chown ftp:ftp /srv/ftp/pub/db_backup_2024.sql /srv/ftp/pub/deploy_notes.txt /srv/ftp/pub/users_export.csv && \
    chmod 644 /srv/ftp/pub/db_backup_2024.sql /srv/ftp/pub/deploy_notes.txt /srv/ftp/pub/users_export.csv

EXPOSE 80 21 22 30010-30019
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
