# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import subprocess
import requests as _requests
from flask import request, session, jsonify
from db import get_db


def _require_login_json():
    if not session.get('user_id'):
        return jsonify({'error': 'login required'}), 401
    return None


def init(app):

    # VULN: IDOR — same missing ownership check as /vaults/<id>, exposed over
    # the API. Lets a scripted sweep enumerate every vault's items.
    @app.route('/api/v1/vaults/<int:vault_id>/items')
    def api_vault_items(vault_id):
        err = _require_login_json()
        if err:
            return err
        rows = get_db().execute(
            "SELECT * FROM vault_items WHERE vault_id = ? ORDER BY id", (vault_id,)
        ).fetchall()
        return jsonify({'vault_id': vault_id, 'items': [dict(r) for r in rows]})

    # VULN: SSRF — "breach check" fetches an operator-supplied URL server-side
    # and reflects the response back. Gated behind is_admin, which is exactly
    # why the mass-assignment escalation matters for the insane chain: this
    # endpoint is otherwise unreachable to a freshly registered account.
    @app.route('/api/breach-check', methods=['POST'])
    def api_breach_check():
        err = _require_login_json()
        if err:
            return err
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        if not (user['is_admin'] or user['role'] == 'admin'):
            return jsonify({'error': 'admin only'}), 403
        url = (request.get_json(silent=True) or request.form).get('url', '').strip()
        if not url:
            return jsonify({'error': 'url required'}), 400
        try:
            resp = _requests.get(url, timeout=5, allow_redirects=True)
            return jsonify({'status': resp.status_code, 'body': resp.text[:4096]})
        except Exception as e:
            return jsonify({'error': str(e)}), 502

    # VULN: command injection — only reachable from the container's own
    # loopback address (i.e. via the SSRF above), so it was never hardened
    # against malicious input. The `format` param is interpolated unsanitised
    # into a shell call that builds the export bundle.
    @app.route('/api/internal/vault-export')
    def api_internal_vault_export():
        if request.remote_addr != '127.0.0.1':
            return jsonify({'error': 'internal only'}), 403
        fmt = request.args.get('format', 'json').strip()
        try:
            output = subprocess.check_output(
                f"echo building vault export bundle as {fmt}",
                shell=True,
                stderr=subprocess.STDOUT,
                timeout=8,
            ).decode(errors='replace')
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return jsonify({'export': output, 'vault_token': 'FLAG{vs_ssrf_internal_vault_export}'})
