# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c) 2026 CommonHuman-Lab
import subprocess
import requests
from flask import request, session, jsonify
from db import get_db


def _require_admin_json():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'not authenticated'}), 401
    user = get_db().execute("SELECT is_admin FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user or not user['is_admin']:
        return jsonify({'error': 'admin only'}), 403
    return None


def init(app):
    # SSRF: no host/scheme allow-list on `url` at all — the server fetches
    # whatever it's given and relays a snippet of the response back, which
    # is what makes this observable rather than a blind SSRF.
    @app.route('/api/admin/import-cover', methods=['POST'])
    def api_admin_import_cover():
        err = _require_admin_json()
        if err:
            return err
        body = request.get_json(silent=True) or {}
        artist_id = body.get('artist_id')
        url = (body.get('url') or '').strip()
        if not artist_id or not url:
            return jsonify({'error': 'artist_id and url required'}), 400
        try:
            resp = requests.get(url, timeout=3)
            snippet = resp.text[:2048]
        except Exception as e:
            return jsonify({'error': str(e)}), 502
        db = get_db()
        db.execute("UPDATE artists SET cover_url = ? WHERE id = ?",
                   ('/static/img/cover-imported.png', artist_id))
        db.commit()
        return jsonify({'ok': True, 'cover_url': '/static/img/cover-imported.png',
                         'fetched_preview': snippet})

    # Reachable only from the container's own loopback — an outside request
    # gets 403'd before anything else runs. `format` is interpolated
    # unquoted into a shell string, so `;`-chained commands execute.
    @app.route('/api/internal/transcode')
    def api_internal_transcode():
        if request.remote_addr != '127.0.0.1':
            return jsonify({'error': 'internal only'}), 403
        fmt = request.args.get('format', 'mp3').strip()
        try:
            output = subprocess.check_output(
                f"echo transcoding as {fmt}",
                shell=True, stderr=subprocess.STDOUT, timeout=8,
            ).decode(errors='replace')
        except subprocess.CalledProcessError as e:
            output = e.output.decode(errors='replace')
        return jsonify({
            'ok': True,
            'flag': 'FLAG{wf_ssrf_internal_transcode_reached}',
            'log': output,
        })
