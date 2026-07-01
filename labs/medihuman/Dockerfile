FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server vsftpd supervisor netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir flask==3.0.3

# SSH — weak credentials sysadmin user
RUN mkdir -p /run/sshd && \
    sed -i \
      -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
      -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
      /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash sysadmin && echo "sysadmin:password" | chpasswd

# FTP — vsftpd anonymous access
# anon_root must be owned by root (not ftp) and not world-writable
RUN mkdir -p /srv/ftp/pub && \
    chown root:root /srv/ftp && chmod 755 /srv/ftp && \
    chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

COPY vsftpd.conf /etc/vsftpd.conf
COPY supervisord.conf /etc/supervisor/conf.d/medihuman.conf
COPY . .
RUN mkdir -p /data/uploads

# Seed FTP pub files (readable by anonymous users)
RUN printf "patient_id,name,dob,ssn,insurance_id\n1,John Walker,1985-03-12,123-45-6789,INS-00441\n2,Maria Santos,1992-07-24,234-56-7890,INS-00442\n3,Kevin Park,1978-11-05,345-67-8901,INS-00443\n4,Sara Mitchell,2001-02-18,456-78-9012,INS-00444\n" \
    > /srv/ftp/pub/patients_export.csv && \
    printf "MediHuman v2.4 System Notes\n--------------------------\nDB: /data/medihuman.db\nApp secret: medihuman-2026-xQ8nRv4\nDefault sysadmin pw: password\nSee /app for source.\n" \
    > /srv/ftp/pub/system_notes.txt && \
    chown ftp:ftp /srv/ftp/pub/patients_export.csv /srv/ftp/pub/system_notes.txt && \
    chmod 644 /srv/ftp/pub/patients_export.csv /srv/ftp/pub/system_notes.txt

EXPOSE 80 21 22 30000-30009
HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/80' || exit 1
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
