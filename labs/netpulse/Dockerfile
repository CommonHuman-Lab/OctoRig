FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor busybox-static \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# SSH — weak credentials
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash netadmin && echo "netadmin:monkey" | chpasswd

# Seed SSH home — harvestable by VaultRip
RUN mkdir -p /home/netadmin/scripts && \
    printf "machine router.netpulse.internal login netadmin password NetRouter99!\nmachine mail.netpulse.internal login relay password SMTPRelay1999!\nmachine ftp.netpulse.internal login netadmin password FtpNetPulse99!\n" \
      > /home/netadmin/.netrc && \
    printf "RADIUS_SECRET=np-radius-shared-1999\nSMTP_PASS=SMTPRelay1999!\nSNMP_COMMUNITY=netpulse-private-rw\nDNS_API_KEY=np-dns-2026-xK9m\nDB_PASSWORD=netpulse-db-1999\n" \
      > /home/netadmin/scripts/.env && \
    printf "snmpwalk -v2c -c netpulse-private-rw 10.0.0.1\ntelnet 10.0.0.1\nping -c 4 router.netpulse.internal\nmysql -u root -pnetpulse-db-1999 netpulse\ncurl -H 'X-DNS-Key: np-dns-2026-xK9m' https://dns.netpulse.internal/api/zones\n" \
      > /home/netadmin/.bash_history && \
    chmod 600 /home/netadmin/.netrc /home/netadmin/.bash_history && \
    chown -R netadmin:netadmin /home/netadmin

# FTP — anonymous read-only
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/netpulse.conf
COPY . .
RUN mkdir -p /data && \
    printf "subscriber_id,username,email,plan,ip_address,password_hash\nNP-0001,dialup_dave,dave@aol.example,56k,10.0.1.10,5f4dcc3b5aa765d61d8327deb882cf99\nNP-0002,isdn_irene,irene@compuserve.example,ISDN,10.0.1.11,e10adc3949ba59abbe56e057f20f883e\nNP-0003,broadband_bob,bob@msn.example,512k,10.0.1.12,25d55ad283aa400af464c76d713c07ad\n" \
      > /srv/ftp/pub/subscribers.csv && \
    printf "NetPulse Network Config\n=======================\nSNMP community (RW): netpulse-private-rw\nRADIUS secret:       np-radius-shared-1999\nRouter admin:        netadmin / NetRouter99!\nSMTP relay:          mail.netpulse.internal (relay/SMTPRelay1999!)\nDefault netadmin pw: monkey\n" \
      > /srv/ftp/pub/network_config.txt && \
    chown ftp:ftp /srv/ftp/pub/subscribers.csv /srv/ftp/pub/network_config.txt && \
    chmod 644 /srv/ftp/pub/subscribers.csv /srv/ftp/pub/network_config.txt

EXPOSE 80 21 22 23 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
