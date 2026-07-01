FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor openssh-client redis-server libpam-pwdfile \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash bankops && echo "bankops:shadow" | chpasswd

# Seed SSH home — harvestable by VaultRip (incl. generated RSA key)
RUN mkdir -p /home/bankops/.ssh /home/bankops/app && \
    ssh-keygen -t rsa -b 2048 -f /home/bankops/.ssh/id_rsa -N "" -C "bankops@humanbank.internal" && \
    printf "172.28.4.2:5432:humanbank:bankops:pg-bank-hb2026!\n172.28.4.2:5432:reporting:readonly:pg-readonly-2026!\n" \
      > /home/bankops/.pgpass && \
    printf "JWT_SECRET=bank-jwt-hb2026-xK9mPq3\nSWIFT_API_KEY=SWIFT-HB-2026-xyzABCDEF\nDB_PASSWORD=pg-bank-hb2026!\nENCRYPTION_KEY=hb-enc-2026-pq3mK9rT\n" \
      > /home/bankops/app/.env && \
    printf "cd /app\npg_dump -U bankops -h 172.28.4.2 -W humanbank > /tmp/backup.sql\npsql -U bankops -h 172.28.4.2 humanbank\ncurl -H 'X-SWIFT-Key: SWIFT-HB-2026-xyzABCDEF' https://swift.humanbank.internal/transfer\n" \
      > /home/bankops/.bash_history && \
    chmod 600 /home/bankops/.pgpass /home/bankops/.ssh/id_rsa /home/bankops/.bash_history && \
    chown -R bankops:bankops /home/bankops

# FTP — login required (virtual user: bankops / master)
RUN mkdir -p /srv/ftp/pub /etc/vsftpd && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub
RUN HASH=$(openssl passwd -1 "master") && \
    printf "bankops:%s\n" "${HASH}" > /etc/vsftpd/ftpd.passwd && \
    chmod 600 /etc/vsftpd/ftpd.passwd
RUN printf "auth    required pam_pwdfile.so pwdfile=/etc/vsftpd/ftpd.passwd\naccount required pam_permit.so\n" \
    > /etc/pam.d/vsftpd

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/humanbank.conf
COPY . .
RUN mkdir -p /data/uploads && \
    printf "account_id,holder,iban,balance,account_type\nHB-100001,Alice Johnson,GB29HUMB60161331926819,12480.00,Current\nHB-100002,Bob Martinez,GB82HUMB60161300001235,3210.50,Savings\nHB-100003,Carol White,GB94HUMB60161399887712,87650.00,Business\nHB-100004,David Kim,GB47HUMB60161355443322,500.00,Current\n" \
      > /srv/ftp/pub/accounts_export.csv && \
    printf "HumanBank Maintenance Notes\n===========================\nDB host:      172.28.4.2:5432\nDB user:      bankops\nDefault bankops pw: shadow\npgpass:       ~/.pgpass\nSWIFT API key stored in ~/app/.env\n" \
      > /srv/ftp/pub/maintenance_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/accounts_export.csv /srv/ftp/pub/maintenance_notes.txt && \
    chmod 644 /srv/ftp/pub/accounts_export.csv /srv/ftp/pub/maintenance_notes.txt

EXPOSE 80 21 22 6379 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
