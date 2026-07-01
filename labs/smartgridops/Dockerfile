# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# Author of this lab : roc1t1z3not <-> https://github.com/roc1t1z3not
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor busybox-static iputils-ping \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3 requests==2.32.3

# SSH — weak credentials (grid operations console)
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash gridadmin && echo "gridadmin:summer2023" | chpasswd

# Seed SSH home — harvestable operational secrets
RUN mkdir -p /home/gridadmin/scada && \
    printf "machine scada.smartgridops.internal login gridadmin password Gr1dC0ntrol!\nmachine mqtt.smartgridops.internal login ingest password MqttIngest2023!\nmachine historian.smartgridops.internal login readonly password Hist0rian2023\n" \
      > /home/gridadmin/.netrc && \
    printf "MQTT_BROKER=mqtt.smartgridops.internal:1883\nMQTT_USER=ingest\nMQTT_PASS=MqttIngest2023!\nDEVICE_API_TOKEN=sgo-device-7f3a9c2e1b\nADMIN_API_TOKEN=sgo-admin-d41d8cd98f\nHISTORIAN_DSN=postgres://readonly:Hist0rian2023@historian.smartgridops.internal/grid\n" \
      > /home/gridadmin/scada/.env && \
    printf "mosquitto_pub -h mqtt.smartgridops.internal -t grid/zone/1/cmd -m reboot\ncurl -H 'X-Device-Token: sgo-device-7f3a9c2e1b' http://127.0.0.1/api/device/list\nping -c4 substation-a.smartgridops.internal\nsnmpwalk -v2c -c grid-private 10.20.0.1\n" \
      > /home/gridadmin/.bash_history && \
    chmod 600 /home/gridadmin/.netrc /home/gridadmin/.bash_history && \
    chown -R gridadmin:gridadmin /home/gridadmin

# FTP — anonymous read-only (firmware / config drop)
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/smartgridops.conf
COPY . .
RUN mkdir -p /data && \
    printf "device_id,name,zone,type,mgmt_ip,api_token\nDEV-1001,Substation A Transformer,1,transformer,10.20.1.10,sgo-device-7f3a9c2e1b\nDEV-1002,Downtown EV Charger Bank,2,ev_charger,10.20.2.20,sgo-device-7f3a9c2e1b\nDEV-1003,North Feeder Recloser,3,recloser,10.20.3.30,sgo-device-7f3a9c2e1b\n" \
      > /srv/ftp/pub/device_inventory.csv && \
    printf "SmartGridOps SCADA Config\n=========================\nMQTT broker:     mqtt.smartgridops.internal:1883 (ingest/MqttIngest2023!)\nDevice API token: sgo-device-7f3a9c2e1b  (shared across all field devices)\nAdmin API token:  sgo-admin-d41d8cd98f\nSNMP community:   grid-private\nDefault gridadmin pw: summer2023\nFLAG{sgo_recon_ftp_config_leak}\n" \
      > /srv/ftp/pub/scada_config.txt && \
    chown ftp:ftp /srv/ftp/pub/device_inventory.csv /srv/ftp/pub/scada_config.txt && \
    chmod 644 /srv/ftp/pub/device_inventory.csv /srv/ftp/pub/scada_config.txt

EXPOSE 80 21 22 23 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
