FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash casinoops && echo "casinoops:sunshine" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/casinoops/app && \
    printf "[client]\npassword=casino-db-golden2026\nhost=127.0.0.1\n" \
      > /home/casinoops/.my.cnf && \
    printf "RNG_SEED_KEY=golden-rng-xK9mPq3\nPAYMENT_API_KEY=ga-pay-2026-abcXYZ\nDB_PASSWORD=casino-db-golden2026\nJWT_SECRET=golden-ace-jwt-2026\nADMIN_TOKEN=ga-admin-tok-2026-xyz\n" \
      > /home/casinoops/app/.env && \
    printf "cd /app\nmysql -u root -pcasino-db-golden2026 goldenace\ncurl -H 'X-API-Key: ga-pay-2026-abcXYZ' https://payments.casino.internal/v1/withdraw\ntail -f /data/goldenace.db\n" \
      > /home/casinoops/.bash_history && \
    chmod 600 /home/casinoops/.my.cnf /home/casinoops/.bash_history && \
    chown -R casinoops:casinoops /home/casinoops

COPY supervisord.conf /etc/supervisor/conf.d/goldenace.conf
COPY ftp_backdoor.py /app/ftp_backdoor.py
COPY . .
RUN mkdir -p /data

EXPOSE 80 21 22 6200 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
