FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor libpam-pwdfile \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash cinemaops && echo "cinemaops:qwerty" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/cinemaops/.aws /home/cinemaops/app && \
    printf "[default]\naws_access_key_id=AKIAIOSFODNN7LIMELIG\naws_secret_access_key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYLIMELIGHT\nregion=eu-west-1\n" \
      > /home/cinemaops/.aws/credentials && \
    printf "STRIPE_SECRET_KEY=sk_live_FakeLimelightStripe1234567890\nPAYMENT_API_SECRET=ll-pay-2026-xyzABCDEF\nDB_PASSWORD=limelight-db-2026\nS3_BUCKET=limelight-posters\nJWT_SECRET=limelight-jwt-2026-xK9m\n" \
      > /home/cinemaops/app/.env && \
    printf "cd /app\naws s3 cp poster.jpg s3://limelight-posters/movies/ --profile default\naws s3 ls s3://limelight-posters\ncurl -H 'Authorization: Bearer ll-pay-2026-xyzABCDEF' https://payments.limelight.internal/charge\n" \
      > /home/cinemaops/.bash_history && \
    chmod 600 /home/cinemaops/.aws/credentials /home/cinemaops/.bash_history && \
    chown -R cinemaops:cinemaops /home/cinemaops

# FTP — login required (virtual user: cinemaops / abc123)
RUN mkdir -p /srv/ftp/pub /etc/vsftpd && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub
RUN HASH=$(openssl passwd -1 "abc123") && \
    printf "cinemaops:%s\n" "${HASH}" > /etc/vsftpd/ftpd.passwd && \
    chmod 600 /etc/vsftpd/ftpd.passwd
RUN printf "auth    required pam_pwdfile.so pwdfile=/etc/vsftpd/ftpd.passwd\naccount required pam_permit.so\n" \
    > /etc/pam.d/vsftpd

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/limelight.conf
COPY . .
RUN mkdir -p /data && \
    printf "booking_id,user,movie,showing_time,seats,total_paid\nLL-3001,john.doe,The Dark Knight,2026-06-01 19:30,C4,12.00\nLL-3002,alice.jones,Inception,2026-06-01 20:00,\"F7,F8\",24.00\nLL-3003,admin,The CommonHuman Experiment,2026-06-02 21:00,A1,19.99\n" \
      > /srv/ftp/pub/bookings_export.csv && \
    printf "Limelight Projector Room Notes\n==============================\nDB:           /data/limelight.db\nS3 bucket:    limelight-posters (creds in ~/.aws/credentials)\nStripe key:   stored in ~/app/.env\nDefault cinemaops pw: qwerty\nMaintenance code: PROJ-4422\n" \
      > /srv/ftp/pub/projector_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/bookings_export.csv /srv/ftp/pub/projector_notes.txt && \
    chmod 644 /srv/ftp/pub/bookings_export.csv /srv/ftp/pub/projector_notes.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
