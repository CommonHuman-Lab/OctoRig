FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# Bootstrap Icons SVG sprite — vendored at build time so the running
# container serves it from its own static/ dir with no runtime internet
# dependency (same build-time-only network assumption as apt-get/pip above).
ADD https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/bootstrap-icons.svg /app/static/icons/bootstrap-icons.svg

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash -N staff && echo "staff:soundcheck" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/staff/platform && \
    printf "DB_URL=sqlite:////data/waveform.db\nDB_PASSWORD=wf-db-secret-2026\nSECRET_KEY=waveform-tR7nQz2\nROYALTY_API_KEY=rk_live_FakeWaveformRoyalty1234567890\nAUDIO_BUCKET=s3://waveform-audio-prod\nAUDIO_BUCKET_KEY=AKIAFAKEWAVEFORMKEY99\n" \
      > /home/staff/platform/.env && \
    printf "machine cdn.waveform-audio.net login staff password AudioCdn2026!\nmachine api.royalty-partners.io login waveform password RoyaltyApi99!\n" \
      > /home/staff/.netrc && \
    printf "cd /app\ngit clone https://staff:ghp_FakeWaveformGitHubToken1234567890@github.com/waveform/platform-config.git\nsqlite3 /data/waveform.db\ntar czf /tmp/backup.tgz /data\n" \
      > /home/staff/.bash_history && \
    chmod 600 /home/staff/.netrc /home/staff/.bash_history && \
    chown -R staff:staff /home/staff

# FTP — anonymous read-only
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/waveform.conf
COPY . .
RUN mkdir -p /data && \
    printf "artist_id,name,monthly_streams,payout_status\n1,Lena Fairweather,182400,paid\n2,Kilowatt Kids,94100,pending\n3,Marigold Static,61200,paid\n" \
      > /srv/ftp/pub/royalty_export.csv && \
    printf "Waveform — Platform Notes\n==========================\nDB path:      /data/waveform.db\nApp secret:   waveform-tR7nQz2\nDefault staff pw: soundcheck\nRoyalty API key stored in ~/platform/.env\n" \
      > /srv/ftp/pub/platform_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/royalty_export.csv /srv/ftp/pub/platform_notes.txt && \
    chmod 644 /srv/ftp/pub/royalty_export.csv /srv/ftp/pub/platform_notes.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
