#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
"""
Interactive scaffold for new OctoRig world labs.

Usage:
    ./octorig.sh new-lab
    python3 labs/scaffold_lab.py          # direct invocation
"""

import os
import re
import sys
import textwrap

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABS_DIR = os.path.join(REPO_ROOT, "labs")
REGISTRY_DIR = os.path.join(REPO_ROOT, "platform", "backend", "app", "labs", "registry", "world")
OCTORIG_SH = os.path.join(REPO_ROOT, "octorig.sh")


# ── helpers ──────────────────────────────────────────────────────────────────


def _read_existing_ids() -> set[int]:
    ids: set[int] = set()
    with open(OCTORIG_SH) as f:
        for line in f:
            m = re.match(r'\s*"(\d+)\|', line)
            if m:
                ids.add(int(m.group(1)))
    return ids


def _read_existing_slugs() -> set[str]:
    slugs: set[str] = set()
    with open(OCTORIG_SH) as f:
        for line in f:
            m = re.match(r'\s*"\d+\|(\S+)\|', line)
            if m:
                slugs.add(m.group(1).lower())
    return slugs


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        val = input(f"  {prompt}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        sys.exit(0)
    return val or default


def _confirm(prompt: str) -> bool:
    try:
        return input(f"  {prompt} [y/N]: ").strip().lower() == "y"
    except (EOFError, KeyboardInterrupt):
        return False


def _slug_ok(slug: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9-]{2,30}$", slug))


def _write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"    created  {os.path.relpath(path, REPO_ROOT)}")


# ── file generators ───────────────────────────────────────────────────────────


def _gen_lab_sh(slug: str, name: str, lab_id: int, subnet: str, ip: str, ssh_user: str, ssh_pass: str) -> str:
    return textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        # =============================================================================
        # Lab: {name}
        # Built from source in labs/{slug}/
        # =============================================================================

        LAB_NAME="{name}"
        CONTAINER_NAME="octorig-{slug}"
        LAB_NET="octorig-{slug}-net"
        LAB_SUBNET="{subnet}"
        LAB_IP="{ip}"

        SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"
        APP_DIR="${{SCRIPT_DIR}}/{slug}"

        source "${{SCRIPT_DIR}}/_common.sh"
        require_action "${{1:-}}"

        case "$1" in
          start)
            header "Starting..."
            ensure_container_gone "$CONTAINER_NAME"

            info "Building {name} image (this may take ~60s for apt packages)..."
            if docker build -q -t octorig-{slug}:latest "$APP_DIR" >/dev/null; then
              good "Image built"
            else
              bad "Image build failed — check labs/{slug}/"
              exit 1
            fi

            ensure_network "$LAB_NET" "$LAB_SUBNET"
            docker run -d \\
              --name "$CONTAINER_NAME" \\
              --network "$LAB_NET" \\
              --ip "$LAB_IP" \\
              --restart unless-stopped \\
              octorig-{slug}:latest

            wait_for_port "$LAB_IP" 80 60

            INFO_LINES=(
              "URL|http://${{LAB_IP}}"
              "SSH|ssh {ssh_user}@${{LAB_IP}}"
              "FTP|ftp ${{LAB_IP}}"
              "Stop|./{slug}.sh stop"
            )
            access_card INFO_LINES
            good "{name} is up!"
            ;;

          stop)
            header "Stopping..."
            if docker rm -f "$CONTAINER_NAME" &>/dev/null; then
              good "Container $CONTAINER_NAME removed."
            else
              warn "Container $CONTAINER_NAME was not running."
            fi
            remove_network "$LAB_NET"
            ;;

          status)
            container_status "$CONTAINER_NAME"
            ;;
        esac
        """)


def _gen_dockerfile(slug: str, name: str, ssh_user: str, ssh_pass: str, ip: str) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        FROM python:3.11-slim
        WORKDIR /app

        RUN apt-get update && apt-get install -y --no-install-recommends \\
            openssh-server vsftpd supervisor iputils-ping \\
            && rm -rf /var/lib/apt/lists/*

        RUN pip install --no-cache-dir flask==3.0.3

        # SSH — weak credentials (ops console)
        RUN mkdir -p /run/sshd && \\
            sed -i \\
              -e 's/#PermitRootLogin.*/PermitRootLogin no/' \\
              -e 's/#PasswordAuthentication.*/PasswordAuthentication yes/' \\
              /etc/ssh/sshd_config && \\
            useradd -m -s /bin/bash {ssh_user} && echo "{ssh_user}:{ssh_pass}" | chpasswd

        # Seed SSH home — harvestable operational secrets
        RUN mkdir -p /home/{ssh_user}/ops && \\
            printf "machine db.{slug}.internal login {ssh_user} password P@ssw0rd!\\n" \\
              > /home/{ssh_user}/.netrc && \\
            printf "APP_SECRET=changeme\\nDB_PATH=/data/{slug}.db\\n" \\
              > /home/{ssh_user}/ops/.env && \\
            chmod 600 /home/{ssh_user}/.netrc && \\
            chown -R {ssh_user}:{ssh_user} /home/{ssh_user}

        # FTP — anonymous read-only (backup drop)
        RUN mkdir -p /srv/ftp/pub && \\
            chown root:root /srv/ftp && chmod 755 /srv/ftp && \\
            chown ftp:ftp /srv/ftp/pub && chmod 755 /srv/ftp/pub

        COPY vsftpd.conf /etc/vsftpd.conf
        COPY supervisord.conf /etc/supervisor/conf.d/{slug}.conf
        COPY . .
        RUN mkdir -p /data && \\
            printf "{name} Backup Manifest\\n=================\\nSSH: {ssh_user}/{ssh_pass}\\nFLAG{{{slug}_recon_ftp_backup_leak}}\\n" \\
              > /srv/ftp/pub/{slug}_backup.txt && \\
            chown ftp:ftp /srv/ftp/pub/{slug}_backup.txt && \\
            chmod 644 /srv/ftp/pub/{slug}_backup.txt

        EXPOSE 80 21 22 30000-30009
        CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
        """)


def _gen_vsftpd_conf() -> str:
    return textwrap.dedent("""\
        anonymous_enable=YES
        local_enable=NO
        write_enable=NO
        anon_root=/srv/ftp
        anon_upload_enable=NO
        anon_mkdir_write_enable=NO
        dirmessage_enable=YES
        xferlog_enable=NO
        connect_from_port_20=YES
        listen=YES
        listen_ipv6=NO
        pam_service_name=vsftpd
        pasv_enable=YES
        pasv_min_port=30000
        pasv_max_port=30009
        """)


def _gen_supervisord_conf(slug: str) -> str:
    return textwrap.dedent(f"""\
        ; SPDX-License-Identifier: AGPL-3.0-or-later
        ; Copyright (c) 2026 CommonHuman-Lab
        [supervisord]
        nodaemon=true
        logfile=/dev/null
        logfile_maxbytes=0

        [program:flask]
        command=python /app/app.py
        autostart=true
        autorestart=true
        stdout_logfile=/dev/null
        stderr_logfile=/dev/null

        [program:sshd]
        command=/usr/sbin/sshd -D -e
        autostart=true
        autorestart=true
        stdout_logfile=/dev/null
        stderr_logfile=/dev/null

        [program:vsftpd]
        command=/usr/sbin/vsftpd /etc/vsftpd.conf
        autostart=true
        autorestart=true
        stdout_logfile=/dev/null
        stderr_logfile=/dev/null
        """)


def _gen_app_py(slug: str, name: str) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        import os
        import secrets
        from flask import Flask, render_template, session

        from db import init_db, get_db
        from routes import auth, main

        app = Flask(__name__)
        app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)

        with app.app_context():
            init_db()

        if __name__ == "__main__":
            app.run(host="0.0.0.0", port=80, debug=False)
        """)


def _gen_db_py(slug: str) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        import sqlite3
        import os

        DB_PATH = os.environ.get("DB_PATH", "/data/{slug}.db")


        def get_db() -> sqlite3.Connection:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            return conn


        def init_db() -> None:
            conn = get_db()
            conn.executescript(\"\"\"
                CREATE TABLE IF NOT EXISTS users (
                    id      INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    is_admin INTEGER NOT NULL DEFAULT 0,
                    bio      TEXT DEFAULT ''
                );

                CREATE TABLE IF NOT EXISTS _flags (
                    id    INTEGER PRIMARY KEY,
                    name  TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL
                );
            \"\"\")

            # Seed admin user (password is vuln to SQLi login bypass)
            conn.execute(
                "INSERT OR IGNORE INTO users (username, password, is_admin) VALUES (?, ?, ?)",
                ("admin", "SuperSecret2026!", 1),
            )
            # Seed flag placeholder — replace value before shipping
            conn.execute(
                "INSERT OR IGNORE INTO _flags (name, value) VALUES (?, ?)",
                ("sqli-search", "FLAG{{{slug}_sqli_search_union}}"),
            )
            conn.commit()
            conn.close()
        """)


def _gen_routes_init() -> str:
    return "# SPDX-License-Identifier: AGPL-3.0-or-later\n# Copyright (c) 2026 CommonHuman-Lab\n"


def _gen_routes_auth(slug: str) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        from flask import Blueprint, render_template, request, session, redirect, url_for
        from db import get_db

        bp = Blueprint("auth", __name__)


        @bp.route("/login", methods=["GET", "POST"])
        def login():
            error = None
            if request.method == "POST":
                username = request.form.get("username", "")
                password = request.form.get("password", "")
                db = get_db()
                # VULN: SQLi login bypass — username is interpolated unsanitised
                row = db.execute(
                    f"SELECT * FROM users WHERE username = '{{username}}' AND password = '{{password}}'"
                ).fetchone()
                if row:
                    session["user_id"] = row["id"]
                    session["username"] = row["username"]
                    session["is_admin"] = bool(row["is_admin"])
                    return redirect(url_for("main.index"))
                error = "Invalid credentials"
            return render_template("login.html", error=error)


        @bp.route("/register", methods=["GET", "POST"])
        def register():
            error = None
            if request.method == "POST":
                username = request.form.get("username", "").strip()
                password = request.form.get("password", "").strip()
                if not username or not password:
                    error = "Username and password required"
                else:
                    db = get_db()
                    try:
                        db.execute(
                            "INSERT INTO users (username, password) VALUES (?, ?)",
                            (username, password),
                        )
                        db.commit()
                        return redirect(url_for("auth.login"))
                    except Exception:
                        error = "Username already taken"
            return render_template("register.html", error=error)


        @bp.route("/logout")
        def logout():
            session.clear()
            return redirect(url_for("auth.login"))
        """)


def _gen_routes_main(slug: str) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        from flask import Blueprint, render_template, session, redirect, url_for

        bp = Blueprint("main", __name__)


        def _require_login():
            if not session.get("user_id"):
                return redirect(url_for("auth.login"))
            return None


        @bp.route("/")
        def index():
            redir = _require_login()
            if redir:
                return redir
            return render_template("index.html", username=session.get("username"))
        """)


def _gen_base_html(name: str) -> str:
    return textwrap.dedent(f"""\
        <!DOCTYPE html>
        <!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
        <!-- Copyright (c) 2026 CommonHuman-Lab -->
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{name}</title>
          <style>
            body {{ font-family: system-ui, sans-serif; background: #0d0d0d; color: #e0e0e0; margin: 0; }}
            nav  {{ background: #111; padding: 0.75rem 1.5rem; border-bottom: 1px solid #222; display: flex; gap: 1rem; align-items: center; }}
            nav a {{ color: #ccc; text-decoration: none; font-size: 0.9rem; }}
            nav a:hover {{ color: #fff; }}
            .brand {{ font-weight: 700; color: #fff; margin-right: auto; }}
            main {{ max-width: 900px; margin: 2rem auto; padding: 0 1.5rem; }}
            .card {{ background: #161616; border: 1px solid #2a2a2a; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; }}
            input, button {{ padding: 0.5rem 0.75rem; border-radius: 4px; border: 1px solid #333; }}
            input {{ background: #111; color: #fff; width: 100%; box-sizing: border-box; margin-bottom: 0.5rem; }}
            button {{ background: #1a6cf5; color: #fff; border: none; cursor: pointer; }}
            .error {{ color: #f55; font-size: 0.875rem; margin-top: 0.25rem; }}
          </style>
        </head>
        <body>
          <nav>
            <span class="brand">{name}</span>
            <a href="/">Home</a>
            <a href="/logout">Logout</a>
          </nav>
          <main>
            {{% block content %}}{{% endblock %}}
          </main>
        </body>
        </html>
        """)


def _gen_index_html(name: str) -> str:
    return textwrap.dedent(f"""\
        <!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
        <!-- Copyright (c) 2026 CommonHuman-Lab -->
        {{% extends "base.html" %}}
        {{% block content %}}
        <div class="card">
          <h2>Welcome to {name}</h2>
          <p>Hello, {{{{ username }}}}!</p>
          <p style="color:#888;font-size:0.875rem;">TODO: add application features and vulnerabilities here.</p>
        </div>
        {{% endblock %}}
        """)


def _gen_login_html(name: str) -> str:
    return textwrap.dedent(f"""\
        <!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
        <!-- Copyright (c) 2026 CommonHuman-Lab -->
        {{% extends "base.html" %}}
        {{% block content %}}
        <div class="card" style="max-width:400px;margin:4rem auto;">
          <h2>Login</h2>
          <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" style="width:100%">Login</button>
          </form>
          {{% if error %}}<p class="error">{{{{ error }}}}</p>{{% endif %}}
          <p style="font-size:0.8rem;margin-top:1rem;color:#888;">No account? <a href="/register" style="color:#aaa;">Register</a></p>
        </div>
        {{% endblock %}}
        """)


def _gen_register_html() -> str:
    return textwrap.dedent("""\
        <!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
        <!-- Copyright (c) 2026 CommonHuman-Lab -->
        {% extends "base.html" %}
        {% block content %}
        <div class="card" style="max-width:400px;margin:4rem auto;">
          <h2>Register</h2>
          <form method="post">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" style="width:100%">Create account</button>
          </form>
          {% if error %}<p class="error">{{ error }}</p>{% endif %}
        </div>
        {% endblock %}
        """)


def _gen_registry_entry(
    slug: str, name: str, description: str, lab_id: int, subnet: str, ip: str,
    ssh_user: str, ssh_pass: str,
) -> str:
    return textwrap.dedent(f"""\
        # SPDX-License-Identifier: AGPL-3.0-or-later
        # Copyright (c) 2026 CommonHuman-Lab
        from app.labs.registry._types import ChallengeDef, LabDefinition

        LAB: LabDefinition = {{
            "id": {lab_id},
            "slug": "{slug}",
            "name": "{name}",
            "description": "{description}",
            "category": "world",
            "container_names": ["octorig-{slug}"],
            "images": {{"app": "octorig-{slug}:latest"}},
            "build_contexts": {{"app": "labs/{slug}"}},
            "start_order": ["app"],
            "exposed_ports": {{"http": 80, "ssh": 22, "ftp": 21}},
            "access_info": [
                {{"key": "URL", "value": "http://{{container_ip}}"}},
                {{"key": "SSH", "value": "ssh {ssh_user}@{{container_ip}}"}},
                {{"key": "FTP", "value": "ftp {{container_ip}}"}},
            ],
            "volume_names": [],
            "env_vars": {{}},
            "requires_privileged": False,
            "challenges": [
                # TODO: add ChallengeDef entries here
                # Example structure:
                # {{
                #     "slug": "{slug}-recon-ftp-backup",
                #     "title": "Open Season",
                #     "description": "FTP allows anonymous login — what's in the public drop?",
                #     "challenge_type": "flag",
                #     "difficulty": "easy",
                #     "category": "recon",
                #     "tags": ["ftp", "recon"],
                #     "skills": ["FTP enumeration", "anonymous access"],
                #     "points": 50,
                #     "flags": [
                #         {{
                #             "value": "FLAG{{{slug}_recon_ftp_backup_leak}}",
                #             "flag_type": "static",
                #             "case_sensitive": False,
                #         }}
                #     ],
                # }},
            ],
        }}
        """)


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print("\n  OctoRig — new world lab scaffold")
    print("  ─────────────────────────────────")

    existing_ids = _read_existing_ids()
    existing_slugs = _read_existing_slugs()
    next_id = max(existing_ids, default=20) + 1

    # Collect inputs
    while True:
        slug = _ask("Lab slug (lowercase, hyphens ok)", "").lower()
        if not _slug_ok(slug):
            print("    ! Slug must be 3–31 chars, start with a letter, only a-z 0-9 and hyphens.")
            continue
        if slug in existing_slugs:
            print(f"    ! Slug '{slug}' already exists in octorig.sh — pick another.")
            continue
        break

    name = _ask("Display name", slug.replace("-", " ").title())
    description = _ask("One-line description (for registry)")
    lab_id = int(_ask("Lab ID", str(next_id)))
    if lab_id in existing_ids:
        print(f"\n  WARNING: ID {lab_id} is already used. You must pick a unique ID.")
        lab_id = int(_ask("Lab ID (unique)", str(next_id)))

    # Derived values
    subnet = f"172.28.{lab_id}.0/24"
    ip = f"172.28.{lab_id}.2"
    ssh_user = slug.replace("-", "") + "ops"
    ssh_pass_default = slug.replace("-", "") + "2026"
    ssh_user = _ask("SSH username", ssh_user)
    ssh_pass = _ask("SSH password (weak, intentional)", ssh_pass_default)

    print(f"\n  Will generate lab ID={lab_id}, subnet={subnet}, IP={ip}")
    if not _confirm("Proceed?"):
        print("  Aborted.")
        sys.exit(0)

    print()

    lab_dir = os.path.join(LABS_DIR, slug)
    if os.path.exists(lab_dir):
        print(f"  ERROR: {lab_dir} already exists. Remove it first.")
        sys.exit(1)

    # Generate lab shell script
    _write(
        os.path.join(LABS_DIR, f"{slug}.sh"),
        _gen_lab_sh(slug, name, lab_id, subnet, ip, ssh_user, ssh_pass),
    )
    os.chmod(os.path.join(LABS_DIR, f"{slug}.sh"), 0o755)

    # Generate lab directory files
    _write(os.path.join(lab_dir, "Dockerfile"), _gen_dockerfile(slug, name, ssh_user, ssh_pass, ip))
    _write(os.path.join(lab_dir, "vsftpd.conf"), _gen_vsftpd_conf())
    _write(os.path.join(lab_dir, "supervisord.conf"), _gen_supervisord_conf(slug))
    _write(os.path.join(lab_dir, "app.py"), _gen_app_py(slug, name))
    _write(os.path.join(lab_dir, "db.py"), _gen_db_py(slug))
    _write(os.path.join(lab_dir, "routes", "__init__.py"), _gen_routes_init())
    _write(os.path.join(lab_dir, "routes", "auth.py"), _gen_routes_auth(slug))
    _write(os.path.join(lab_dir, "routes", "main.py"), _gen_routes_main(slug))
    _write(os.path.join(lab_dir, "templates", "base.html"), _gen_base_html(name))
    _write(os.path.join(lab_dir, "templates", "index.html"), _gen_index_html(name))
    _write(os.path.join(lab_dir, "templates", "login.html"), _gen_login_html(name))
    _write(os.path.join(lab_dir, "templates", "register.html"), _gen_register_html())

    # Generate platform registry entry
    _write(
        os.path.join(REGISTRY_DIR, f"{slug}.py"),
        _gen_registry_entry(slug, name, description, lab_id, subnet, ip, ssh_user, ssh_pass),
    )

    print(f"""
  ✓ Scaffold complete!

  Next steps:
  ───────────
  1. Add this line to octorig.sh LABS array (before the closing parenthesis):
       "{lab_id}|{slug}|{slug}.sh|{description}"

  2. Add {lab_id} to WORLD_LAB_IDS in octorig.sh:
       WORLD_LAB_IDS=( ... {lab_id} )

  3. Add the registry entry to platform/backend/app/labs/registry/world/__init__.py:
       from .{slug} import LAB as {slug.upper().replace("-", "_")}_LAB
       ...add {slug.upper().replace("-", "_")}_LAB to LAB_REGISTRY list

  4. Design your vulnerabilities in labs/{slug}/ and fill in challenges[] in:
       platform/backend/app/labs/registry/world/{slug}.py

  5. Test:
       ./octorig.sh start {lab_id}
       curl http://{ip}/
    """)


if __name__ == "__main__":
    main()
