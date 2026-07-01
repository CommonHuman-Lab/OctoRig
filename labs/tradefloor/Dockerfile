FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor libpam-pwdfile \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 lxml==5.2.2

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash trader && echo "trader:letmein" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/trader/.aws /home/trader/deploy && \
    printf "[default]\naws_access_key_id=AKIAIOSFODNN7TRADEFLR\naws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYTRADEFLOOR\nregion=eu-west-1\n\n[prod]\naws_access_key_id=AKIAI44QH8DHBEXTRADER\naws_secret_access_key=je7MtGbClwBF/2Tk/h3yCo8nvbInZFbYmtSXtrdr\nregion=us-east-1\n" \
      > /home/trader/.aws/credentials && \
    printf "BROKER_API_SECRET=tf-broker-2026-xQ8nRv4mPq3\nJWT_SECRET=trade-jwt-2026-pq3mK9\nDB_PASSWORD=tradefloor-db-2026\nWEBHOOK_SECRET=tf-webhook-abc123\n" \
      > /home/trader/deploy/.env && \
    printf "cd /app\naws s3 ls s3://tradefloor-reports --profile prod\ncurl -H 'Authorization: Bearer tf-broker-2026-xQ8nRv4mPq3' https://api.broker.internal/v1/accounts\npsql -U trader -h db.internal -W tradefloor\n" \
      > /home/trader/.bash_history && \
    chmod 600 /home/trader/.aws/credentials /home/trader/.bash_history && \
    chown -R trader:trader /home/trader

# FTP — login required (virtual user: trader / baseball)
RUN mkdir -p /srv/ftp/pub /etc/vsftpd && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub
RUN HASH=$(openssl passwd -1 "baseball") && \
    printf "trader:%s\n" "${HASH}" > /etc/vsftpd/ftpd.passwd && \
    chmod 600 /etc/vsftpd/ftpd.passwd
RUN printf "auth    required pam_pwdfile.so pwdfile=/etc/vsftpd/ftpd.passwd\naccount required pam_permit.so\n" \
    > /etc/pam.d/vsftpd

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/tradefloor.conf
COPY . .
RUN mkdir -p /data/uploads && \
    printf "account_id,symbol,qty,avg_cost,current_price\nTF-1001,AAPL,150,142.30,178.20\nTF-1002,MSFT,200,310.50,420.10\nTF-1003,TSLA,50,220.00,195.40\nTF-1004,NVDA,75,480.00,870.50\n" \
      > /srv/ftp/pub/portfolio_export.csv && \
    printf "TradeFloor Deployment Notes\n===========================\nDB:           /data/tradefloor.db\nBroker API:   stored in ~/deploy/.env\nAWS profiles: ~/.aws/credentials (default + prod)\nDefault trader pw: letmein\n" \
      > /srv/ftp/pub/deploy_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/portfolio_export.csv /srv/ftp/pub/deploy_notes.txt && \
    chmod 644 /srv/ftp/pub/portfolio_export.csv /srv/ftp/pub/deploy_notes.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
