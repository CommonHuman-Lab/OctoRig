# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
# =============================================================================
# OctoRig VulnAD — Samba4 Active Directory Domain Controller
# Builds Samba 4.19 from source (with AD DC support) on Ubuntu 22.04.
# Multi-stage: builder compiles, runtime image is lean.
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1 — build
# ---------------------------------------------------------------------------
FROM ubuntu:22.04 AS builder

ENV DEBIAN_FRONTEND=noninteractive
ENV SAMBA_VERSION=4.19.6

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        pkg-config \
        python3 \
        python3-dev \
        python3-dnspython \
        python3-pycryptodome \
        python3-markdown \
        python3-setuptools \
        libacl1-dev \
        libattr1-dev \
        libblkid-dev \
        libgnutls28-dev \
        libldap2-dev \
        libpam0g-dev \
        libreadline-dev \
        libcups2-dev \
        libpopt-dev \
        libjansson-dev \
        liblmdb-dev \
        libgpgme-dev \
        libarchive-dev \
        libtasn1-bin \
        libtasn1-dev \
        dbus \
        flex \
        bison \
        xsltproc \
        docbook-xsl \
        libavahi-client-dev \
        zlib1g-dev \
        libbsd-dev \
        liburing-dev \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && cpan -T Parse::Yapp 2>/dev/null || true

WORKDIR /build
RUN wget -q "https://download.samba.org/pub/samba/stable/samba-${SAMBA_VERSION}.tar.gz" && \
    tar xf "samba-${SAMBA_VERSION}.tar.gz" && \
    rm "samba-${SAMBA_VERSION}.tar.gz"

WORKDIR /build/samba-${SAMBA_VERSION}
RUN ./configure \
        --prefix=/usr/local/samba \
        --with-configdir=/etc/samba \
        --with-logfilebase=/var/log/samba \
        --with-lockdir=/var/run/samba \
        --with-statedir=/var/lib/samba \
        --with-cachedir=/var/cache/samba \
        --with-privatedir=/var/lib/samba/private \
        --enable-fhs \
        --without-systemd \
        --disable-cups \
        --disable-iprint

RUN make -j"$(nproc)" && make install

# ---------------------------------------------------------------------------
# Stage 2 — runtime
# ---------------------------------------------------------------------------
FROM ubuntu:22.04

LABEL maintainer="CommonHuman-Lab"
LABEL description="Samba4 AD DC for VulnAD lab"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update -qq && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-markdown \
        libpython3.10 \
        python3-dnspython \
        python3-pycryptodome \
        libgnutls30 \
        libjansson4 \
        liblmdb0 \
        libpopt0 \
        libacl1 \
        libblkid1 \
        libarchive13 \
        libavahi-client3 \
        libavahi-common3 \
        libdbus-1-3 \
        libgpgme11 \
        liburing2 \
        krb5-user \
        dnsutils \
        net-tools \
        iputils-ping \
        curl \
        ldap-utils \
        ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy compiled Samba installation from builder
COPY --from=builder /usr/local/samba /usr/local/samba
COPY --from=builder /etc/samba /etc/samba

# Runtime directories
RUN mkdir -p \
        /var/log/samba \
        /var/run/samba \
        /var/lib/samba/private \
        /var/cache/samba \
        /etc/samba

ENV PATH="/usr/local/samba/bin:/usr/local/samba/sbin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/samba/lib:/usr/local/samba/lib/samba"

RUN echo "/usr/local/samba/lib" > /etc/ld.so.conf.d/samba.conf && \
    echo "/usr/local/samba/lib/samba" >> /etc/ld.so.conf.d/samba.conf && \
    ldconfig

RUN pip3 install --quiet --no-warn-script-location ldap3

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Kerberos, LDAP, LDAPS, SMB, Global Catalog
EXPOSE 88 389 636 445 3268

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/389' || exit 1
ENTRYPOINT ["/entrypoint.sh"]
