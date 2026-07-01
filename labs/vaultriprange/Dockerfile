FROM debian:bookworm-slim

# ── System packages ────────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    python3 \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# ── SSH daemon config ──────────────────────────────────────────────────────────
RUN mkdir -p /run/sshd && \
    sed -i \
        -e 's/#PermitRootLogin.*/PermitRootLogin no/' \
        -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \
        -e 's/#PubkeyAuthentication.*/PubkeyAuthentication yes/' \
        /etc/ssh/sshd_config

# ── Users ──────────────────────────────────────────────────────────────────────
RUN useradd -m -s /bin/bash labuser && echo "labuser:LabUser123!" | chpasswd && \
    useradd -m -s /bin/bash deploy  && echo "deploy:Deploy456!"   | chpasswd

# ── labuser: SSH key ───────────────────────────────────────────────────────────
RUN mkdir -p /home/labuser/.ssh && chmod 700 /home/labuser/.ssh && \
    ssh-keygen -t rsa -b 2048 -f /home/labuser/.ssh/id_rsa -N "" -C "labuser@prod-server-01" && \
    chmod 600 /home/labuser/.ssh/id_rsa && \
    chown -R labuser:labuser /home/labuser/.ssh

# ── labuser: AWS credentials ───────────────────────────────────────────────────
RUN mkdir -p /home/labuser/.aws && cat > /home/labuser/.aws/credentials << 'EOF'
[default]
aws_access_key_id = AKIAIOSFODNN7EXAMPLE
aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[production]
aws_access_key_id = AKIAI44QH8DHBEXAMPLE
aws_secret_access_key = je7MtGbClwBF/2Zp9Utk/h3yCo8nvbEXAMPLEKEY
region = eu-west-1
EOF

# ── labuser: kubeconfig with bearer token ──────────────────────────────────────
RUN mkdir -p /home/labuser/.kube && cat > /home/labuser/.kube/config << 'EOF'
apiVersion: v1
clusters:
- cluster:
    server: https://k8s.prod.example.com:6443
  name: prod-cluster
contexts:
- context:
    cluster: prod-cluster
    user: labuser-sa
  name: prod-context
current-context: prod-context
kind: Config
users:
- name: labuser-sa
  user:
    token: eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJwcm9kdWN0aW9uIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImxhYnVzZXItc2EiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6cHJvZHVjdGlvbjpsYWJ1c2VyLXNhIn0.FAKESIGNATURE
EOF

# ── labuser: Docker Hub credentials ───────────────────────────────────────────
# auth = base64("labuser:DockerPassword123!")
RUN mkdir -p /home/labuser/.docker && cat > /home/labuser/.docker/config.json << 'EOF'
{
  "auths": {
    "https://index.docker.io/v1/": {
      "auth": "bGFidXNlcjpEb2NrZXJQYXNzd29yZDEyMyE="
    },
    "registry.example.com": {
      "auth": "bGFidXNlcjpSZWdpc3RyeVNlY3JldDQ1Ng=="
    }
  }
}
EOF

# ── labuser: git credentials ───────────────────────────────────────────────────
RUN cat > /home/labuser/.gitconfig << 'EOF'
[user]
    name  = Lab User
    email = labuser@example.com
[credential]
    helper = store
EOF

RUN cat > /home/labuser/.git-credentials << 'EOF'
https://labuser:ghp_FakeGitHubPATtokenExampleABCDEF1234@github.com
https://labuser:glpat-FakeGitLabTokenExample12345@gitlab.example.com
EOF

# ── labuser: database credential files ────────────────────────────────────────
RUN cat > /home/labuser/.pgpass << 'EOF'
localhost:5432:production_db:labuser:PgProductionPass123!
db.example.com:5432:*:labuser:PgRemotePass456!
EOF
RUN chmod 600 /home/labuser/.pgpass

RUN cat > /home/labuser/.netrc << 'EOF'
machine ftp.example.com login labuser password FtpPassword789!
machine api.example.com login labuser password ApiNetrcSecret321
EOF
RUN chmod 600 /home/labuser/.netrc

RUN cat > /home/labuser/.my.cnf << 'EOF'
[client]
user     = labuser
password = MySQLLabPass123!
host     = localhost
EOF
RUN chmod 600 /home/labuser/.my.cnf

# ── labuser: shell history with secrets in commands ────────────────────────────
RUN cat > /home/labuser/.bash_history << 'EOF'
ls -la
mysql -u root -pMySQLRootPass123! production_db
git pull origin main
scp deploy@192.168.1.50:/backup/data.tar.gz .
curl -u admin:AdminPassword456! https://api.internal.example.com/v1/users
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
psql postgresql://labuser:PgProductionPass123!@localhost:5432/production_db
docker login -u labuser -p DockerPassword123! registry.example.com
ssh -i ~/.ssh/id_rsa deploy@10.0.1.20
kubectl --token=eyJhbGciOiJSUzI1NiJ9.FakeToken config set-cluster prod
EOF

# ── labuser: application .env files ───────────────────────────────────────────
RUN mkdir -p /home/labuser/app && cat > /home/labuser/app/.env << 'EOF'
DATABASE_URL=postgresql://labuser:PgProductionPass123!@localhost:5432/production_db
REDIS_URL=redis://:CachedPass789@localhost:6379/0
SECRET_KEY=django-insecure-fake-secret-key-for-lab-abcdef1234567890
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
STRIPE_SECRET_KEY=sk_live_FakeStripeKeyForLabTesting1234
SENDGRID_API_KEY=SG.FakeSendGridKeyExample.abcdefghijklmnopqrstuvwxyz123456
JWT_SECRET=supersecret-jwt-signing-key-do-not-expose
EOF

RUN mkdir -p /home/labuser/infra && cat > /home/labuser/infra/terraform.tfvars << 'EOF'
db_password      = "TerraformDbPass999!"
admin_api_key    = "tf-api-key-abcdef1234567890"
ssh_private_key  = "~/.ssh/id_rsa"
EOF

# ── labuser: fake Kerberos ccache (for file discovery testing) ─────────────────
# magic bytes 0x05 0x04 = MIT ccache version 4
RUN printf '\x05\x04\x00\x0c\x00\x01\x00\x08labuser\x00' > /tmp/krb5cc_1000 && \
    ln -s /tmp/krb5cc_1000 /home/labuser/.cache/krb5cc_labuser 2>/dev/null || true

# ── deploy: SSH key + AWS + service .env ──────────────────────────────────────
RUN mkdir -p /home/deploy/.ssh && chmod 700 /home/deploy/.ssh && \
    ssh-keygen -t ed25519 -f /home/deploy/.ssh/id_ed25519 -N "" -C "deploy@ci-runner" && \
    chmod 600 /home/deploy/.ssh/id_ed25519 && \
    chown -R deploy:deploy /home/deploy/.ssh

RUN mkdir -p /home/deploy/.aws && cat > /home/deploy/.aws/credentials << 'EOF'
[deploy]
aws_access_key_id = AKIAIOSFODNN7DEPLOY
aws_secret_access_key = DeploySecretKeyFakeExample/ABCDEFGHIJK
region = eu-central-1
EOF

RUN mkdir -p /home/deploy/service && cat > /home/deploy/service/.env << 'EOF'
DATABASE_URL=postgresql://deploy:DeployDbPass789!@db.internal:5432/app_db
INTERNAL_API_KEY=int-api-deploy-FakeKey-ABCDEF123456
WEBHOOK_SECRET=wh-secret-FakeWebhookSigningKey9876
EOF

RUN cat > /home/deploy/.bash_history << 'EOF'
cd service && python3 app.py
aws s3 cp s3://prod-backups/dump.sql . --profile deploy
psql postgresql://deploy:DeployDbPass789!@db.internal:5432/app_db
curl -H "X-API-Key: int-api-deploy-FakeKey-ABCDEF123456" https://internal.example.com/api/status
EOF

# ── Fix ownership ──────────────────────────────────────────────────────────────
RUN chown -R labuser:labuser /home/labuser && \
    chown -R deploy:deploy   /home/deploy

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22

HEALTHCHECK --interval=30s --timeout=3s --start-period=20s --retries=3 \
  CMD bash -c '</dev/tcp/127.0.0.1/22' || exit 1
ENTRYPOINT ["/entrypoint.sh"]
